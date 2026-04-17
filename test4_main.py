from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
chat_model = ChatOpenAI(
    base_url="http://localhost:8080",
    api_key="not-needed",
    model="mlx-community/gemma-4-e4b-it-4bit"
)
class AgentState(TypedDict):
    number1: int | float
    number2: int | float
    operation: str
    result: int | float
    final_result: str
    question: str
def first_node(state: AgentState) -> AgentState:
    """This is the first node"""
    state["question"] = input("What is the math problem you want to solve?")
    n1_response = chat_model.invoke("Take the following math problem and extract the first number: " + state["question"] + " the output should only contain the number with nothing else.")
    n2_response = chat_model.invoke("Take the following math problem and extract the second number: " + state["question"] + " the output should only contain the number with nothing else.")
    op_response = chat_model.invoke("Take the following math problem and extract the operation: " + state["question"] + " the output should only contain the operation name (add, subtract, multiply, or divide) with nothing else.")
    state["number1"] = float(n1_response.content)
    state["number2"] = float(n2_response.content)
    state["operation"] = op_response.content.strip().lower()
    return state
def adder_node(state: AgentState) -> AgentState:
    """This is the adder node"""
    state["result"] = state["number1"] + state["number2"]
    state["final_result"] = f"The result of adding {state["number1"]} and {state["number2"]} is {state["result"]}"
    return state

def subtractor_node(state: AgentState) -> AgentState:
    """This is the subtractor node"""
    state["result"] = state["number1"] - state["number2"]
    state["final_result"] = f"The result of subtracting {state["number1"]} and {state["number2"]} is {state["result"]}"
    return state

def multiplier_node(state: AgentState) -> AgentState:
    """This is the multiplier node"""
    state["result"] = state["number1"] * state["number2"]
    state["final_result"] = f"The result of multiplying {state["number1"]} and {state["number2"]} is {state["result"]}"
    return state

def divider_node(state: AgentState) -> AgentState:
    """This is the divider node"""
    state["result"] = state["number1"] / state["number2"]
    state["final_result"] = f"The result of dividing {state["number1"]} and {state["number2"]} is {state["result"]}"
    return state

def router_node(state: AgentState) -> str:
    """This is the router function"""
    op = state.get("operation", "")
    if hasattr(op, "content"):
        op = op.content
    op = str(op).strip().lower()

    if "add" in op:
        return "adder_node"
    elif "subtract" in op:
        return "subtractor_node"
    elif "multiply" in op:
        return "multiplier_node"
    elif "divide" in op:
        return "divider_node"
    else:
        return END

graph = StateGraph(AgentState)
graph.add_node("first_node", first_node)
graph.add_node("adder_node", adder_node)
graph.add_node("subtractor_node", subtractor_node)
graph.add_node("multiplier_node", multiplier_node)
graph.add_node("divider_node", divider_node)

graph.add_conditional_edges("first_node", router_node)

graph.add_edge("adder_node", END)
graph.add_edge("subtractor_node", END)
graph.add_edge("multiplier_node", END)
graph.add_edge("divider_node", END)
graph.set_entry_point("first_node")
graph = graph.compile()
print(graph.invoke({}))
