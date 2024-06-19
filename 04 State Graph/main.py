from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal, Union
import random


class LotteryState(TypedDict):
    input: str
    winnings: Union[str, None]
    missed: Union[str, None]


def BuyLottery(state: LotteryState):
    random_number = random.randint(0, 3)
    state['input'] = random_number
    return state


def Checking(state: LotteryState):
    if state['input'] == 0:
        state['winnings'] = "win"
        return state
    else:
        state['missed'] = "missed"
        return state


def checking_result(state: LotteryState) -> Literal["buy", END]:
    if state.get("winnings") == "win":
        print("You win! Go home.")
        return END
    else:
        print("You missed. Buy again.")
        return "buy"


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
        "buy": "buy",
        END: END,
    },
)

# Compile the workflow into a runnable app
app = workflow.compile()

# Start the lottery process
final_state = app.invoke({"input": "", "winnings": None, "missed": None})

print("Final State:", final_state)
