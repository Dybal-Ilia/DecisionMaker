from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from tavily  import TavilyClient
from langchain_core.tools import tool
from dotenv import load_dotenv
import os
from .schemas import WorkerState, ReflectorResponse
from src.utils import load_prompt
from src.utils import get_logger
from .tools import tools_list

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
logger = get_logger()


class Worker:
    def __init__(self, model_name):
        self.llm = ChatGoogleGenerativeAI(model=model_name, api_key=GEMINI_API_KEY)
        self.graph = self._build_persona_graph()

    def _persona_call(self, state:WorkerState):
        name = state["name"]
        prompt = load_prompt(name)
        question = state["question"]    
        messages = state["messages"]
        last_message = messages[-1] if messages else ""
        corrections = state["corrections"]
        instructions = state["instructions"]
        chain = prompt | self.llm.bind_tools(tools_list)
        logger.info(f"Persona {name} is being executed")
        response = chain.invoke({
            "question": question,   
            "messages": last_message,
            "instructions": instructions,   
            "corrections": corrections
        })
        logger.info(f"Persona {name} generated a response")
        logger.info(f"PERSONA RESPONSE:\n{response.content}")
        return {"messages": [response]}

    def _should_use_tools(self, state:WorkerState):
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools"
        return "reflection_call"

    def _reflection_call(self, state:WorkerState):
        prompt = load_prompt(name="reflector")
        chain = prompt | self.llm.with_structured_output(ReflectorResponse, method="json_mode")
        question = state["question"]
        last_message = state["messages"][-1].content
        instructions = state["instructions"]
        counter = state["counter"]
        logger.info("Reflector is being called")
        response = chain.invoke({
            "question": question,
            "message": last_message,
            "instructions": instructions
        })
        logger.info("Reflector generated corrections")
        logger.info(f"REFLECTOR RESPONSE:\n{response}")

        score = response.score
        corrections = response.corrections

        return{ 
            "counter": counter + 1,
            "score": score,
            "corrections": corrections,
        }

    def _should_end(self, state:WorkerState):
        counter = state["counter"]
        score = state["score"]
        if score > 8 or counter > 4:
            return "END"
        return "persona_call"


    def _build_persona_graph(self):
        graph = StateGraph(WorkerState)

        graph.add_node("persona_call", self._persona_call)
        graph.add_node("tools", ToolNode(tools_list))
        graph.add_node("reflection_call", self._reflection_call)
        graph.add_edge(START, "persona_call")
        graph.add_conditional_edges(
            source="persona_call",
            path=self._should_use_tools,
            path_map={
                "tools": "tools",
                "reflection_call": "reflection_call"
            }
        )
        graph.add_edge("tools", "persona_call")
        graph.add_conditional_edges(
            source="reflection_call",
            path=self._should_end,
            path_map={
                "persona_call": "persona_call",
                "END": END
            }
        )
        app = graph.compile()
        return app

    def run_worker(self, persona_initial_state:dict):
        response = self.graph.invoke(persona_initial_state)
        messages = response["messages"]
        last_message = messages[-1]
        return last_message