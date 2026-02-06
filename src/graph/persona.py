from langchain_groq.chat_models import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_tavily import TavilySearch
from dotenv import load_dotenv
import os
from .schemas import WorkerState, ReflectionResponse
from src.utils import load_prompt
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


llm = ChatGroq(model="llama-3.3-70b-versatile")
tools = [TavilySearch(api_key=TAVILY_API_KEY)]
tool_node = ToolNode(tools)
def persona_call(state:WorkerState):
    name = state["name"]
    prompt = load_prompt(name)
    chain = prompt | llm.bind_tools(tools)
    question = state["question"]
    messages = state["messages"]
    corrections = state["corrections"]
    instructions = state["instructions"]
    last_correction = corrections[-1] if corrections else ""
    response = chain.invoke({
        "question": question,
        "messages": messages,
        "instructions": instructions,
        "corrections": last_correction
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
    chain = prompt | llm.with_structured_output(ReflectionResponse)
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
    counter += 1
    return{
        "score": response.score,
        "corrections": [response.correction],
        "counter": counter
    }

def should_end(state:WorkerState):
    counter = state["counter"]
    score = state["score"]
    if counter >= 3:
        return "END"
    if score >= 8.5:
        return "END"
    return "persona_call"


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
persona_graph = build_persona_graph()
def run_persona(persona_initial_state):
    response = persona_graph.invoke(persona_initial_state)
    messages = response["messages"]
    last_message = messages[-1]
    return last_message