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
        max_results=5,              # 5 High-quality results is better than 10 low-quality ones
        search_depth="advanced",    # <--- Forces Tavily to scrape deeper
        include_raw_content=True,   # <--- Fetches the FULL article text, not just a snippet
        include_answer=True         # <--- Asks Tavily to generate a direct answer too)
    )