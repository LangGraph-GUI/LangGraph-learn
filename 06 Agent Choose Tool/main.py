from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal, Callable, Dict, List, Any
import inspect
import json
import random
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from abc import ABC, abstractmethod

# Tool registry to hold information about tools
tool_registry: Dict[str, Callable] = {}
tool_info_registry: List[Dict[str, Any]] = []

# Decorator to register tools
def tool(func: Callable) -> Callable:
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
    tool_registry[func.__name__] = func
    tool_info_registry.append(tool_info)
    return func

# Define the tools with detailed parameter descriptions in the docstrings
@tool
def mul(a: int, b: int) -> int:
    """
    :function: mul   
    :param int a: First number to add
    :param int b: Second number to add
    :return: a * b
    """
    return a * b

@tool
def ls() -> List[str]:
    """
    :function: ls
    :return: List of filenames in the current directory
    """
    # Fake implementation
    return ["file1.txt", "file2.txt", "file3.txt"]

@tool
def filewrite(name: str, content: str) -> None:
    """
    :function: filewrite
    :param str name: Name of the file
    :param str content: Content to write to the file
    :return: None
    """
    # Fake implementation
    print(f"Writing to {name}: {content}")

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
    tools_list: str

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
        llm = ChatOllama(model="mistral", format="json", temperature=0)
        llm_chain = prompt | llm | StrOutputParser()
        generation = llm_chain.invoke({
            "history": self.state["history"], 
            "use_tool": self.state["use_tool"],
            "tools_list": self.state["tools_list"]
        })
        data = json.loads(generation)
        self.state["use_tool"] = data.get("use_tool", False)        
        self.state["tool_exec"] = generation

        self.state["history"] += "\n" + generation
        self.state["history"] = clip_history(self.state["history"])

        return self.state

# Define agents
class ChatAgent(AgentBase):
    def get_prompt_template(self) -> str:
        return """
            Available tools: {tools_list}
            Question: {history}
            As ChatAgent, decide if we need to use a tool or not.
            If we don't need a tool, just reply; otherwise, let the ToolAgent handle it.
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

def ToolExecutor(state: ToolState) -> ToolState:
    if not state["tool_exec"]:
        raise ValueError("No tool_exec data available to execute.")
    
    choice = json.loads(state["tool_exec"])
    tool_name = choice["function"]
    args = choice["args"]
    
    if tool_name not in tool_registry:
        raise ValueError(f"Tool {tool_name} not found in registry.")
    
    result = tool_registry[tool_name](*args)
    state["history"] += f"\nExecuted {tool_name} with result: {result}"
    state["history"] = clip_history(state["history"])
    state["use_tool"] = False
    state["tool_exec"] = ""
    return state

# For conditional edges
def check_use_tool(state: ToolState) -> Literal["use tool", "not use tool"]:
    if state.get("use_tool") == True:
        return "use tool"
    else:
        return "not use tool"

# Define the state machine
workflow = StateGraph(ToolState)

# Initialize tasks for ChatAgent and ToolAgent
def chat_agent(state: ToolState) -> ToolState:
    return ChatAgent(state).execute()

def tool_agent(state: ToolState) -> ToolState:
    return ToolAgent(state).execute()

workflow.add_node("chat_agent", chat_agent)
workflow.add_node("tool_agent", tool_agent)
workflow.add_node("tool", ToolExecutor)

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
workflow.add_edge('tool', END)

# Generate the tools list
tools_list = json.dumps([
    {
        "name": tool["name"],
        "description": tool["description"]
    }
    for tool in tool_info_registry
])

# Compile the workflow into a runnable app
app = workflow.compile()

def question(history: str) -> None:
    initial_state = ToolState(
        history=history,
        use_tool=False,
        tool_exec="",
        tools_list=tools_list
    )

    for state in app.stream(initial_state):
        print(state)

# Example usage
if __name__ == "__main__":
    question("help me ls files in current folder")
    question("who are you")
