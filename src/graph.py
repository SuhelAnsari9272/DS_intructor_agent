
from langgraph.graph import StateGraph, START, END
from src.states import State
from src.nodes import router_node, python_node, sql_node, excel_node, ml_node, general_instructor, synthesizer_node
from src.edges import conditional_routing_node

ROUTES = {
        "python": "python",
        "sql": "sql",
        "excel": "excel",
        "ml": "ml",
        "general_instructor" : "general_instructor"
    }

def create_workflow_graph()  :

    graph = StateGraph(State)
    graph.add_node("router", router_node)
    graph.add_node("general_instructor", general_instructor)
    graph.add_node("python", python_node)
    graph.add_node("sql", sql_node)
    graph.add_node("excel", excel_node)
    graph.add_node("ml", ml_node)
    graph.add_node("synthesizer", synthesizer_node)

    graph.add_edge(START, "router")
    graph.add_conditional_edges("router", conditional_routing_node,ROUTES)
    # graph.add_conditional_edges("router", route_to_agents, ROUTES)

    graph.add_edge("python", "synthesizer")
    graph.add_edge("sql", "synthesizer")
    graph.add_edge("excel", "synthesizer")
    graph.add_edge("ml", "synthesizer")

    graph.add_edge("synthesizer", END)

    return graph

