from langgraph.graph import Graph


def function_1(input_1):
    return input_1 + " Hello "

def function_2(input_2):
    return input_2 + "World!"


# Define a Langchain graph
workflow = Graph()

workflow.add_node("node_1", function_1)
workflow.add_node("node_2", function_2)

workflow.add_edge('node_1', 'node_2')

workflow.set_entry_point("node_1")
workflow.set_finish_point("node_2")

app = workflow.compile()

print(app.invoke("langgraph: "))