"""
LangGraph chatbot backend with SQLite-backed conversation persistence.

Exports `chatbot` (compiled graph) and `get_all_threads()` for use by the
Streamlit frontend (streamlit_frontend_tool.py).
"""

#******************************Imports********************************************
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from dotenv import load_dotenv
import sqlite3
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
import requests

#******************************Environment Setup********************************************
load_dotenv()

# OpenAI chat model; API key is read from the environment via load_dotenv()
llm = ChatOpenAI()


#******************************Tool Definition********************************************
search_tool = DuckDuckGoSearchRun(region="us-en")

@tool
def calculator(first_number: float, second_number: float, operation: str) -> dict:
    """
    Use this calculator to perform basic arithmetic operations on two numbers. 
    Supported operations: add, subtract, multiply, divide
    """
    try:
        if operation == "add":
            return {"result": first_number + second_number}
        elif operation == "subtract":
            return {"result": first_number - second_number}
        elif operation == "multiply":
            return {"result": first_number * second_number}
        elif operation == "divide":
            if second_number == 0:
                return {"error": "Cannot divide by zero"}
            return {"result": first_number / second_number}
        else:
            return {"error": "Invalid operation"}
    except Exception as e:
        return {"error": str(e)}

@tool
def get_stock_price(symbol: str) -> dict:
    """
    Use this tool to get the current price of a stock.
    """
    try:
        response = requests.get(f"https://api.example.com/stock/{symbol}")
        response.raise_for_status()
        return {"price": response.json()["price"]}
    except Exception as e:
        return {"error": str(e)}

tools = [calculator, get_stock_price, search_tool]
llm_with_tools = llm.bind_tools(tools)

#******************************State Definition********************************************
class ChatState(TypedDict):
    """Graph state: a growing list of chat messages."""
    messages: Annotated[list[BaseMessage], add_messages]

#******************************Graph Nodes********************************************
def chat_node(state: ChatState):
    """Invoke the LLM with the current message history and append its reply."""
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

tool_node = ToolNode(tools)

#******************************Persistence (SQLite Checkpointer)********************************************
# Persist conversation checkpoints to a local SQLite database so threads can
# be resumed across sessions.
connection = sqlite3.connect(database="chat_history.db", check_same_thread=False)
checkpointer = SqliteSaver(conn=connection)

#******************************Graph Construction********************************************
graph = StateGraph(ChatState)

graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chat_node")
graph.add_conditional_edges("chat_node", tools_condition)
graph.add_edge("tools", "chat_node")

# Compiled graph with checkpointing enabled; pass config={"configurable": {"thread_id": "..."}}
# when invoking or streaming to scope each conversation to a thread.
chatbot = graph.compile(checkpointer=checkpointer)

#******************************Debug / Manual Test********************************************
#config = {"configurable": {"thread_id": "123"}}
#print(chatbot.invoke({"messages": [HumanMessage(content="Hello, how are you?")]}, config=config))

#******************************Utility Functions********************************************
def get_all_threads():
    """Return every unique thread_id stored in the SQLite checkpointer."""
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config["configurable"]["thread_id"])
    return list(all_threads)
