from langgraph.graph import StateGraph, END
from typing import TypedDict
import random
import json
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from abc import ABC, abstractmethod

# Specify the local language model
local_llm = "mistral"
llm = ChatOllama(model=local_llm, format="json", temperature=0)

# Function to clip history to the last 8000 characters
def clip_history(history: str, max_chars: int = 8000) -> str:
    if len(history) > max_chars:
        return history[-max_chars:]
    return history

# Define the state for our workflow
class TRPGState(TypedDict):
    history: str

# Define the base class for tasks
class AgentBase(ABC):
    def __init__(self, state: TRPGState):
        self.state = state

    @abstractmethod
    def get_prompt_template(self) -> str:
        pass

    def execute(self) -> TRPGState:
        # Clip the history to the last 8000 characters
        self.state["history"] = clip_history(self.state["history"])
        
        # Define the prompt template
        template = self.get_prompt_template()
        prompt = PromptTemplate.from_template(template)
        formatted_prompt = prompt.format(history=self.state["history"])
        
        llm_chain = prompt | llm | StrOutputParser()
        generation = llm_chain.invoke(formatted_prompt)
        
        self.state["history"] += "\n" + generation
        # Clip the history to the last 8000 characters
        self.state["history"] = clip_history(self.state["history"])

        return self.state

# Define specific task classes
class DM(AgentBase):
    def get_prompt_template(self) -> str:
        return """
            {history}
            As DM. Describe the current scenario for the player 
        """

class Player(AgentBase):
    def get_prompt_template(self) -> str:
        return """
            Here is the scenario: {history}
            As a Player, I want 
            output is action
        """

# Define the state machine
workflow = StateGraph(TRPGState)

# Initialize tasks for DM and Player
def dm_task(state: TRPGState) -> TRPGState:
    return DM(state).execute()

def player_task(state: TRPGState) -> TRPGState:
    return Player(state).execute()

workflow.add_node("dm", dm_task)
workflow.add_node("player", player_task)

workflow.set_entry_point("dm")

# Define edges between nodes
workflow.add_edge("dm", "player")
workflow.add_edge("player", "dm")

# Compile the workflow into a runnable app
app = workflow.compile()

# Initialize the state
initial_state = TRPGState(role="DM", history="A monster appears in front of you.")


for s in app.stream(initial_state):
    # Print the current state
    print(s)
