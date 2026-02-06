from typing import TypedDict, Annotated
from pydantic import BaseModel, Field
from langchain_core.messages import AIMessage
import operator


class WorkerState(TypedDict):
    question: str
    name: str
    instructions: list[str]
    messages: Annotated[list, operator.add]
    corrections: Annotated[list, operator.add] 
    score: float
    counter: int

class ChatState(TypedDict):
    question: str
    team: list[str]
    instructions: list[str]
    aggregated_messages: Annotated[list, operator.add]
    final_response: AIMessage

class DecomposerResponse(BaseModel):
    instructions: list[str]


class ReflectionResponse(BaseModel):
    score: float = Field(default=0, description="A message score against provided question")
    correction: str = Field(..., description="Instructions for corrections")


