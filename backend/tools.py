import os 
from dotenv import load_dotenv
from langchain_tavily import TavilySearch
load_dotenv()

TAVILY_API_KEY=os.getenv("TAVILY_API_KEY")

print("TAVILY_API_KEY :",TAVILY_API_KEY[:4])

if not TAVILY_API_KEY :
    print("You have not putted TAVILY_API_KEY in the .env file .")

def get_search_tool():
    return TavilySearch(
        max_results=5,
        search_depth="advanced",
        include_raw_content=True,
        include_answer=True  
    )

 
 