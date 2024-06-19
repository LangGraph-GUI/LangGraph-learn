from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal, Union
import random


class LotteryState(TypedDict):
    input: str
    winnings: Union[str, None]
    missed: Union[str, None]

# for node
def BuyLottery(state: LotteryState):
    random_number = random.randint(0, 2)
    print("buy number: " + str(random_number))
    state['input'] = random_number
    return state

# for node
def Checking(state: LotteryState):
    prize_number = random.randint(0, 2)
    print("prize number: " + str(prize_number))
    if state['input'] == prize_number:
        state['winnings'] = "win"
        return state
    else:
        state['missed'] = "missed"
        return state

# for conditional edges
def checking_result(state: LotteryState) -> Literal["win", "missed"]:
    if state.get("winnings") == "win":
        print("You win! Go home.")
        return "win"
    else:
        print("You missed. Buy again.")
        return "missed"


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

# Compile the workflow into a runnable app
app = workflow.compile()

# Start the lottery process
for s in app.stream({"input": "", "winnings": None, "missed": None}):
    print(s)
