# 03 Graph Chain Hello World

This project demonstrates the use of the `langgraph` and `langchain-community` libraries to create a workflow graph that interacts with a local language model to generate and process content.

## Environment Setup

### Prerequisites

- Python 3.11
- `langgraph`, `langchain-community`, and `langchain-core` libraries

### Installing Dependencies

Install the necessary Python packages:
```sh
pip install langgraph langchain-community langchain-core httpx
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

The script starts by importing the necessary libraries:

```python
from langgraph.graph import Graph
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json
```

### Specifying the Local Language Model

Specify the local language model to be used (`phi3` in this case):

```python
local_llm = "phi3"
```

### Initializing the ChatOllama Model

Initialize the `ChatOllama` model with desired parameters:

```python
llm = ChatOllama(model=local_llm, format="json", temperature=0)
```

### Defining Functions

Define the `Agent` and `Tool` functions to be used in the workflow:

```python
def Agent(question):
    # Define the prompt template
    template = """
        Question: {question} Let's think step by step.
        your output format is filename:"" and  content:""
        make sure your output is right json
    """
    
    prompt = PromptTemplate.from_template(template)

    # Format the prompt with the input variable
    formatted_prompt = prompt.format(question=question)

    llm_chain = prompt | llm | StrOutputParser()
    generation = llm_chain.invoke(formatted_prompt)
    
    return generation

def Tool(input):
    print("Tool Stage input:" + input)
    # Parse the JSON input
    data = json.loads(input)
    # Extract the "content" and "filename" parts
    content = data.get("content", "")
    filename = data.get("filename", "output.md")
    # Write the content to the specified filename
    with open(filename, 'w') as file:
        file.write(content)
    return input
```

### Creating the Workflow Graph

Create a `Graph` instance and add the defined functions as nodes:

```python
# Define a Langchain graph
workflow = Graph()

workflow.add_node("agent", Agent)
workflow.add_node("tool", Tool)
```

### Connecting the Nodes

Connect the nodes to define the workflow:

```python
workflow.add_edge('agent', 'tool')
```

### Setting Entry and Finish Points

Set the entry and finish points of the workflow:

```python
workflow.set_entry_point("agent")
workflow.set_finish_point("tool")
```

### Compiling and Invoking the Workflow

Compile the workflow and invoke it:

```python
app = workflow.compile()

app.invoke("write an article, content is startup.md ")

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

## Additional Resources

For more information and tutorials on using `LangGraph`, refer to [Learn LangGraph - The Easy Way](https://www.youtube.com/watch?v=R8KB-Zcynxc).
