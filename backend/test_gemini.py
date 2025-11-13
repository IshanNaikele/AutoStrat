import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
os.getenv("GOOGLE_API_KEY")
load_dotenv()

def test_gemini():
    print("Testing Gemini...")
    try:
        # Initialize the Model
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
        
        # Send a simple message
        response = llm.invoke("Hello, represent the number 5 as a roman numeral.")
        
        print("✅ Success! Gemini responded:")
        print(response.content)
    except Exception as e:
        print("❌ Error connecting to Gemini:")
        print(e)

if __name__ == "__main__":
    test_gemini()