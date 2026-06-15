
def save_graph(graph) : 

    mermaid_code = graph.get_graph().draw_mermaid()

    # print(mermaid_code)
    with open("artifacts/graph.mmd", "w") as f:
        f.write(mermaid_code)