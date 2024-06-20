# 03 Graph Chain Hello World

This project demonstrates the use of the `langgraph` and `langchain-community` libraries to create a workflow graph that interacts with a local language model to generate and process content.

This tutorials is refer to [Learn LangGraph - The Easy Way](https://www.youtube.com/watch?v=R8KB-Zcynxc).

## Core Explanation


### Defining Functions

Because we use json format, we can parse that 

```python
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

## Running the Script

1. Ensure all dependencies are installed as described in the [Installing Dependencies](#installing-dependencies) section.
2. If required, ensure the `ollama` server is running as described in the [Setting Up the Ollama Server](#setting-up-the-ollama-server) section.
3. Run the Python script:
   ```sh
   python main.py
   ```