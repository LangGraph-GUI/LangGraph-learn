# 02 LangGraph Hello World

This project demonstrates the use of the `langgraph` library to create a simple workflow graph with two nodes. Each node represents a function that processes input data and passes it to the next node.

This tutorials is refer to [Learn LangGraph - The Easy Way](https://www.youtube.com/watch?v=R8KB-Zcynxc).

## Environment Setup

### Prerequisites

- Python 3.11
- `langgraph` library
- `ollama` server (if needed)

### Installing Dependencies

Install the necessary Python package:
```sh
pip install langgraph
```

### Setting Up the Ollama Server

If your project requires the `ollama` server, follow these steps to set up and run it:

1. Open a terminal and start the `ollama` server:
   ```sh
   ollama serve
   ```

2. Open another terminal and run the Python script:
   ```sh
   python main.py
   ```

## Script Explanation

### Importing Libraries

The script starts by importing the necessary library:

```python
from langgraph.graph import Graph
```

### Defining Functions

Define two simple functions to be used in the workflow:

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

1. Ensure all dependencies are installed as described in the [Installing Dependencies](#installing-dependencies) section.
2. If required, ensure the `ollama` server is running as described in the [Setting Up the Ollama Server](#setting-up-the-ollama-server) section.
3. Run the Python script:
   ```sh
   python main.py
   ```

## Notes

- Ensure all dependencies are installed and the `ollama` server is running before executing the script (if needed).
- Adjust the functions and workflow as needed to suit your use case.

