import os
import json
from dotenv import load_dotenv
from backend.tools import get_search_tool # Ensure this path matches your folder structure
 
load_dotenv()

def test_search_quality():
    print("\n" + "="*80)
    print("🧪 TESTING SEARCH TOOL OUTPUT QUALITY")
    print("="*80)
    
    # 1. Initialize
    try:
        search_tool = get_search_tool()
        print("✅ Search tool initialized.")
    except Exception as e:
        print(f"❌ Error initializing tool: {e}")
        return

    # 2. Define Query
    query = "future of quantum computing in finance 2025"
    print(f"🔎 Searching for: '{query}'")
    print("-" * 80)

    try:
        # 3. Run Search
        # Note: We pass the string directly or a dict depending on the specific wrapper version. 
        # The safest way with the new tool is usually just the query string or {"query": ...}
        response = search_tool.invoke({"query": query})

        # 4. Normalize the Output (The Fix)
        # The new TavilySearch returns a DICT. The actual articles are in response['results']
        if isinstance(response, dict) and 'results' in response:
            articles = response['results']
        elif isinstance(response, list):
            articles = response
        else:
            print("⚠️ Unknown response format.")
            print(response)
            return

        count = len(articles)
        print(f"📊 STATUS: Found {count} articles.\n")

        # 5. Print Readable Details
        print("📄 ARTICLE DETAILS:")
        for i, article in enumerate(articles, 1):
            print(f"\n[{i}] {article.get('title', 'No Title')}")
            print(f"    🔗 URL: {article.get('url', 'No URL')}")
            
            # Clean up content preview
            content = article.get('content', 'No Content')
            # Remove newlines for cleaner display
            clean_content = content.replace('\n', ' ')[:] 
            print(f"    📝 Content: {clean_content}...")
            
            # Check score if available
            if 'score' in article:
                print(f"    Cw Relevance Score: {article['score']}")

        # 6. Analysis
        print("\n" + "="*80)
        print("📈 QUALITY ANALYSIS")
        print("="*80)
        
        if count < 5:
            print(f"⚠️  WARNING: Only {count} results returned.")
            print("   (Tavily sometimes filters duplicates automatically, even if you ask for 10)")
        else:
            print(f"✅ SUCCESS: Received {count} high-quality results.")

        # Check for modern dates (2024/2025)
        modern_content = any("2024" in str(a) or "2025" in str(a) for a in articles)
        if modern_content:
            print("✅ TIMELINESS: Data contains references to 2024/2025.")
        else:
            print("⚠️  TIMELINESS: No recent dates found in snippets. Check search query.")

    except Exception as e:
        print(f"❌ EXECUTION ERROR: {e}")

if __name__ == "__main__":
    test_search_quality()