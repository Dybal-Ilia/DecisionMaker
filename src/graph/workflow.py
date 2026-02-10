from langchain_groq.chat_models import ChatGroq
from langgraph.graph import StateGraph, END, START
from src.utils import load_prompt
from dotenv import load_dotenv
from .schemas import ChatState
from langgraph.types import Send, Command
from src.graph.persona import Worker
from src.utils import get_logger
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GRQO_API_KEY")
logger = get_logger()

class Chat:
    def __init__(self, model_name):
        self.llm = ChatGroq(model=model_name, api_key=GROQ_API_KEY)
        self.worker = Worker(model_name="openai/gpt-oss-120b")
        self.graph = self._build_chat_graph()

    def _query_decomposition(self, state: ChatState) -> ChatState:
        question = state["question"]
        prompt = load_prompt(name="decomposer")
        chain = prompt | self.llm
        logger.info("Query Decomposer is being called")
        response = chain.invoke({
            "question": question
        })
        logger.info("Query Decomposer generated a response")
        return{"instructions": response.content}

    
    def _compile_team(self, state:ChatState):
        team = state["team"]
        question = state["question"]
        instructions = state["instructions"]
        logger.info(f"Compiling team - {team}")
        return Command(goto=[Send("persona_call",
                    {
                        "question": question,
                        "name": persona,
                        "instructions": instructions,
                        "messages": [],
                        "corrections": [],
                        "counter": 0
                    }) for persona in team])

    def _call_persona(self, state:ChatState):
        question = state["question"]
        name = state["name"]
        instructions = state["instructions"]
        messages = state["messages"]
        corrections = state["corrections"]
        counter = state["counter"]
        response = self.worker.run_worker(persona_initial_state={
            "question": question,
            "name": name,
            "instructions": instructions,
            "messages": messages,
            "counter": counter,
            "corrections": corrections
        })
        return {"aggregated_messages": [response]}

    def _aggregate(self, state:ChatState):

        question = state["question"]
        messages = state["aggregated_messages"]
        prompt = load_prompt(name="aggregator")
        chain = prompt | self.llm
        logger.info("Aggregator is being called")
        response = chain.invoke({
            "question": question,
            "messages": messages
        })
        logger.info("Aggregator generated a response")
        return {"final_response": response}


    def _build_chat_graph(self):
        graph = StateGraph(ChatState)
        graph.add_node("query_decomposition", self._query_decomposition)
        graph.add_node("compile_team", self._compile_team)
        graph.add_node("aggregator", self._aggregate)
        graph.add_node("persona_call", self._call_persona)
        graph.add_edge(START, "query_decomposition")
        graph.add_edge("query_decomposition", "compile_team")
        graph.add_edge("persona_call", "aggregator")
        graph.add_edge("aggregator", END)
        app = graph.compile()
        return app
    
    def run_chat(self, initial_state:dict):
        response = self.graph.invoke(initial_state)
        response = response["final_response"].content.replace("$", "\$")
        return response


