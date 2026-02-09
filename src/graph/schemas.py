from typing import TypedDict, Annotated
from langchain_core.messages import AIMessage
import operator


class WorkerState(TypedDict):
    question: str
    name: str
    instructions: str
    messages: Annotated[list, operator.add]
    counter: int
    corrections: str

class ChatState(TypedDict):
    question: str
    team: list[str]
    instructions: list[str]
    aggregated_messages: Annotated[list, operator.add]
    final_response: AIMessage



