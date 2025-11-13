import os
from dotenv import load_dotenv
from typing import Annotated, TypedDict, List
import operator
from datetime import datetime 

# --- Use the new, correct package ---
from langchain_tavily import TavilySearch

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition

# 1. Load Keys
load_dotenv()

# 2. Setup Tools & Model
tool = TavilySearch(max_results=2)
tools = [tool]

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
llm_with_tools = llm.bind_tools(tools)

# 3. Define State
class State(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]

# 4. Define the Agent Node
def agent_node(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

# Helper to clean up Gemini's final answer
def parse_gemini_output(ai_message):
    if isinstance(ai_message.content, list):
        return " ".join([part['text'] for part in ai_message.content if 'text' in part])
    return ai_message.content

# 5. Build the Graph
workflow = StateGraph(State)

workflow.add_node("agent", agent_node)
workflow.add_node("tools", ToolNode(tools))

workflow.set_entry_point("agent")

workflow.add_conditional_edges(
    "agent",
    tools_condition,
)

workflow.add_edge("tools", "agent")

app = workflow.compile()

# --- TEST IT ---
if __name__ == "__main__":
    print("🤖 Asking Agent to search (with current date)...")
    
    today = datetime.now().strftime("%B %d, %Y")
    input_text = f"Today is {today}. What is the weather in Nagpur right now?"
    
    print(f"   Query: {input_text}\n")
    
    # Stream the events
    events = app.stream(
        {"messages": [HumanMessage(content=input_text)]},
        stream_mode="values"
    )
    
    for event in events:
        # --- FIX IS HERE ---
        last_message = event["messages"][-1] 
        # -------------------
        
        if last_message.type == "ai":
            if hasattr(last_message, 'tool_calls') and len(last_message.tool_calls) > 0:
                print(f"[AI]: 👉 Decided to use tool: {last_message.tool_calls[0]['name']}")
            else:
                clean_answer = parse_gemini_output(last_message)
                print(f"\n[AI]: {clean_answer}")
        
        elif last_message.type == "tool":
            print(f"[Tool Output]: {last_message.content[:200]}...")