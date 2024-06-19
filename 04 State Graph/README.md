# State Machine in LangGraph

This project demonstrates the use of the `langgraph` library to create a state machine for a simple lottery case. The workflow consists of nodes representing different states of the lottery process, where users keep buying ticket until win.

This tutorials is ref from
* [Learn LangGraph - The Easy Way](https://www.youtube.com/watch?v=R8KB-Zcynxc).
* [langgraph_code_assistant.ipynb](https://github.com/langchain-ai/langgraph/blob/main/examples/code_assistant/langgraph_code_assistant.ipynb)

## Environment Setup

### Prerequisites

- Python 3.11
- `langgraph` library

### Installing Dependencies

Install the necessary Python package:
```sh
pip install langgraph
```

## Script Explanation

### Importing Libraries

The script starts by importing the necessary libraries:

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal, Union
import random
```

### Defining State and Functions

Define a `TypedDict` for the lottery state and functions representing different actions in the lottery process:

```python
class LotteryState(TypedDict):
    input: str
    winnings: Union[str, None]
    missed: Union[str, None]


def BuyLottery(state: LotteryState):
    random_number = random.randint(0, 2)
    print("buy number: " + str(random_number))
    state['input'] = random_number
    return state


def Checking(state: LotteryState):
    prize_number = random.randint(0, 2)
    print("prize number: " + str(prize_number))
    if state['input'] == prize_number:
        state['winnings'] = "win"
        return state
    else:
        state['missed'] = "missed"
        return state


def checking_result(state: LotteryState) -> Literal["buy", END]:
    if state.get("winnings") == "win":
        print("You win! Go home.")
        return "win"
    else:
        print("You missed. Buy again.")
        return "missed"
```

### Creating the State Machine Workflow

Create a `StateGraph` instance and add the defined functions as nodes:

```python
# Define a LangGraph state machine
workflow = StateGraph(LotteryState)

# Add nodes to the workflow
workflow.add_node("buy", BuyLottery)
workflow.add_node("check", Checking)

# Set the entry point of the workflow
workflow.set_entry_point("buy")

# Define edges between nodes
workflow.add_edge("buy", "check")

# Add conditional edges
workflow.add_conditional_edges(
    "check",
    checking_result,
    {
        "missed": "buy",
        "win": END,
    },
)
```

### Compiling and Invoking the Workflow

Compile the workflow into a runnable app and start the lottery process:

```python
# Compile the workflow into a runnable app
app = workflow.compile()

# Start the lottery process
final_state = app.invoke({"input": "", "winnings": None, "missed": None})

print("Final State:", final_state)
```

## Running the Script

1. Ensure all dependencies are installed as described in the [Installing Dependencies](#installing-dependencies) section.
2. Run the Python script:
   ```sh
   python main.py
   ```