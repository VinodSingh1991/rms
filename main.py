import sqlite3
import os
from typing import Annotated, Literal
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode
import pandas as pd
from llm_helper import get_llm_modal_with_tools
from langchain_core.runnables import Runnable, RunnableConfig
from langgraph.graph.message import AnyMessage, add_messages
from langchain.prompts import ChatPromptTemplate

from typing_extensions import TypedDict
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableLambda

from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition

# DB path
db_path = os.path.join('databse-sqllite/Lead.sqlite')

# #print("Database Path:", execute_query("SELECT * FROM Leads"))
# # Tool Definitions with SQLite Queries
import logging

# Initialize logging (this can be configured more globally)
logging.basicConfig(level=logging.INFO)

@tool
def get_all_lead_details(ss: str):
    
    """
    Fetch all lead details from the Leads table in the database.

    This function retrieves all the leads available in the database.

    Args:
        db_file (str): The path to the SQLite database file.

    Returns:
        List[Dict]: A list of dictionaries representing all leads,
        where each dictionary contains column names as keys.
    """
    conn = None
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        logging.info("Connected to database")

        # Execute query to fetch all rows from Leads table
        query = 'SELECT * FROM Leads'
        logging.info("Executing query: %s", query)
        cursor.execute(query)
        
        # Fetch all rows and extract column names
        rows = cursor.fetchall()
        column_names = [column[0] for column in cursor.description]
        results = [dict(zip(column_names, row)) for row in rows]
        
        logging.info("Query executed successfully, fetched %d rows", len(rows))
        
        return results
    
    except sqlite3.Error as e:
        logging.error("SQLite error: %s", e)
        return []

    finally:
        if conn:
            cursor.close()
            conn.close()
            logging.info("Database connection closed")

    
class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable
        
    def __call__(self, state: State, config: RunnableConfig):
        while True:
            # configuration = config.get("configurable", {})
            # passenger_id = configuration.get("passenger_id", None)
            # state = {**state, "user_info": passenger_id}
            result = self.runnable.invoke(state)
            # If the LLM happens to return an empty response, we will re-prompt it
            # for an actual response.
            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break
        return {"messages": result}

# Define Tools for LangGraph
tools = [get_all_lead_details]

# Bind tools to the LLM
model = get_llm_modal_with_tools(tools)

def handle_tool_error(state) -> dict:
    error = state.get("error")
    tool_calls = state["messages"][-1].tool_calls
    return {
        "messages": [
            ToolMessage(
                content=f"Error: {repr(error)}\n please fix your mistakes.",
                tool_call_id=tc["id"],
            )
            for tc in tool_calls
        ]
    }

def create_tool_node_with_fallback(tools: list) -> dict:
    return ToolNode(tools).with_fallbacks(
        [RunnableLambda(handle_tool_error)], exception_key="error"
    )
# User input to test the agent
#user_input = input("Enter your question about leads: ")

user_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", 
         "You are the database assistant for a lead management system. "
         "Use the provided tools to search for lead details, top leads, follow-up information, and priority leads. "
         "Be persistent when searching. If a search returns no results, provide a message to the user. `No Result found from your tools`"
         ### Important Note:
        "You are **prohibited from generating any additional information beyond what these tools provide**. If no data is available, respond with `No Result found from your tools`."

         ),
       
       
        ("placeholder", "{messages}")
    ]
)

assistant_runnable = user_prompt | model

#print("assistant_runnable", assistant_runnable)


builder = StateGraph(State)

builder.add_node("assistant", Assistant(assistant_runnable))
builder.add_node("tools", create_tool_node_with_fallback(tools))
builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "assistant")

memory = MemorySaver()

app = builder.compile(checkpointer=memory)

# result = app.invoke({"messages": [HumanMessage(content=user_input)]}, config={"configurable": {"thread_id": 42}})

# print("res", result.messages[-1].content)

import uuid
thread_id = str(uuid.uuid4())

db_file = 'databse-sqllite/Lead.sqlite'

config = {
    "configurable": {
        # The passenger_id is used in our flight tools to
        # fetch the user's flight information\
        # Checkpoints are accessed by thread_id
        "thread_id": thread_id,
    }
}

_printed = set()

events = app.stream(
        {"messages": ("user", "what is list of leads")}, config, stream_mode="values"
)


def _print_event(event: dict, _printed: set, max_length=1500):
    current_state = event.get("dialog_state")
    if current_state:
        print("Currently in: ", current_state[-1])
    message = event.get("messages")
    if message:
        if isinstance(message, list):
            message = message[-1]
        if message.id not in _printed:
            msg_repr = message.pretty_repr(html=True)
            if len(msg_repr) > max_length:
                msg_repr = msg_repr[:max_length] + " ... (truncated)"
            print(msg_repr)
            _printed.add(message.id)
            
for event in events:
    _print_event(event, _printed)