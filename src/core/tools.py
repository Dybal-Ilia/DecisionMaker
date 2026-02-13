from langchain_core.tools import tool
from tavily import TavilyClient
from dotenv import load_dotenv
from ..utils import get_logger
from .schemas import ArxiveArticle, ArxivSearchResult, PersonaCallTool
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from ..utils import load_prompt
import arxiv
import os

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
logger = get_logger()

@tool(description="A web-search tool")
def web_search(query: str):
    """Search for up-to-date information on the Internet.
    
    WHEN TO USE:
    - Questions about current products, prices, or availability
    - Real-time data: news, events, statistics, market info
    - Anything where recency matters
    
    WHEN NOT TO USE:
    - Deep academic or scientific research (use arxiv_search instead)
    - Questions you can answer confidently from established knowledge
    
    Args:
        query (str): a concise, specific web search query.
            - Good: "best machine learning desktop PC under $2000 2026"
            - Bad: "computer"
    """
    try:
        _tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
        logger.info(f"Web-search tool is being executed with query:\n{query}")
        return _tavily_client.search(query=query, search_depth="basic", max_results=2)
    except Exception as e:
        return "Web search tool is currently unavailable"

@tool(description="Arxiv articles search tool")
def arxiv_search(query:str):

    """Search for academic articles on arxiv.org
    WHEN TO USE:
    - User asks about scientific research, studies, or academic papers
    - You need evidence-based backing for claims about science, technology, medicine, or mathematics
    - User explicitly asks for sources or citations
    - Whenever you think that you might benefir from this tool
    
    WHEN NOT TO USE:
    - General product recommendations or purchasing advice
    - Questions about current events, prices, or real-time data (use web_search instead)
    - Simple factual questions you can answer confidently without a source
    
    Args:
        query (str): a focused academic search query — use specific technical terms, not conversational language.
            - Good: "transformer architecture GPU memory optimization"
            - Bad: "how to make my computer faster for AI"   
    """

    logger.info(f"Arxiv Search tool is being executed with query:\n{query}")
    articles = []
    client = arxiv.Client()
    response = arxiv.Search(query=query,
                            max_results=5,
                            sort_by=arxiv.SortCriterion.LastUpdatedDate,
                            sort_order=arxiv.SortOrder.Descending)
    
    for result in client.results(response):
        article = ArxiveArticle(
            title=result.title,
            url=result.entry_id,
            summary=result.summary[:150],
            authors=[author.name for author in result.authors[:3]]
        )
        articles.append(article)

    search_result = ArxivSearchResult(
        query=query,
        articles=articles
    )

    logger.info(f"Arxiv search results:\n{search_result}")
    return search_result.model_dump_json()


@tool(description="Call another agent for help", args_schema=PersonaCallTool)
def consult_expert(persona:str, query: str):
    """Tool to call another persona that can help figure out the problem
    
    WHEN TO USE THIS TOOL:
    - Whenever the user query is cross-domain and you have difficulty responding with your domain specification.
    - In case you think you might benefir from different point of view

    Args:
        persona (str): name of the persona to be called
        query (str): a query the persona will have to give answer to
    """
    logger.info("Tool consul_expert is executed")
    prompt = load_prompt(persona)
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite")
    chain = prompt | llm
    logger.info(f"Tool consult_expert called {persona} to execute:\n{query}")
    response = chain.invoke({
            "question": query,   
            "messages": "",
            "instructions": [],   
            "corrections": ""
        })
    return response.content[-1]["text"]
    



tools_list = [web_search, arxiv_search, consult_expert]