from typing import TypedDict
from pydantic import BaseModel
from typing import Literal
from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from prompt import router_prompt, python_instructor_prompt, sql_instructor_prompt, \
                    excel_instructor_prompt, ml_instructor_prompt

from dotenv import load_dotenv
load_dotenv()

class State(TypedDict):
    query: str
    route: str
    response: str

class RouterOutput(BaseModel):
    route: Literal["python", "sql", "excel", "ml"]

llm = ChatGroq(model = "llama-3.3-70b-versatile", temperature=0)

def router_node(state : State) : 
    result= llm.with_structured_output(RouterOutput).invoke(router_prompt)
    return {"route" : result.route}

def python_node(state : State) : 
    response = llm.invoke( 
        [
            SystemMessage(content = python_instructor_prompt),
            HumanMessage(content= f"Question : {state['query']}")
        ]
    )

    return {"response" : response}

def sql_node(state : State) : 
    response = llm.invoke( 
        [
            SystemMessage(content = sql_instructor_prompt),
            HumanMessage(content= f"Question : {state['query']}")
        ]
    )

    return {"response" : response}

def excel_node(state : State) : 
    response = llm.invoke( 
        [
            SystemMessage(content = excel_instructor_prompt),
            HumanMessage(content= f"Question : {state['query']}")
        ]
    )

    return {"response" : response}

def ml_node(state : State) : 
    response = llm.invoke( 
        [
            SystemMessage(content = ml_instructor_prompt),
            HumanMessage(content= f"Question : {state['query']}")
        ]
    )

    return {"response" : response}

graph = StateGraph(State)
graph.add_node("router", router_node)
graph.add_node("python", python_node)
graph.add_node("sql", sql_node)
graph.add_node("excel", excel_node)
graph.add_node("ml", ml_node)

graph.add_edge(START, "router")
graph.add_conditional_edges(
    "router",
    lambda state: state["route"],
    {
        "python": "python",
        "sql": "sql",
        "excel": "excel",
        "ml": "ml"
    }
)
graph.add_edge("python", END)
graph.add_edge("sql", END)
graph.add_edge("excel", END)
graph.add_edge("ml", END)

instructor = graph.compile()

answer = instructor.invoke({"query":  "How does Random Forest work?"})
print(answer["response"].content)