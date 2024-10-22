# from llm_helper import apiKey, modal_name

# result = llm.invoke("Hello, how are you?")
# print(result)

from typing import Annotated, Literal, TypedDict
from langchain_core.messages import HumanMessage
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import Graph, StateGraph , START, END, MessagesState
from langgraph.prebuilt import ToolNode
from llm_helper import get_llm_modal_with_tools

# Define the tools for the agent to use
@tool
def serach(query: str):
    """Call to Surf the web"""
    if "sf" in query.lower() or 'san francisco' in query.lower():
        return "It's 60 degrees and foggy."
    return "I'm sorry, I don't have that information. 90"

tools = [serach]

tool_node = ToolNode(tools)

#model = ChatAnthropic(model='claude-3-5-sonnet-20240620', temperature=0, api_key=apiKey).bind_tools(tools)
model = get_llm_modal_with_tools(tools)

# Define the function that determines whether to continue or not
def should_continue(state:MessagesState) -> Literal["tools", END]:
    messages = state['messages']
    last_message = messages[-1]
    
    if last_message.tool_calls:
        return "tools"
    return END

# Define the function that calls the model
def call_model(state:MessagesState) -> str:
    messages = state['messages']
    response = model.invoke(messages)
    return {"messages": [response]}
 
workflow = StateGraph(MessagesState)

workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "agent")

workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", 'agent')

checkpointer = MemorySaver()

app = workflow.compile(checkpointer=checkpointer)

userInput = input("enter quetsion")

final_state = app.invoke({"messages": [HumanMessage(content=userInput)]}, config={"configurable": {"thread_id": 42}})

result = final_state["messages"][-1].content

print("final_state", result)
    