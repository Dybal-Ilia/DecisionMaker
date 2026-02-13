from typing import TypedDict, Annotated, Literal
from langchain_core.messages import AIMessage, BaseMessage
from pydantic import BaseModel, Field
import operator


class DecomposerResponse(BaseModel):
    instructions: list[str] = Field(description="Numbered list of atomic requirements extracted from the query")
    ambiguities: list[str] = Field(default_factory=list, description="Unclear aspects that might need clarification")
    assumed_context: list[str] = Field(default_factory=list, description="Implicit assumptions about user intent")

class ReflectorResponse(BaseModel):
    score: int = Field(default=0, description="Numeric integer response score from 1 to 10")
    corrections: list[str] = Field(default_factory=list, description="A list of corrections that should be applied to agents response")

class ArxiveArticle(BaseModel):
    title: str = Field(..., description="Title of the article")
    url: str = Field(..., description="URL associated with the result")
    summary: str = Field(..., description="A short summary of the article provided by arxiv")
    authors: list[str] = Field(..., description="A list of authors who contributed to the article")

class ArxivSearchResult(BaseModel):
    query:str = Field(..., description="Initial search query")
    articles: list[ArxiveArticle] = Field(..., description="A list of ArxivArticle objects")
    

class ChatState(TypedDict):
    question: str
    domain: str
    instructions: list[str]
    messages: Annotated[list[BaseMessage], operator.add]
    context: str
    #counter: int
    score: int
    corrections: str
    final_response: AIMessage

class PersonaCallTool(BaseModel):
    persona: Literal['Society & Culture', 'Science & Mathematics', 'Health', 'Education & Reference', 'Computers & Internet', 'Sports',
                     'Business & Finance', 'Entertainment & Music', 'Family & Relationships', 'Politics & Government'] = Field(
                         ..., description="A name of persona to be called for query execution"
                     )
    query: str = Field(..., description="A query that is redirected to another persona (can fully match the initial user query)")



