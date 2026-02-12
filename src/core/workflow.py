from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain_groq.chat_models import ChatGroq
from langgraph.graph import StateGraph, END, START
from src.utils import load_prompt
from dotenv import load_dotenv
from .schemas import ChatState, DecomposerResponse
from src.core.persona import Worker
from src.utils import get_logger
import os

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEYs")
logger = get_logger()

class Chat:
    def __init__(self, model_name):
        self.llm = ChatGroq(model=model_name, api_key=GROQ_API_KEY)
        self.worker = Worker(model_name="gemini-2.5-flash-lite")
        self.graph = self._build_chat_graph()

    def _query_decomposition(self, state: ChatState) -> ChatState:
        question = state["question"]
        prompt = load_prompt(name="decomposer")
        chain = prompt | self.llm.with_structured_output(DecomposerResponse, method="json_mode")
        logger.info("Query Decomposer is being called")
        response = chain.invoke({
            "question": question
        })
        logger.info("Query Decomposer generated a response")
        logger.info(response.model_dump_json(indent=2))
        return{"instructions":response.model_dump_json(indent=2)}        


    def _call_persona(self, state:ChatState):
        question = state["question"]
        domain = state["domain"]
        instructions = state["instructions"]
        response = self.worker.run_worker(persona_initial_state={
            "question": question,
            "name": domain,
            "instructions": instructions,
            "messages": [],
            "counter": 0,
            "score": 0,
            "corrections": ""
        })
        return {"final_response": response}


    def _build_chat_graph(self):
        graph = StateGraph(ChatState)
        graph.add_node("query_decomposition", self._query_decomposition)
        graph.add_node("persona_call", self._call_persona)
        graph.add_edge(START, "query_decomposition")
        graph.add_edge("query_decomposition", "persona_call")
        graph.add_edge("persona_call", END)
        app = graph.compile()
        return app
    
    def run_chat(self, initial_state:dict):
        response = self.graph.invoke(initial_state)
        response = response["final_response"].content
        return response


