

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from src.states import State, RouterOutput, SynthesizedOutput, AgentOutput

from prompts.router_prompt import router_prompt
from prompts.excel_prompt  import excel_instructor_prompt, excel_instructor_prompt_1
from prompts.ml_prompt import ml_instructor_prompt, ml_instructor_prompt_1
from prompts.sql_prompt import sql_instructor_prompt, sql_instructor_prompt_1
from prompts.synthesize_prompt import synthesizer_prompt
from prompts.python_prompt import python_instructor_prompt, python_instructor_prompt_1
from prompts.general_prompt import general_instructor_prompt

from config import llm

from utils.domain_desc import get_selected_domain

def router_node(state : State) :

    prompt = router_prompt.format(query=state["query"])
    result= llm.with_structured_output(RouterOutput).invoke(prompt)
    
    return {"routes" : result}

def router_node_with_embedding(state : State) :

    selected_domains, entropy_norm =  get_selected_domain(state["query"])

    if entropy_norm <= 0.75 :
        result = RouterOutput(routes=selected_domains,  confidence= 1.00 - entropy_norm)
        return {"routes" : result}
    
    else :
        prompt = router_prompt.format(query=state["query"])
        result= llm.with_structured_output(RouterOutput).invoke(prompt)
        return {"routes" : result}

def python_node(state : State) : 

    if len(state['routes'].routes) ==  1 : 

        response = llm.with_structured_output(SynthesizedOutput).invoke([
                            SystemMessage(content = python_instructor_prompt_1),
                            HumanMessage(content= f"Question : {state['query']}") ])

        return { "final_response" : response }
    
    else : 

        response = llm.invoke([
            SystemMessage(content = python_instructor_prompt),
            HumanMessage(content= f"Question : {state['query']}")])
        
        return {"agent_outputs" : [{
                'agent' : "python" ,
                "answer" : response.content
            }]}

    
def sql_node(state : State) : 

    if len(state['routes'].routes) ==  1 :

        response = llm.with_structured_output(SynthesizedOutput).invoke([
                            SystemMessage(content = sql_instructor_prompt_1),
                            HumanMessage(content= f"Question : {state['query']}") ])
        
        return { "final_response" : response }
    
    else :

        response = llm.invoke([
            SystemMessage(content = sql_instructor_prompt),
            HumanMessage(content= f"Question : {state['query']}")])
        
        return {"agent_outputs" : [{
                'agent' : "sql" ,
                "answer" : response.content
            }]}


def excel_node(state : State) :

    if len(state['routes'].routes) ==  1 :

        response = llm.with_structured_output(SynthesizedOutput).invoke([
                            SystemMessage(content = excel_instructor_prompt_1),
                            HumanMessage(content= f"Question : {state['query']}") ])
        
        return { "final_response" : response }
    
    else :
        response = llm.invoke([
            SystemMessage(content = excel_instructor_prompt),
            HumanMessage(content= f"Question : {state['query']}")])
        
        return {"agent_outputs" : [{
                'agent' : "excel" ,
                "answer" : response.content
            }]}

def ml_node(state : State) : 

    if len(state['routes'].routes) ==  1 :

        response = llm.with_structured_output(SynthesizedOutput).invoke([
                            SystemMessage(content = ml_instructor_prompt_1),
                            HumanMessage(content= f"Question : {state['query']}") ])
        
        return { "final_response" : response }
    
    else :
        response = llm.invoke([
            SystemMessage(content = ml_instructor_prompt),
            HumanMessage(content= f"Question : {state['query']}")])
        
        return {"agent_outputs" : [{
                'agent' : "ml" ,
                "answer" : response.content
            }]}


def synthesizer_node(state: State):

    if len(state['routes'].routes) ==  1 :

        response = state['final_response']
        
        return {"final_response" : response}
    
    else :

        agent_outputs = state["agent_outputs"]

        response = llm.with_structured_output(SynthesizedOutput).invoke([
                SystemMessage(content=synthesizer_prompt),
                HumanMessage(content=f"""
                        User Question:
                        {state['query']}

                        Agent Responses:
                        {agent_outputs}
                            """
                            )])

    return {"final_response": response}
                

def general_instructor(state :State) : 
    response  = llm.invoke(
        [
            SystemMessage(content = general_instructor_prompt),
            HumanMessage(content= f"Question : {state['query']}")
        ]
    )

    return {"final_response" : response.content}