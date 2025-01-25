from langgraph.graph import StateGraph, END, START
from typing import TypedDict, Literal, Union, Dict, Callable, Any
import random
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# ==========================
# Common state
# ==========================
class SharedState(TypedDict):
    active_subgraph: str
    input: Union[str, None]
    winnings: Union[str, None]
    missed: Union[str, None]
    buy_item: Union[str, None]

# ==========================
# Subgraph: Lottery
# ==========================
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

def checking_result(state: LotteryState) -> Literal["win", "missed"]:
    if state.get("winnings") == "win":
        print("You win! Go to buy.")
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


# ==========================
# Subgraph: Buy
# ==========================
class BuyState(TypedDict):
    buy_item: str

def buy_ice_cream(state: BuyState):
    print("Buy ice cream")
    return {"buy_item": "ice cream"}

buy_builder = StateGraph(BuyState)
buy_builder.add_node("buy", buy_ice_cream)
buy_builder.set_entry_point("buy")
buy_graph = buy_builder.compile()

# ==========================
# Subgraph Registry
# ==========================
subgraph_registry: Dict[str, Any] = {
    "lottery": lottery_graph,
    "buy": buy_graph,
}


# ==========================
# Main Graph: Root
# ==========================
class RootState(TypedDict):
   active_subgraph: str
   input: Union[str, None]
   winnings: Union[str, None]
   missed: Union[str, None]
   buy_item: Union[str, None]


def route_to_subgraph(state: RootState):
    
    active_subgraph = state['active_subgraph']
    if active_subgraph not in subgraph_registry:
        raise ValueError(f"Subgraph {active_subgraph} not found")

    subgraph = subgraph_registry[active_subgraph]
    
    if active_subgraph == "lottery":
        response = subgraph.invoke({"input": state['input'], "winnings": state['winnings'], "missed": state['missed']})
        
        if response.get("winnings") == "win":
             return {"active_subgraph": "buy", "input": None, "winnings": None, "missed": None, "buy_item": None}
        else:
            return {"active_subgraph": "lottery", "input": response['input'], "winnings": response['winnings'], "missed": response['missed'], "buy_item": None}
            
    elif active_subgraph == "buy":
        response = subgraph.invoke({"buy_item": state['buy_item']})
        return {"active_subgraph": None, "input": None, "winnings": None, "missed": None, "buy_item": response['buy_item']}
    else:
         return {"active_subgraph": None, "input": None, "winnings": None, "missed": None, "buy_item": None}
         
def check_subgraph_end(state: RootState) -> Literal["continue", "end"]:
    if state.get("active_subgraph") == None:
        return "end"
    else:
        return "continue"


root_builder = StateGraph(RootState)
root_builder.add_node("route", route_to_subgraph)
root_builder.set_entry_point("route")
root_builder.add_conditional_edges("route", check_subgraph_end, {
    "continue": "route",
    "end": END
})
root_graph = root_builder.compile()


# ==========================
# Main Graph: Top Level
# ==========================
class MainGraphState(TypedDict):
    active_subgraph: str
    input: Union[str, None]
    winnings: Union[str, None]
    missed: Union[str, None]
    buy_item: Union[str, None]


def main_entry(state: MainGraphState):
   return {"active_subgraph": "lottery", "input": None, "winnings": None, "missed": None, "buy_item": None}


main_builder = StateGraph(MainGraphState)
main_builder.add_node("main_entry", main_entry)
main_builder.add_node("root", root_graph)
main_builder.set_entry_point("main_entry")
main_builder.add_edge("main_entry", "root")
main_graph = main_builder.compile()


# ==========================
# Run
# ==========================
for s in main_graph.stream(
    {
        "active_subgraph": None,
        "input": None,
        "winnings": None,
        "missed": None,
        "buy_item": None
    }
):
    print(s)