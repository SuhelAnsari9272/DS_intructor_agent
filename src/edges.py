
from src.states import State

# fan-out 
def route_to_agents(state : State) : 
    return state['routes']


def conditional_routing_node(state : State) : 
    routes = state["routes"]

    if routes.confidence < 0.25 :    # this we need to tune
        return "general_instructor" 

    # if len(routes.routes) == 0 :
    #     return "general_instructor"
    
    return routes.routes

