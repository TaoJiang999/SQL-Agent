from typing import Annotated, List, Union
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    """The state of the agent."""
    messages: Annotated[List[BaseMessage], operator.add]
