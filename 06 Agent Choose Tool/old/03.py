from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal
from typing import Callable, Dict, List, Any, TypedDict
import inspect
import random
import json
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from abc import ABC, abstractmethod

# Tool registry to hold information about tools
tool_registry: List[Dict[str, Any]] = []

# Decorator to register tools
def register_tool(func: Callable) -> Callable:
    signature = inspect.signature(func)
    docstring = func.__doc__ or ""
    params = [
        {"name": param.name, "type": param.annotation}
        for param in signature.parameters.values()
    ]
    tool_info = {
        "name": func.__name__,
        "description": docstring,
        "parameters": params
    }
    tool_registry.append(tool_info)
    return func

# Define the tools with detailed parameter descriptions in the docstrings
@register_tool
def add(a: int, b: int) -> int:
    """
    :function: add   
    :param int a: First number to add
    :param int b: Second number to add
    :return: Sum of a and b
    """
    return a + b

@register_tool
def ls() -> List[str]:
    """
    :function: ls
    :return: List of filenames in the current directory
    """
    # Fake implementation
    return ["file1.txt", "file2.txt", "file3.txt"]

@register_tool
def filewrite(name: str, content: str) -> None:
    """
    :function: filewrite
    :param str name: Name of the file
    :param str content: Content to write to the file
    :return: None
    """
    # Fake implementation
    print(f"Writing to {name}: {content}")


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
    use_tool: bool
    tool_exec: str


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
        generation = llm_chain.invoke({"history": self.state["history"], "use_tool": self.state["use_tool"]})
        data = json.loads(generation)
        self.state["use_tool"] = data.get("use_tool", "")        
        self.state["tool_exec"] = data

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
            {{"function": "<function>", "args": [<arg1>,<arg2>, ...]}}
        """

def ToolExecute(state: ToolState) -> ToolState:
    choice = self.llm_output(self.state["tool_exec"])
    tool_name = choice["use_tool"]
    args = self.convert_args(tool_name, choice["args"])
    result = globals()[tool_name](*args)

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
workflow.add_node("tool", ToolExecute)

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

workflow.add_edge('tool_agent', 'tool')



# Compile the workflow into a runnable app
app = workflow.compile()

# Initialize the state
initial_state = ToolState(
    history="help me ls files in current folder",
    use_tool=False, 
    )

for s in app.stream(initial_state):
    # Print the current state
    print("for s in app.stream(initial_state):")
    print(s)
