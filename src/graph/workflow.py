from .persona import run_persona, build_persona_graph
from langchain_groq.chat_models import ChatGroq
from langgraph.graph import StateGraph, END, START
from src.utils import load_prompt
from dotenv import load_dotenv
from .schemas import ChatState
from langgraph.types import Send, Command
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GRQO_API_KEY")
llm = ChatGroq(model="llama-3.3-70b-versatile")
persona_graph = build_persona_graph()


def query_decomposition(state: ChatState) -> ChatState:
    question = state["question"]
    prompt = load_prompt(name="decomposer")
    chain = prompt | llm
    response = chain.invoke({
        "question": question
    })
    return{"instructions": response.content}

    
def compile_team(state:ChatState):
    team = state["team"]
    question = state["question"]
    instructions = state["instructions"]

    return Command(goto=[Send("persona_call",
                {
                    "question": question,
                    "name": persona,
                    "instructions": instructions,
                    "messages": [],
                    "corrections": [],
                    "counter": 0
                }) for persona in team])

def call_persona(state:ChatState):
    question = state["question"]
    name = state["name"]
    instructions = state["instructions"]
    messages = state["messages"]
    corrections = state["corrections"]
    counter = state["counter"]
    response = run_persona(persona_graph=persona_graph, persona_initial_state={
        "question": question,
        "name": name,
        "instructions": instructions,
        "messages": messages,
        "counter": counter,
        "corrections": corrections
    })
    return {"aggregated_messages": [response]}

def aggregate(state:ChatState):
    question = state["question"]
    messages = state["aggregated_messages"]
    prompt = load_prompt(name="aggregator")
    chain = prompt | llm
    response = chain.invoke({
        "question": question,
        "messages": messages
    })
    return {"final_response": response}



def build_chat_graph():
    graph = StateGraph(ChatState)
    graph.add_node("query_decomposition", query_decomposition)
    graph.add_node("compile_team", compile_team)
    graph.add_node("aggregator", aggregate)
    graph.add_node("persona_call", call_persona)
    graph.add_edge(START, "query_decomposition")
    graph.add_edge("query_decomposition", "compile_team")
    graph.add_edge("persona_call", "aggregator")
    graph.add_edge("aggregator", END)
    app = graph.compile()
    return app

