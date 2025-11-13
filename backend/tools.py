import os
from dotenv import load_dotenv
from langchain_tavily import TavilySearch

load_dotenv()
# The Search tool is being used by the Senior Researcher Agent 
def get_search_tool():
    # Ensure the key exists
    if not os.getenv("TAVILY_API_KEY"):
        raise ValueError("TAVILY_API_KEY not found in .env file")
        
    return TavilySearch(
        max_results=5,               
        search_depth="advanced",     
        include_raw_content=True,    
        include_answer=True         
    )