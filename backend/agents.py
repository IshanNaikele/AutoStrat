import operator
from typing import Annotated, List, TypedDict
from datetime import datetime

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
from dotenv import load_dotenv

# Import our custom tool setup
from backend.tools import get_search_tool

load_dotenv()

# --- 1. SETUP ---
tool = get_search_tool()
tools = [tool]

# Gemini Flash is fast and cheap
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
llm_with_tools = llm.bind_tools(tools)

# --- 2. HELPER FUNCTION ---
def parse_gemini_output(ai_message):
    """Fixes the issue where Gemini sometimes returns a list of text blocks."""
    if isinstance(ai_message.content, list):
        return " ".join([part['text'] for part in ai_message.content if 'text' in part])
    return ai_message.content

# --- 3. STATE DEFINITION ---
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    final_report: str

# --- 4. NODES ---

def researcher_node(state: AgentState):
    messages = state['messages']
    
    # CRITICAL: Get the current date for the prompt
    today = datetime.now().strftime("%B %d, %Y")
    
    sys_msg = SystemMessage(content=f"""
    You are a Senior Researcher. Today is {today}.
    
    Your goal is to find the most RECENT information on the user's topic.
    1. You MUST use the search tool.
    2. Include the current year ({today.split(',')[-1]}) in your search queries if relevant.
    3. Summarize the key findings (facts, stats, dates).
    """)
    
    response = llm_with_tools.invoke([sys_msg] + messages)
    return {"messages": [response]}

def analyst_node(state: AgentState):
    messages = state['messages']
    
    sys_msg = SystemMessage(content="""
    You are a Data Analyst. 
    Review the research data in the history.
    Identify 3 key trends and any conflicting information.
    Provide a structured analysis.
    """)
    
    response = llm.invoke([sys_msg] + messages)
    return {"messages": [response]}

def strategist_node(state: AgentState):
    messages = state['messages']
    
    sys_msg = SystemMessage(content="""
    You are a Content Strategist.
    Based on the analysis, write a high-quality blog post/report.
    
    Format Requirements:
    - Use Markdown (## Headers, bullet points).
    - Catchy Title.
    - specific section for 'Key Takeaways'.
    - No preamble (don't say "Here is the report"), just output the report.
    """)
    
    response = llm.invoke([sys_msg] + messages)
    
    # Clean output
    clean_content = parse_gemini_output(response)
    
    # Update state with the final string so the API can grab it easily
    return {"messages": [response], "final_report": clean_content}

# --- 5. BUILD GRAPH ---
workflow = StateGraph(AgentState)

workflow.add_node("researcher", researcher_node)
workflow.add_node("tools", ToolNode(tools))
workflow.add_node("analyst", analyst_node)
workflow.add_node("strategist", strategist_node)

# Define Edges
workflow.set_entry_point("researcher")

# Logic: Researcher -> (maybe Tools -> Researcher) -> Analyst -> Strategist -> END
workflow.add_conditional_edges(
    "researcher",
    tools_condition,
    {"tools": "tools", "__end__": "analyst"}
)
workflow.add_edge("tools", "researcher")
workflow.add_edge("analyst", "strategist")
workflow.add_edge("strategist", END)

# Compile
graph_app = workflow.compile()

 