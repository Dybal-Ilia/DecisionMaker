from typing import TypedDict, Annotated
from langchain_core.messages import AIMessage
from pydantic import BaseModel, Field
import operator


class DecomposerResponse(BaseModel):
    instructions: list[str] = Field(description="Numbered list of atomic requirements extracted from the query")
    ambiguities: list[str] = Field(default_factory=list, description="Unclear aspects that might need clarification")
    assumed_context: list[str] = Field(default_factory=list, description="Implicit assumptions about user intent")

class ReflectorResponse(BaseModel):
    score: int = Field(default=0, description="Numeric integer response score from 1 to 10")
    corrections: list[str] = Field(default_factory=list, description="A list of corrections that should be applied to agents response")

class WorkerState(TypedDict):
    question: str
    name: str
    instructions: str
    messages: Annotated[list, operator.add]
    counter: int
    score: int
    corrections: str

class ChatState(TypedDict):
    question: str
    domain: str
    instructions: list[str]
    final_response: AIMessage



