from typing import TypedDict, List, Dict, Annotated
from pydantic import BaseModel, Field
from typing import Literal
from operator import add

class AgentOutput(BaseModel) :
    agent : str
    answer : str 
    # topics_covered: List[str] =  Field(default_factory=list)
    # related_topics: List[str] =  Field(default_factory=list)
    # key_takeaways: List[str] =  Field(default_factory=list)

class RouterOutput(BaseModel):
    routes: List[Literal["python", "sql", "excel", "ml"]]
    confidence : float


class SynthesizedOutput(BaseModel):
    answer: str =  Field(description="Short answer under 500 words.")
    topics_covered: List[str] = Field(default_factory=list)
    key_takeaways: List[str] =  Field(default_factory=list)
    recommended_next_topics: List[str] = Field(default_factory=list)

class State(TypedDict):
    query: str
    routes: RouterOutput
    agent_outputs: Annotated[AgentOutput, add]
    final_response: SynthesizedOutput
