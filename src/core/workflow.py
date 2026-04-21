from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain_core.messages import ToolMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from src.utils import load_prompt
from dotenv import load_dotenv
from .schemas import ChatState, DecisionDraft
from src.utils import get_logger
from .tools import tools_list
import streamlit as st
import os

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL")
logger = get_logger()


class Persona:
    def __init__(self, db):
        self.llm = ChatGoogleGenerativeAI(
            model=LLM_MODEL, api_key=GEMINI_API_KEY
        )
        self.db = db
        self.graph = self._build_chat_graph()


    async def _persona_call(self, state: ChatState):
        prompt = load_prompt("Persona")
        query = state["query"]
        draft = state["draft"]
        draft_clarifications = state["clarifications"]
        messages = state["messages"]
        memories = state["memories"]
        llm_with_tools = self.llm.bind_tools(tools_list)
        logger.info("Persona is being called")

        if messages and isinstance(messages[-1], ToolMessage):
            prompt_messages = prompt.invoke(
                {
                    "query": query,
                    "draft": draft.model_dump_json(indent=2),
                    "draft_clarifications": draft_clarifications,
                    "messages": "",
                    "memories": memories
                }
            ).to_messages()

            tool_exchange = []
            for msg in reversed(messages):
                tool_exchange.insert(0, msg)
                if isinstance(msg, AIMessage) and getattr(msg, "tool_calls", None):
                    break

            response = await llm_with_tools.ainvoke(prompt_messages + tool_exchange)
        else:
            last_message = messages[-1] if messages else ""
            chain = prompt | llm_with_tools
            response = await chain.ainvoke(
                {
                    "query": query,
                    "draft": draft.model_dump_json(indent=2),
                    "draft_clarifications": draft_clarifications,
                    "messages": last_message,
                    "memories": memories
                }
            )

        logger.info("Persona generated a response")
        logger.info(f"PERSONA RESPONSE:\n{response.content}")
        return {"messages": [response]}

    def _upadte_final_response(state:ChatState):
        messages = state["messages"]
        return {"final_response": messages[-1]}
    def _should_use_tools(self, state: ChatState):
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools"
        return "end"

    def _build_chat_graph(self):
        graph = StateGraph(ChatState)
        graph.add_node("persona_call", self._persona_call)
        graph.add_node("tools", ToolNode(tools_list))
        graph.add_conditional_edges(
            source="persona_call",
            path=self._should_use_tools,
            path_map={"tools": "tools", "end": END},
        )
        graph.add_edge("tools", "persona_call")
        graph.set_entry_point("persona_call")
        app = graph.compile()
        return app

    async def run_chat(self, initial_state: dict):
        response = await self.graph.ainvoke(input=initial_state)
        message_to_display = response["messages"][-1].content
        return message_to_display


class Drafter:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite", api_key=GEMINI_API_KEY
        )

    async def generate_draft(self, query: str):
        prompt = load_prompt(name="drafter")
        chain = prompt | self.llm.with_structured_output(DecisionDraft)
        try:
            response = await chain.ainvoke({"query": query})
            return response
        except Exception as e:
            st.error(f"Unable to invoke Drafter: {e}")
            return None
   