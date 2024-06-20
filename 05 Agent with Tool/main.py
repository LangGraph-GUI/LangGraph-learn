from langgraph.graph import StateGraph, END
from typing import TypedDict
import random
import json
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Define the state for our workflow
class TRPGState(TypedDict):
    role: str
    history: str

# Specify the local language model
local_llm = "phi3"
llm = ChatOllama(model=local_llm, format="json", temperature=0)

# Function to clip history to the last 8000 characters
def clip_history(history: str, max_chars: int = 8000) -> str:
    if len(history) > max_chars:
        return history[-max_chars:]
    return history

# Define the DM function
def DM(state: TRPGState):
   
    # Define the prompt template for the DM
    template = """
        You are the DM. Describe the current scenario for the player based on the following history.
        History: {history}
    """
    prompt = PromptTemplate.from_template(template)
    formatted_prompt = prompt.format(history=state["history"])
    llm_chain = prompt | llm | StrOutputParser()
    generation = llm_chain.invoke(formatted_prompt)
    
    state["history"] += "\n" + generation
    # Clip the history to the last 8000 characters
    state["history"] = clip_history(state["history"])

    state["role"] = "Player"
    return state

# Define the Player function
def Player(state: TRPGState):
   
    # Define the prompt template for the Player
    template = """
        You are the player. Here is the scenario: {scenario}
        What do you do? Provide a detailed action.
    """
    prompt = PromptTemplate.from_template(template)
    formatted_prompt = prompt.format(scenario=state["history"])
    llm_chain = prompt | llm | StrOutputParser()
    generation = llm_chain.invoke(formatted_prompt)
    
    state["history"] += "\n" + generation
    # Clip the history to the last 8000 characters
    state["history"] = clip_history(state["history"])

    state["role"] = "DM"
    return state

# Define the state machine
workflow = StateGraph(TRPGState)

workflow.add_node("dm", DM)
workflow.add_node("player", Player)

workflow.set_entry_point("dm")

# Define edges between nodes
workflow.add_edge("dm", "player")
workflow.add_edge("player", "dm")

# Compile the workflow into a runnable app
app = workflow.compile()

# Initialize the state
initial_state = TRPGState(role="DM", history="A monster appears in front of you.")

# Start the infinite gameplay loop
for s in app.stream(initial_state):
    print(s)
