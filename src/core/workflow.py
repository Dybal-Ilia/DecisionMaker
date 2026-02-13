from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain_core.messages import ToolMessage, AIMessage
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
from src.utils import load_prompt
from dotenv import load_dotenv
from .schemas import ChatState, DecomposerResponse, ReflectorResponse
from src.utils import get_logger
from .tools import tools_list
import asyncio
import os

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
logger = get_logger()

class Chat:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", api_key=GEMINI_API_KEY)
        self.graph = self._build_chat_graph()

    async def _query_decomposition(self, state: ChatState) -> ChatState:
        question = state["question"]
        prompt = load_prompt(name="decomposer")
        chain = prompt | self.llm.with_structured_output(DecomposerResponse, method="json_mode")
        logger.info("Query Decomposer is being called")
        response = await chain.ainvoke({
            "question": question
        })
        logger.info("Query Decomposer generated a response")
        logger.info(response.model_dump_json(indent=2))
        return{"instructions":response.model_dump_json(indent=2)}        


    async def _persona_call(self, state:ChatState):
        domain = state["domain"]
        prompt = load_prompt(domain)
        question = state["question"]    
        messages = state["messages"]
        corrections = state["corrections"]
        instructions = state["instructions"]
        context = state["context"]
        llm_with_tools = self.llm.bind_tools(tools_list)
        logger.info(f"Persona {domain} is being executed")

        if messages and isinstance(messages[-1], ToolMessage):
            prompt_messages = prompt.invoke({
                "question": question,
                "messages": "",
                "instructions": instructions,
                "corrections": corrections,
                "context": context
            }).to_messages()

            tool_exchange = []
            for msg in reversed(messages):
                tool_exchange.insert(0, msg)
                if isinstance(msg, AIMessage) and getattr(msg, "tool_calls", None):
                    break
            for msg in tool_exchange:
                if isinstance(msg, ToolMessage) and len(msg.content) > 1000:
                    msg.content = msg.content[:1000] + "\n... [truncated]"

            response = await llm_with_tools.ainvoke(prompt_messages + tool_exchange)
        else:
            last_message = messages[-1] if messages else ""
            chain = prompt | llm_with_tools
            response = await chain.ainvoke({
                "question": question,
                "messages": last_message,
                "instructions": instructions,
                "corrections": corrections,
                "context": context
            })

        logger.info(f"Persona {domain} generated a response")
        logger.info(f"PERSONA RESPONSE:\n{response.content}")
        return {"messages": [response]}

    def _should_use_tools(self, state:ChatState):
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools"
        return "reflection_call"
    
    async def _reflection_call(self, state:ChatState):
        prompt = load_prompt(name="reflector")
        chain = prompt | self.llm.with_structured_output(ReflectorResponse, method="json_mode")
        question = state["question"]
        last_message = state["messages"][-1].content
        instructions = state["instructions"]
        #counter = state["counter"]
        logger.info("Reflector is being called")
        response = await chain.ainvoke({
            "question": question,
            "message": last_message,
            "instructions": instructions
        })
        logger.info("Reflector generated corrections")
        logger.info(f"REFLECTOR RESPONSE:\n{response.model_dump_json()}")

        score = response.score
        corrections = response.corrections

        return{ 
            #"counter": counter + 1,
            "score": score,
            "corrections": corrections,
        }
    
    def _should_end(self, state:ChatState):
        #counter = state["counter"]
        score = state["score"]
        if score > 7:
            return "END"
        return "persona_call"

    def _build_chat_graph(self):
        graph = StateGraph(ChatState)
        graph.add_node("query_decomposition", self._query_decomposition)
        graph.add_node("persona_call", self._persona_call)
        graph.add_node("tools", ToolNode(tools_list))
        graph.add_node("reflection_call", self._reflection_call)
        graph.set_entry_point("query_decomposition")
        graph.add_edge("query_decomposition", "persona_call")
        graph.add_conditional_edges(
            source="persona_call",
            path=self._should_use_tools,
            path_map={
                "tools":"tools",
                "reflection_call":"reflection_call"
            }
        )
        graph.add_edge("tools", "persona_call")
        graph.add_conditional_edges(
            source="reflection_call",
            path=self._should_end,
            path_map={
                "END":END,
                "persona_call": "persona_call"
            }
        )
        app = graph.compile()
        return app
    
    async def run_chat(self, initial_state:dict):
        response = await self.graph.ainvoke(input=initial_state)
        message_to_display = response["messages"][-1].content
        return message_to_display


