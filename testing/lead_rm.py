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

# DB path
db_path = os.path.join('databse-sqllite/Lead.sqlite')
db_file = 'databse-sqllite/Lead.sqlite'

# # Helper function to execute a query and fetch results
# def execute_query(query: str, params=None):
#     conn = sqlite3.connect('databse-sqllite/Lead.sqlite')
#     cursor = conn.cursor()
#     if params:
#         cursor.execute(query, params)
#     else:
#         cursor.execute(query)
#     results = cursor.fetchall()
#     conn.close()
#     return results

# #print("Database Path:", execute_query("SELECT * FROM Leads"))
# # Tool Definitions with SQLite Queries
@tool
def get_all_lead_details():
    """
    Fetch all lead details from the Leads table in the database.

    This function retrieves all the leads available in the database.

    Returns:
        List[Dict]: A list of dictionaries representing all leads,
        where each dictionary contains column names as keys.
    """
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    query = 'SELECT * FROM Leads'  # Use uppercase for SQL keywords for readability
    cursor.execute(query)
    
    rows = cursor.fetchall()  # Fetch all rows from the query result
    column_names = [column[0] for column in cursor.description]  # Get column names
    results = [dict(zip(column_names, row)) for row in rows]  # Create a list of dictionaries

    cursor.close()
    conn.close()
    
    # It's usually best to avoid printing in library functions unless for debugging
    # Consider using logging instead if you want to keep track of the results
    return results
    
class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

class Assistent:
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

# ToolNode that will invoke the tools
#tool_node = ToolNode(tools)

# Define a function to call the model (Agent)
# def call_model(state: MessagesState) -> str:
#     """
#     Call the model (LLM) and return the response.

#     Args:
#         state (MessagesState): The current state of the messages.

#     Returns:
#         dict: The updated state with the LLM's response.
#     """
#     messages = state['messages']
#     response = model.invoke(messages)
#     return {"messages": [response]}

# # Function to determine if tools should be called or terminate the workflow
# def should_continue(state: MessagesState) -> Literal["tools", END]:
#     """
#     Determine whether the process should call tools or end the flow.

#     Args:
#         state (MessagesState): The current state of the messages.

#     Returns:
#         Literal["tools", END]: Returns 'tools' to call tools or END to finish.
#     """
#     messages = state['messages']
#     last_message = messages[-1]
    
#     if last_message.tool_calls:
#         return "tools"
#     return END

# Build the workflow graph
workflow = StateGraph(MessagesState)

# Add Nodes to the graph
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

# Define the edges (flow)
workflow.add_edge(START, "agent")  # Start with the agent
workflow.add_conditional_edges("agent", should_continue)  # Conditional edge to tools or end
workflow.add_edge("tools", "agent")  # After tools, go back to the agent

# Use MemorySaver for checkpoints
checkpointer = MemorySaver()

# Compile the graph
app = workflow.compile(checkpointer=checkpointer)


# User input to test the agent
user_input = input("Enter your question about leads: ")

# Prompt that will guide the agent
inp = f"""
You are an AI assistant with 10 years of experience in Prompt Engineering. Your task is to respond to the user's input by understanding the query, analyzing it, and using the appropriate tool from the available toolset to provide the best possible answer.

### Instructions:
1. **Understand the User Query**: Carefully analyze the user's input to grasp the intent and context of the question.
2. **Use the Tools Only**: Based on your analysis, select the most relevant tool from the toolset to retrieve information or solve the user's problem. You must ONLY provide information returned from the tools. You are **strictly forbidden** from generating any information outside the results provided by the tools. The preferred tools are: `get_all_lead_details`, `get_top_leads_info`, `get_followup`, `get_priority_leads`.
3. **Handle Empty Results**: If the tool returns no relevant data or an empty response, clearly state: "No Info Found."
4. **Deliver a Clear Output**: Ensure that the output is concise, accurate, and easy for the user to understand.

**Tools List**: `get_all_lead_details`, `get_top_leads_info`, `get_followup`, `get_priority_leads`

### Important Note:
You are **prohibited from generating any additional information beyond what these tools provide**. If no data is available, respond with "No Info Found."

### Input:
{user_input}

### Output:
Your response should directly address the user's query and meet their expectations, providing a clear and actionable answer based strictly on tool outputs. If no data is found, return the message: "No Info Found."
"""

# Invoke the compiled workflow with the user input
final_state = app.invoke(
    {"messages": [HumanMessage(content=inp)]}, 
    config={"configurable": {"thread_id": 42}}
)

# Get the final response from the last message
result = final_state["messages"][-1].content

# Output the final result
print("Final Response:", result)
