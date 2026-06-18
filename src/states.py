from typing import TypedDict, List, Dict, Annotated
from pydantic import BaseModel
from typing import Literal
from operator import add

class AgentOutput(BaseModel) :
    agent : str
    answer : str

class RouterOutput(BaseModel):
    routes: List[Literal["python", "sql", "excel", "ml"]]
    confidence : float

class State(TypedDict):
    query: str
    routes: RouterOutput
    agent_outputs: Annotated[AgentOutput, add]
    final_response: str
