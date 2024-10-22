import sqlite3
import os
from typing import Annotated
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables import Runnable, RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode
from llm_helper import get_llm_modal_with_tools
from langgraph.graph.message import AnyMessage, add_messages
from langchain.prompts import ChatPromptTemplate
from typing_extensions import TypedDict
from langgraph.prebuilt import ToolNode, tools_condition
from testing.response_helper import convert_response_to_modal

import logging

# Initialize logging (this can be configured more globally)
logging.basicConfig(level=logging.INFO)

@tool
def get_all_lead_details(ss: str):
    """
        Fetch all lead details from the Leads table in the database.
        
        Args:
            db_file (str): The path to the SQLite database file.

        Returns:
            The tool must return the output in the following structured JSON format:

            {
            "status": "success",  # Fixed key for status
            "response_type": "table",      # Fixed key for type
            "total_no_of_leads": <int>,  # Total number of leads retrieved
            "acid_columns": <list of column names>,  # List of column names in the table
            "acid_rows": <list of row dictionaries>  # List of row dictionaries, each representing a lead
            "acid_update_message_of_ai": "Here is The List of Complete Leads"
            }

            If no leads are found, the response should be:

            {
            "status": "error",  # Fixed key for status
            "message": "No Result found from your tools"  # Error message
            }
        """
    
    conn = None
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        logging.info("Connected to database")

        # Execute query to fetch all rows from Leads table
        query = 'SELECT * FROM Leads LIMIT 1'
        logging.info("Executing query: %s", query)
        cursor.execute(query)
        
        # Fetch all rows and extract column names
        rows = cursor.fetchall()
        column_names = [column[0] for column in cursor.description]
        #results = convert_response_to_modal("table", {"rows": rows, "columns": column_names})
        results = [dict(zip(column_names, row)) for row in rows]
        
        output = {
            "acid_result_type": "acid_table",
            "total_no_of_leads": len(rows),
            "acid_columns": column_names,
            "acid_rows": results,
            "acid_update_message_of_ai": "Here is The List of Complete Leads"
        }  
        logging.info("Query executed successfully, fetched %d rows", len(rows))
        
        return output
    
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
         "Your task is to use the provided tools to search for lead details, top leads, follow-up information, and priority leads. "
         "You must return responses in the structured format specified in the tool descriptions. "
         "Each tool will have its own expected output format that you must follow precisely. "
         "The output must always include the following keys: status, response_type, and the relevant data fields depending on the tool used."
         
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

# events = app.stream(
#         {"messages": ("user", "what is list of leads")}, config, stream_mode="values"
# )


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
            
# for event in events:
#     _print_event(event, _printed)

def start_app(msg):
    # print("msg", msg)
    
    # return msg
    messages = app.invoke({"messages": [("user", msg.message)]}, config)
    message = messages.get("messages")
    if message:
        if isinstance(message, list):
                message = message[-1]
    
    return message

# result = start_app()

# print("events", result)