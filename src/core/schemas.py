from typing import TypedDict, Annotated, Literal
from langchain_core.messages import AIMessage, BaseMessage
from pydantic import BaseModel, Field, UUID4
import operator


class DecomposerResponse(BaseModel):
    instructions: list[str] = Field(description="Numbered list of atomic requirements extracted from the query or Implicit assumptions about user intent")

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
    counter: int
    # score: int
    corrections: str
    final_response: AIMessage

class PersonaCallTool(BaseModel):
    persona: Literal['Society & Culture', 'Science & Mathematics', 'Health', 'Education & Reference', 'Computers & Internet', 'Sports',
                     'Business & Finance', 'Entertainment & Music', 'Family & Relationships', 'Politics & Government'] = Field(
                         ..., description="A name of persona to be called for query execution"
                     )
    query: str = Field(..., description="A query that is redirected to another persona (can fully match the initial user query)")



class User(BaseModel):
    user_id: UUID4 = Field(..., description="User Unique UUID4 Identifier")
    user_name: str = Field(..., description="User First Name")
    user_lastname:str = Field(..., description="User Lastname")
    user_nickname:str = Field(..., description="User Unique Nickname")
    user_password:str = Field(..., description= "User Password Hash")


class DecisionDraft(BaseModel):
    general_intent: str = Field(..., description="User's general intent. It's short and accurate." \
    "For example if user queries about vacation and going abroad it should be 'Travelling', etc.")
    options: list[str] = Field(..., description="A list of options the user provided. For example if the query is like" \
    "'I'm planning to buy a car and cant decide between audi and bmw' then the options are [audi, bmw]")
    preferences: list[str] = Field(..., description="A list of preferences provided by the user. It can be anything that the user mentioned. For example if the query is like:" \
    "'Help me decide where to travel, I want it to be warm and not rainy', the preferences are [the travel country is warm, the weather should be sunny]")
    assumptions: list[str] = Field(..., description="A list of your own assumptions. It is more like a draft of your plan and thoughts. What you are going to investigate, what should be taken into account, somw other notes you can only assume")
