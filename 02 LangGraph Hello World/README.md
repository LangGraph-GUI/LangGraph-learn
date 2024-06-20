# 02 LangGraph Hello World

This project demonstrates the use of the `langgraph` library to create a simple workflow graph with two nodes. Each node represents a function that processes input data and passes it to the next node.

This tutorials is refer to [Learn LangGraph - The Easy Way](https://www.youtube.com/watch?v=R8KB-Zcynxc).

## Environment Setup

### Prerequisites

- Python 3.11
- `langgraph` library

### Installing Dependencies

Install the necessary Python package:
```sh
pip install langgraph
```

## Core Explanation

### Defining Functions

Define two simple node to be used in the workflow:

```python
def function_1(input_1):
    return input_1 + " Hello "

def function_2(input_2):
    return input_2 + "World!"
```

### Creating the Workflow Graph

Create a `Graph` instance and add the defined functions as nodes:

```python
# Define a Langchain graph
workflow = Graph()

workflow.add_node("node_1", function_1)
workflow.add_node("node_2", function_2)
```

### Connecting the Nodes

Connect the nodes to define the workflow:

```python
workflow.add_edge('node_1', 'node_2')
```

### Setting Entry and Finish Points

Set the entry and finish points of the workflow:

```python
workflow.set_entry_point("node_1")
workflow.set_finish_point("node_2")
```

### Compiling and Invoking the Workflow

Compile the workflow and invoke it:

```python
app = workflow.compile()

output = app.invoke("langgraph: ")

print(output)
```

## Running the Script

Run the Python script:
   ```sh
   python main.py
   ```