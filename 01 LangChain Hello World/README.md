# Project Overview

This project demonstrates the use of the `langchain` and `langchain-community` libraries to interact with a locally hosted language model using the `ChatOllama` class. The script formats a prompt, sends it to the model, and processes the response.

## Environment Setup

### Prerequisites

- Python 3.11
- `langchain-community` and `langchain-core` libraries
- `ollama` server

### Installing Dependencies

Install the necessary Python packages:
```sh
pip install langchain-community langchain-core tenacity<8.4.0
```

### Setting Up the Ollama Server

Follow these steps to set up and run the `ollama` server:

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

The script starts by importing the necessary libraries from the `langchain` ecosystem:

```python
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
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

### Defining the Prompt Template

Define the prompt template to be used:

```python
template = "Question: {question}
Answer: Let's think step by step."
prompt = PromptTemplate.from_template(template)
```

### Formatting the Prompt

Format the prompt with the input variable:

```python
formatted_prompt = prompt.format(question="Tell me about you")
```

### Creating the LLM Chain

Create the LLM chain to process the prompt and parse the output:

```python
llm_chain = prompt | llm | StrOutputParser()
generation = llm_chain.invoke(formatted_prompt)
```

### Printing the Output

Print the generated output:

```python
print(generation)
```

## Running the Script

1. Ensure the `ollama` server is running as described in the [Setting Up the Ollama Server](#setting-up-the-ollama-server) section.
2. Run the Python script in another terminal:
   ```sh
   python main.py
   ```

## Notes

- Ensure all dependencies are installed and the `ollama` server is running before executing the script.
- Adjust the prompt template and input question as needed to suit your use case.
