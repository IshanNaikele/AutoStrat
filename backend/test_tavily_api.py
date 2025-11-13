import os
# 1. Load environment variables FIRST
from dotenv import load_dotenv
load_dotenv() 

# 2. Now import the tool (it will look for the key immediately upon use)
from langchain_community.tools.tavily_search import TavilySearchResults

def test_tavily():
    print("Testing Tavily Search...")
    
    # Debugging: Check if the key is actually loaded
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        print("❌ Error: TAVILY_API_KEY is missing from .env or not loaded.")
        return

    try:
        # Initialize the Tool
        tool = TavilySearchResults(max_results=1)
        
        # Run a search
        result = tool.invoke("What is the capital of France?")
        
        print("✅ Success! Tavily found data:")
        print(result)
    except Exception as e:
        print("❌ Error connecting to Tavily:")
        print(e)

if __name__ == "__main__":
    test_tavily()