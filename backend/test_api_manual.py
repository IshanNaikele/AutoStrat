import requests
import time

# Base URL of your local API
BASE_URL = "http://127.0.0.1:8000"

def test_workflow():
    print("🧪 Testing AutoStrat API...")
    
    # 1. Define the topic
    topic = "Latest developments in Solid State Batteries 2025"
    
    # 2. Start the Task (POST)
    print(f"1. Sending request for: '{topic}'")
    start_response = requests.post(
        f"{BASE_URL}/generate-strategy", 
        json={"topic": topic}
    )
    
    if start_response.status_code != 200:
        print("❌ Failed to start task:", start_response.text)
        return

    data = start_response.json()
    task_id = data["task_id"]
    print(f"✅ Task Started! ID: {task_id}")
    
    # 3. Poll for Status (GET)
    print("2. Polling for results (this takes 30-60s)...")
    
    while True:
        status_response = requests.get(f"{BASE_URL}/status/{task_id}")
        status_data = status_response.json()
        
        status = status_data["status"]
        
        if status == "completed":
            print("\n🎉 SUCCESS! Report Generated:")
            print("="*50)
            print(status_data["result"])
            print("="*50)
            break
            
        elif status == "failed":
            print("\n❌ Task Failed:", status_data["result"])
            break
            
        else:
            # Still processing
            print(f"   ... Status: {status}")
            time.sleep(5) # Wait 5 seconds before checking again

if __name__ == "__main__":
    test_workflow()