
from langgraph.graph import Graph

from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

import json


from langgraph.graph import StateGraph
from typing import TypedDict, List, Annotated
import Operator

class State(TypedDict):
    input: str
    all_actions: Annotated[List[str], operator.add]




# Specify the local language model
local_llm = "phi3"

# Initialize the ChatOllama model with desired parameters
llm = ChatOllama(model=local_llm, format="json", temperature=0)


def Task(question):
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

# Define a Langchain graph
workflow = Graph()

workflow.add_node("task", Task)
workflow.add_node("tool", Tool)

workflow.add_edge('task', 'tool')

workflow.set_entry_point("task")
workflow.set_finish_point("tool")

app = workflow.compile()

app.invoke("write an article, content is startup.md ")
