from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal, Union
import random
import json
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Define the state for our workflow
class TRPGState(TypedDict):
    role: str
    message: str
    result: Union[str, None]

# Define the roll_dice function
def roll_dice(num_dice: int, die_size: int) -> int:
    """Rolls the specified number of dice with the given die size."""
    return sum(random.randint(1, die_size) for _ in range(num_dice))

# Specify the local language model
local_llm = "phi3"
llm = ChatOllama(model=local_llm, format="json", temperature=0)

# Define the DM function
def DM(state: TRPGState):
    # Define the prompt template for the DM
    template = """
        You are the DM. Describe the current scenario for the player.
        Scenario: {scenario}
    """
    prompt = PromptTemplate.from_template(template)
    scenario = "A monster appears in front of you."
    formatted_prompt = prompt.format(scenario=scenario)
    llm_chain = prompt | llm | StrOutputParser()
    generation = llm_chain.invoke(formatted_prompt)
    
    state["role"] = "Player"
    state["message"] = generation
    return state

# Define the Player function
def Player(state: TRPGState):
    # Define the prompt template for the Player
    template = """
        You are the player. Here is the scenario: {scenario}
        What do you do?
    """
    prompt = PromptTemplate.from_template(template)
    formatted_prompt = prompt.format(scenario=state["message"])
    llm_chain = prompt | llm | StrOutputParser()
    generation = llm_chain.invoke(formatted_prompt)
    
    state["role"] = "DM"
    state["message"] = generation
    return state

# Define the Action function
def Action(state: TRPGState):
    message = state.get("message", "")
    if "hit a monster with" in message:
        parts = message.split(" ")
        dice_info = parts[-1]
        num_dice, die_size = map(int, dice_info.split("d"))
        result = roll_dice(num_dice, die_size)
        state["result"] = f"Rolled {dice_info}: {result}"
    else:
        state["result"] = "The action was not recognized."
    return state

# Define the state machine
workflow = StateGraph(TRPGState)

workflow.add_node("dm", DM)
workflow.add_node("player", Player)
workflow.add_node("action", Action)

workflow.set_entry_point("dm")

# Define edges between nodes
workflow.add_edge("dm", "player")
workflow.add_edge("player", "action")
workflow.add_edge("action", "dm")

# Compile the workflow into a runnable app
app = workflow.compile()

# Initialize the state
initial_state = TRPGState(role="DM", message="A monster appears in front of you.", result=None)

# Start the infinite gameplay loop
for s in app.stream(initial_state):
    print(s)
