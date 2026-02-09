from langchain_groq.chat_models import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_tavily import TavilySearch
from tavily  import TavilyClient
from langchain_core.tools import tool
from dotenv import load_dotenv
import os
from .schemas import WorkerState
from src.utils import load_prompt
from src.utils import get_logger

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
logger = get_logger()

@tool(description="A web-search tool")
def web_search(query: str):
    """A tool designed for information search on the Internet
    
    Args:
        query: a query for a web-search to be executed   
    """

    _tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
    return _tavily_client.search(query=query, search_depth="basic", max_results=3)


llm = ChatGroq(model="llama-3.3-70b-versatile", max_tokens=5096)
tools = [web_search]
llm_with_tools = llm.bind_tools(tools)
tool_node = ToolNode(tools)



def persona_call(state:WorkerState):
    name = state["name"]
    prompt = load_prompt(name)
    chain = prompt | llm_with_tools
    question = state["question"]    
    messages = state["messages"]
    corrections = state["corrections"]
    instructions = state["instructions"]
    response = chain.invoke({
        "question": question,
        "messages": messages,
        "instructions": instructions,   
        "corrections": corrections
    })
    return {"messages": [response]}

def should_use_tools(state:WorkerState):
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return "reflection_call"

def reflection_call(state:WorkerState):
    prompt = load_prompt(name="reflector")
    chain = prompt | llm
    question = state["question"]
    messages = state["messages"]
    instructions = state["instructions"]
    last_message = messages[-1]
    counter = state["counter"]
    response = chain.invoke({
        "question": question,
        "message": last_message,
        "instructions": instructions
    })
    return{ 
        "counter": counter + 1,
        "corrections": response.content,
    }

def should_end(state:WorkerState):
    counter = state["counter"]
    if counter < 3:
        return "persona_call"
    return "END"


def build_persona_graph():
    graph = StateGraph(WorkerState)

    graph.add_node("persona_call", persona_call)
    graph.add_node("tools", tool_node)
    graph.add_node("reflection_call", reflection_call)
    graph.add_edge(START, "persona_call")
    graph.add_conditional_edges(
        source="persona_call",
        path=should_use_tools,
        path_map={
            "tools": "tools",
            "reflection_call": "reflection_call"
        }
    )
    graph.add_edge("tools", "persona_call")
    graph.add_conditional_edges(
        source="reflection_call",
        path=should_end,
        path_map={
            "persona_call": "persona_call",
            "END": END
        }
    )
    app = graph.compile()
    return app

def run_persona(persona_graph, persona_initial_state:dict):
    response = persona_graph.invoke(persona_initial_state)
    messages = response["messages"]
    last_message = messages[-1]
    return last_message