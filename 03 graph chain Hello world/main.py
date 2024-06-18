from langgraph.graph import Graph

from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

import json


# Specify the local language model
local_llm = "phi3"

# Initialize the ChatOllama model with desired parameters
llm = ChatOllama(model=local_llm, format="json", temperature=0)


def Agent(question):
    # Define the prompt template
    template = "Question: {question}\nAnswer: Let's think step by step."
    prompt = PromptTemplate.from_template(template)

    # Format the prompt with the input variable
    formatted_prompt = prompt.format(question="Tell me about you")


    llm_chain = prompt | llm | StrOutputParser()
    generation = llm_chain.invoke(formatted_prompt)
    
    return generation


def Tool(input):
    # Parse the JSON input
    data = json.loads(input)
    # Extract the "answer" part
    answer = data.get("answer", "")
    # Write the answer to output.txt
    with open('output.txt', 'w') as file:
        file.write(answer)

    return input


# Define a Langchain graph
workflow = Graph()

workflow.add_node("agent", Agent)
workflow.add_node("tool", Tool)

workflow.add_edge('agent', 'tool')

workflow.set_entry_point("agent")
workflow.set_finish_point("tool")

app = workflow.compile()

print(app.invoke("Tell me about you"))
