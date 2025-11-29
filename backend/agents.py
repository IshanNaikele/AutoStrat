import operator
from typing import Annotated,TypedDict,List
from datetime import datetime
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage,BaseMessage,HumanMessage
from langgraph.graph import START,END,StateGraph
from langgraph.prebuilt import ToolNode,tools_condition

# For loading the API Key & other Credentials from the .env file 
from dotenv import load_dotenv
load_dotenv()
GEMINI_API_KEY=os.getenv("GOOGLE_API_KEY")
# Import from other Files 
from backend.tools import get_search_tool

# For Using tool 
tool=get_search_tool()
tools=[tool]

# For Binding Tool with LLM 
llm=ChatGoogleGenerativeAI(model="gemini-2.5-flash",temperature=0,api_key=GEMINI_API_KEY)
llm_with_tools=llm.bind_tools(tools)


def parse_gemini_output(ai_message):
    if isinstance(ai_message.content,str):
        return ai_message.content
     
    if isinstance(ai_message.content,list):
        parts=[]
        for part in ai_message.content :
            if isinstance(part,dict) and 'text' in part:
                parts.append(part['text'])
            elif isinstance(part,str):
                parts.append(part)

        return " ".join(parts)
    
    return  str(ai_message.content)

        
 # State Defination 
 

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    research_data:str
    analysis_data:str
    final_data :str


def researcher_node(state: AgentState):
    print("="*80)
    print("👉 ENTERING: Researcher Node")
    print("="*80)
    messages = state['messages']
    today = datetime.now().strftime("%B %d, %Y")
    
    sys_msg = SystemMessage(content=f"""
    You are a Senior Researcher. Today is {today}.
    You are a Senior Market Researcher conducting comprehensive research.

YOUR TASK:
1. Use the search tool to find the TOP 5 most relevant and recent sources about this topic
2. Focus on: research papers, news articles, industry reports, expert opinions, and emerging trends
3. Search for: key statistics, market data, competing viewpoints, and real-world applications
4. Prioritize sources from the last 6 months for current trends
5. Look for both mainstream and specialized/technical sources

OUTPUT FORMAT:
- List each source with: Title, URL, Key Findings (2-3 sentences per source)
- Include publication dates where available
- Highlight any conflicting information across sources
- Minimum 300 words of substantive research findings
    """)
    
    print("="*80)
    print(sys_msg)
    print("="*80)

    response = llm_with_tools.invoke([sys_msg] + messages)
    
    # --- THE FIX FOR DISAPPEARING DATA ---
    # Only update 'research_data' if the agent actually wrote text.
    # If it just called a tool (content is empty), keep the OLD data (or empty string).
    content = parse_gemini_output(response)
    
    if content and len(content) > 10:
        return {"messages": [response], "research_data": content}
    
    # If empty (tool call), just update messages, don't wipe research_data
    return {"messages": [response]}


def analyst_node(state: AgentState):
    print("👉 ENTERING: Analyst Node") 
    
    # 1. Get the CLEAN data
    research_output = state.get('research_data', 'No research found.')
    
    # 2. Define the Role & Task
    sys_msg = SystemMessage(content="You are a Data Analyst.")
    
    task_msg = HumanMessage(content=f"""
    HERE IS THE RESEARCH DATA:
    {research_output}
    
    INSTRUCTIONS:
Analyze the research data and extract actionable insights.

YOUR ANALYSIS MUST INCLUDE:

1. *KEY THEMES & TRENDS* (5-7 major themes)
   - Identify recurring patterns across sources
   - Distinguish between established facts and emerging trends

2. *STATISTICS & DATA POINTS*
   - Extract all relevant numbers, percentages, market sizes, growth rates
   - Note the source for each statistic

3. *COMPETING VIEWPOINTS*
   - Identify areas of disagreement or debate
   - Present multiple perspectives on controversial points

4. *KNOWLEDGE GAPS*
   - What questions remain unanswered?
   - What areas need deeper research?

5. *TIMELINE & CONTEXT*
   - When are these trends expected to materialize?
   - What are the prerequisite conditions?

OUTPUT FORMAT: Use clear markdown with headers and bullet points.
Minimum 400 words of analytical depth.
    """)
    
    # 3. Invoke (Clean Context)
    response = llm.invoke([sys_msg, task_msg])
    clean_analysis = parse_gemini_output(response)
    
    print(f"   Analyst Generated: {len(clean_analysis)} chars") 
    
    return {"messages": [response], "analysis_data": clean_analysis}


def strategist_node(state: AgentState):
    print("👉 ENTERING: Strategist Node")
    
    # Get Inputs
    original_topic = state['messages'][0].content if state['messages'] else "the topic"
    research_data = state.get('research_data', 'No research found.')
    analysis_data = state.get('analysis_data', 'No analysis found.')
    
    sys_msg = SystemMessage(content="You are a Content Strategist.")
    
    # Explicitly feed the previous outputs
    prompt = f"""
    TOPIC: {original_topic}
    
    --- RESEARCH DATA ---
    {research_data}
    
    --- ANALYSIS DATA ---
    {analysis_data}
    
    INSTRUCTIONS:
    You are crafting a comprehensive market research report and content strategy document.

STRUCTURE YOUR OUTPUT AS FOLLOWS:

1. *CATCHY TITLE* 
   - Make it engaging, specific, and SEO-friendly
   - Include the main keyword/topic

2. *EXECUTIVE SUMMARY* (150 words)
   - Key findings in 3-4 bullet points
   - Main takeaway for decision-makers

3. *DETAILED SECTIONS* (Create 4-6 main sections based on the analysis)
   For each section:
   - Clear section header
   - 3-5 key talking points with supporting evidence
   - Include relevant statistics and data
   - Reference specific sources when making claims

4. *EMERGING OPPORTUNITIES*
   - What actionable insights can businesses/readers use?
   - Future predictions based on current trends

5. *CONCLUSION*
   - Synthesize the main findings
   - Provide 2-3 strategic recommendations

6. *SOURCES CITED*
   - List all referenced sources with URLs

TONE: Professional but accessible. Target audience is business strategists and decision-makers.
LENGTH: Minimum 800 words. Maximum 1500 words.
FORMAT: Use markdown with proper headers (##, ###), bullet points, and *bold* for emphasis.
    """
    
    task_msg = HumanMessage(content=prompt)
    
    response = llm.invoke([sys_msg, task_msg])
    clean_content = parse_gemini_output(response)
    
    return {"messages": [response], "final_report": clean_content}



# --- BUILD GRAPH ---
workflow = StateGraph(AgentState)
workflow.add_node("researcher", researcher_node)
workflow.add_node("tools", ToolNode(tools))
workflow.add_node("analyst", analyst_node)
workflow.add_node("strategist", strategist_node)

workflow.set_entry_point("researcher")

workflow.add_conditional_edges(
    "researcher",
    tools_condition,
    {"tools": "tools", "_end_": "analyst"}
)

workflow.add_edge("tools", "researcher")
workflow.add_edge("analyst", "strategist")
workflow.add_edge("strategist", END)

graph_app = workflow.compile()