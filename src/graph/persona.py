from langchain_groq.chat_models import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from tavily  import TavilyClient
from langchain_core.tools import tool
from dotenv import load_dotenv
import os
from .schemas import WorkerState, ReflectorResponse
from src.utils import load_prompt
from src.utils import get_logger

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
logger = get_logger()

@tool(description="A web-search tool")
def web_search(query: str):
    """Search for up-to-date information on the Internet
    
    Args:
        query (str): a query for a web-search to be executed   
    """

    _tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
    logger.info("Web-search tool is being executed")
    return _tavily_client.search(query=query, search_depth="basic", max_results=3)


tools = [web_search]


class Worker:
    def __init__(self, model_name):
        self.llm = ChatGroq(model=model_name, api_key=GROQ_API_KEY)
        self.graph = self._build_persona_graph()

    def _persona_call(self, state:WorkerState):
        name = state["name"]
        prompt = load_prompt(name)
        question = state["question"]    
        messages = state["messages"]
        corrections = state["corrections"]
        instructions = state["instructions"]
        chain = prompt | self.llm.bind_tools(tools)
        logger.info(f"Persona {name} is being executed")
        response = chain.invoke({
            "question": question,
            "messages": messages,
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
        messages = state["messages"]
        instructions = state["instructions"]
        last_message = messages[-1]
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
        hallucinations = response.hallucination_flags
        corrections.extend(hallucinations)

        return{ 
            "counter": counter + 1,
            "score": score,
            "corrections": corrections,
        }

    def _should_end(self, state:WorkerState):
        counter = state["counter"]
        score = state["score"]
        if score > 8 or counter > 3:
            return "END"
        return "persona_call"


    def _build_persona_graph(self):
        graph = StateGraph(WorkerState)

        graph.add_node("persona_call", self._persona_call)
        graph.add_node("tools", ToolNode(tools))
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