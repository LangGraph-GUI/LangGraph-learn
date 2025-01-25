from langgraph.graph import StateGraph, END, START
from typing import TypedDict, Literal, Union, Dict, Callable, Any
import random

# ==========================
# Subgraph Registry
# ==========================
subgraph_registry: Dict[str, Any] = {}

# ==========================
# Subgraph: Lottery
# ==========================
class LotteryState(TypedDict):
    input: str
    winnings: Union[str, None]
    missed: Union[str, None]
    try_times: int

def BuyLottery(state: LotteryState):
    random_number = random.randint(0, 3)
    print("buy number: " + str(random_number))
    state['input'] = random_number
    state['try_times'] += 1 
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

def checking_result(state: LotteryState) -> Literal["win", "missed"]:
    if state.get("winnings") == "win":
        print("You win!")
        return "win"
    else:
        print("You missed. Buy again.")
        return "missed"

lottery_builder = StateGraph(LotteryState)
lottery_builder.add_node("buy", BuyLottery)
lottery_builder.add_node("check", Checking)
lottery_builder.set_entry_point("buy")
lottery_builder.add_edge("buy", "check")
lottery_builder.add_conditional_edges(
    "check",
    checking_result,
    {
        "missed": "buy",
        "win": END,
    },
)
lottery_graph = lottery_builder.compile()
subgraph_registry["lottery"] = lottery_graph


# ==========================
# Subgraph: Buy
# ==========================
class BuyState(TypedDict):
    buy_item: str
    try_times: int

def buy_reward(state: BuyState):
    if state.get("try_times", 0) > 2:
        print("Buy ice cream")
        return {"buy_item": "ice cream", "try_times": state.get("try_times")}
    else:
        print("Buy cookie")
        return {"buy_item": "cookie", "try_times": state.get("try_times")}


buy_builder = StateGraph(BuyState)
buy_builder.add_node("buy", buy_reward)
buy_builder.set_entry_point("buy")
buy_graph = buy_builder.compile()

subgraph_registry["buy"] = buy_graph

# ==========================
# Subgraph: Root
# ==========================
class RootState(TypedDict):
    buy_item: Union[str, None]
    lottery_result: Union[str, None]
    try_times: int
    
def route_to_lottery(state: RootState):
    subgraph = subgraph_registry["lottery"]
    
    # Pass the try_times from RootState into LotteryState
    lottery_state = {"input": "0", "winnings": None, "missed": None, "try_times": state.get('try_times', 0)}
    response = subgraph.invoke(lottery_state)
    
    # Print try times before buy
    print("Lottery try times:", response.get("try_times"))
    
    return {"buy_item": state["buy_item"], "lottery_result": response.get("winnings"), "try_times": response.get("try_times")}


def route_to_buy(state: RootState):
    subgraph = subgraph_registry["buy"]
    # Pass try_times to buy subgraph
    response = subgraph.invoke({"buy_item": state['buy_item'], "try_times": state.get("try_times")})
    return {"buy_item": response.get("buy_item"), "lottery_result": state.get("lottery_result"), "try_times": response.get("try_times")}

root_builder = StateGraph(RootState)
root_builder.add_node("lottery", route_to_lottery)
root_builder.add_node("buy", route_to_buy)
root_builder.set_entry_point("lottery")
root_builder.add_edge("lottery", "buy")
root_graph = root_builder.compile()

subgraph_registry["root"] = root_graph

# ==========================
# Main Graph: Top Level
# ==========================
class MainGraphState(TypedDict):
    input: Union[str, None]


def invoke_subgraph(state: MainGraphState):
    subgraph = subgraph_registry["root"]
    response = subgraph.invoke(
         {"buy_item": None, "try_times": 0}
    )
    return  {
             "input": None
    }
    

main_graph = StateGraph(MainGraphState)
main_graph.add_node("subgraph", invoke_subgraph)
main_graph.set_entry_point("subgraph")

main_graph = main_graph.compile()


# ==========================
# Run
# ==========================
for s in main_graph.stream(
    {
        "input": None,
    }
):
    print(s)