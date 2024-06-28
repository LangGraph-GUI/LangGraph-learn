from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal
import random
import json
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from abc import ABC, abstractmethod

# Specify the local language model
local_llm = "mistral"
llm = ChatOllama(model=local_llm, format="json", temperature=0)

# Clip the history to the last 8000 characters
def clip_history(history: str, max_chars: int = 8000) -> str:
    if len(history) > max_chars:
        return history[-max_chars:]
    return history

# Define the state for our workflow
class ToolState(TypedDict):
    history: str
    use_toll: bool

# Define the base class for tasks
class AgentBase(ABC):
    def __init__(self, state: ToolState):
        self.state = state

    @abstractmethod
    def get_prompt_template(self) -> str:
        pass

    def execute(self) -> ToolState:
        # Clip the history to the last 8000 characters
        self.state["history"] = clip_history(self.state["history"])
        
        # Define the prompt template
        template = self.get_prompt_template()
        prompt = PromptTemplate.from_template(template)        
        llm_chain = prompt | llm | StrOutputParser()
        generation = llm_chain.invoke({"history": self.state["history"], "use_toll": self.state["use_toll"]})
        data = json.loads(generation)
        self.state["use_tool"] = data.get("use_tool", "")        


        self.state["history"] += "\n" + generation
        self.state["history"] = clip_history(self.state["history"])

        return self.state

# Define agents
class ChatAgent(AgentBase):
    def get_prompt_template(self) -> str:
        return """
            {history}
            As ChatAgent, decide we need use tool/py or not
            if we don't need tool, just reply, otherwirse, let tool agent to handle
            Output the JSON in the format: {{"scenario": "your reply", "use_tool": True/False}}
        """

class ToolAgent(AgentBase):
    def get_prompt_template(self) -> str:
        return """
            History: {history}
            Available tools: {tools_list}
            Based on the history, choose the appropriate tool and arguments in the format:
            {{"use_tool": "<function>", "args": [<arg1>,<arg2>, ...]}}
        """

# for conditional edges
def check_use_tool(state: ToolState) -> Literal["use tool", "not use tool"]:
    if state.get("use_tool") == True:
        return "use tool"
    else:
        return "not use tool"

# Define the state machine
workflow = StateGraph(ToolState)

# Initialize tasks for DM and Player
def chat_agent(state: ToolState) -> ToolState:
    return ChatAgent(state).execute()

def tool_agent(state: ToolState) -> ToolState:
    return ToolAgent(state).execute()

workflow.add_node("chat_agent", chat_agent)
workflow.add_node("tool_agent", tool_agent)

workflow.set_entry_point("chat_agent")

# Define edges between nodes

workflow.add_conditional_edges(
    "chat_agent",
    check_use_tool,
    {
        "use tool": "tool_agent",
        "not use tool": END,
    }
)

# Compile the workflow into a runnable app
app = workflow.compile()

# Initialize the state
initial_state = ToolState(
    history="what files we have in current folder",
    use_tool=False, 
    )

for s in app.stream(initial_state):
    # Print the current state
    print("for s in app.stream(initial_state):")
    print(s)
