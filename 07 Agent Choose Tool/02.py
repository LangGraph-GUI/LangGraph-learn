import inspect
import json
from typing import Callable, Dict, List, Any, TypedDict
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

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

# Define the state for our workflow
class ToolState(TypedDict):
    history: str

# Clip the history to the last 8000 characters
def clip_history(history: str, max_chars: int = 8000) -> str:
    if len(history) > max_chars:
        return history[-max_chars:]
    return history

class AgentBase:
    def __init__(self, state: ToolState):
        self.state = state

    def execute(self) -> ToolState:
        self.state["history"] = clip_history(self.state["history"])
        choice = self.llm_output(self.state["history"])
        tool_name = choice["use_tool"]
        args = self.convert_args(tool_name, choice["args"])
        result = globals()[tool_name](*args)
        self.state["history"] += f"\nQuestion: {self.state['history']}\nResponse: {result}\n"
        return self.state

    def llm_output(self, history: str) -> Dict[str, Any]:
        # Generate the detailed tools list
        tools_list = [
            {
                "name": tool["name"],
                "description": tool["description"]
            }
            for tool in tool_registry
        ]
        
        # Create the prompt for LLM
        template = """
            History: {history}
            Available tools: {tools_list}
            Based on the history, choose the appropriate tool and arguments in the format:
            {{"use_tool": "<function>", "args": [<arg1>,<arg2>, ...]}}
        """
        prompt = PromptTemplate.from_template(template)
        
        # Format the prompt with the input variables
        formatted_prompt = prompt.format(history=history, tools_list=json.dumps(tools_list))
        
        # Initialize the ChatOllama model with desired parameters
        local_llm = "phi3"
        llm = ChatOllama(model=local_llm, format="json", temperature=0)
        llm_chain = prompt | llm | StrOutputParser()
        
        # Invoke the LLM with the formatted prompt
        generation = llm_chain.invoke({"history": history, "tools_list": json.dumps(tools_list)})
        
        return json.loads(generation)
    
    def convert_args(self, tool_name: str, args: List[str]) -> List[Any]:
        tool_info = next(tool for tool in tool_registry if tool["name"] == tool_name)
        converted_args = []
        for arg, param in zip(args, tool_info["parameters"]):
            param_type = param["type"]
            converted_arg = param_type(arg)
            converted_args.append(converted_arg)
        return converted_args

class Robot(AgentBase):
    pass

# Initialize the state
initial_state = ToolState(
    history="help me add 3 and 6"
)

# Create a robot instance and handle the question
robot = Robot(initial_state)
final_state = robot.execute()

# Print the final state history
print(f"Final state history: {final_state['history']}")

# Initialize the state for the second question
initial_state = ToolState(
    history="help me see what files we have now"
)

# Create a robot instance and handle the question
robot = Robot(initial_state)
final_state = robot.execute()

# Print the final state history
print(f"Final state history: {final_state['history']}")
