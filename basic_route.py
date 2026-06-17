from typing import TypedDict
from pydantic import BaseModel
from typing import Literal
from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from prompt import router_prompt, python_instructor_prompt, sql_instructor_prompt, \
                    excel_instructor_prompt, ml_instructor_prompt, general_instructor_prompt

from utils import save_graph

from dotenv import load_dotenv
load_dotenv()


class RouterOutput(BaseModel):
    route: Literal["python", "sql", "excel", "ml"]
    confidence :  float

class State(TypedDict):
    query: str
    route: RouterOutput
    response: str

llm = ChatGroq(model = "llama-3.1-8b-instant", #"llama-3.3-70b-versatile", 
               temperature=0.7, 
               max_tokens= 100
               )

def router_node(state : State) : 
    prompt = router_prompt.format(query=state["query"])
    
    result= llm.with_structured_output(RouterOutput).invoke(prompt)

    return {"route" : result}

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

def general_instructor(state :State) : 
    response  = llm.invoke(
        [
            SystemMessage(content = general_instructor_prompt),
            HumanMessage(content= f"Question : {state['query']}")
        ]
    )

    return {"response" : response}

def conditional_routing_node(state : State) : 
    route = state["route"]
    if route.confidence < 0.5 :
        return "general_instructor"
    
    return route.route
    

graph = StateGraph(State)
graph.add_node("router", router_node)
graph.add_node("python", python_node)
graph.add_node("sql", sql_node)
graph.add_node("excel", excel_node)
graph.add_node("ml", ml_node)
graph.add_node("general_instructor", general_instructor)

graph.add_edge(START, "router")
graph.add_conditional_edges("router", conditional_routing_node)
graph.add_edge("python", END)
graph.add_edge("sql", END)
graph.add_edge("excel", END)
graph.add_edge("ml", END)

instructor = graph.compile()
save_graph(instructor)

user_query = "How can I analyze sales data and build a prediction model?"

answer = instructor.invoke({"query": user_query })
print(answer["response"].content)

# #  debug
# for event in instructor.stream({"query": user_query}):    
#     print(event)