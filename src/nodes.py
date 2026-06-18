

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from src.states import State, RouterOutput
from src.prompts import router_prompt, python_instructor_prompt, sql_instructor_prompt, general_instructor_prompt, \
                    excel_instructor_prompt, ml_instructor_prompt, synthesizer_prompt

from config import llm

from utils.domain_desc import get_selected_domain

def router_node(state : State) :

    prompt = router_prompt.format(query=state["query"])
    result= llm.with_structured_output(RouterOutput).invoke(prompt)
    
    return {"routes" : result}

def router_node_with_embedding(state : State) :

    selected_domains, confidence =  get_selected_domain(state["query"])

    if selected_domains :

        result = RouterOutput(routes=selected_domains,  confidence=confidence )

        return {"routes" : result}

    prompt = router_prompt.format(query=state["query"])
    result= llm.with_structured_output(RouterOutput).invoke(prompt)
    
    return {"routes" : result}

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

def general_instructor(state :State) : 
    response  = llm.invoke(
        [
            SystemMessage(content = general_instructor_prompt),
            HumanMessage(content= f"Question : {state['query']}")
        ]
    )

    return {"final_response" : response.content}