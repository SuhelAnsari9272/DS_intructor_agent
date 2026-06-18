from typing import TypedDict, List, Dict, Annotated
from pydantic import BaseModel
from typing import Literal
from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from operator import add

from prompt import router_prompt, python_instructor_prompt, sql_instructor_prompt, \
                    excel_instructor_prompt, ml_instructor_prompt, synthesizer_prompt

from utils import save_graph

from dotenv import load_dotenv
load_dotenv()


ROUTES = {
        "python": "python",
        "sql": "sql",
        "excel": "excel",
        "ml": "ml",
    }


class RouterOutput(BaseModel):
    routes: List[Literal["python", "sql", "excel", "ml"]]

class State(TypedDict):
    query: str
    routes: List[str]   
    agent_outputs: Annotated[list, add]
    final_response: str

llm = ChatGroq(model = "llama-3.1-8b-instant", #"llama-3.3-70b-versatile", 
               temperature=0.7, 
               max_tokens= 200
               )

def router_node(state : State) :

    prompt = router_prompt.format(query=state["query"])
    result= llm.with_structured_output(RouterOutput).invoke(prompt)
    
    return {"routes" : result.routes}

def python_node(state : State) : 
    response = llm.invoke([
                        SystemMessage(content = python_instructor_prompt),
                        HumanMessage(content= f"Question : {state['query']}") ])

    return {
            "agent_outputs" : [
                {
                    'agent' : "python", 
                    "answer" : response.content
                }
            ]
        }

def sql_node(state : State) : 
    response = llm.invoke([
            SystemMessage(content = sql_instructor_prompt),
            HumanMessage(content= f"Question : {state['query']}")])


    return {
            "agent_outputs" : [
                {
                    'agent' : "sql", 
                    "answer" : response.content
                }
            ]
        }

def excel_node(state : State) : 
    response = llm.invoke([SystemMessage(content = excel_instructor_prompt),
                        HumanMessage(content= f"Question : {state['query']}")])

    return {
            "agent_outputs" : [
                {
                    'agent' : "excel", 
                    "answer" : response.content
                }
            ]
        }

def ml_node(state : State) : 
    response = llm.invoke([SystemMessage(content = ml_instructor_prompt),
                        HumanMessage(content= f"Question : {state['query']}")])

    return {
            "agent_outputs" : [
                {
                    'agent' : "ml", 
                    "answer" : response.content
                }
            ]
        }


def synthesizer_node(state: State):

    agent_outputs = state["agent_outputs"]

    response = llm.invoke([
            SystemMessage(content=synthesizer_prompt),
            HumanMessage(content=f"""
                    User Question:
                    {state['query']}

                    Agent Responses:
                    {agent_outputs}
                        """
                        )])

    return {"final_response": response.content}


def route_to_agents(state : State) : 
    return state['routes']



graph = StateGraph(State)
graph.add_node("router", router_node)
graph.add_node("python", python_node)
graph.add_node("sql", sql_node)
graph.add_node("excel", excel_node)
graph.add_node("ml", ml_node)
graph.add_node("synthesizer", synthesizer_node)

graph.add_edge(START, "router")
graph.add_conditional_edges("router", route_to_agents, ROUTES)

graph.add_edge("python", "synthesizer")
graph.add_edge("sql", "synthesizer")
graph.add_edge("excel", "synthesizer")
graph.add_edge("ml", "synthesizer")

graph.add_edge("synthesizer", END)

instructor = graph.compile()
save_graph(instructor)

user_question = "How do I train a Random Forest in Python?"

answer = instructor.invoke({"query": user_question})
print(answer['final_response'])

# #  debug
# for event in instructor.stream({"query": user_question}):    
#     print(event)