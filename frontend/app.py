import streamlit as st
import requests
import time
import os

# Setup page config
st.set_page_config(
    page_title="AutoStrat | AI Research Agent",
    page_icon="🚀",
    layout="centered"
)

# --- CONSTANTS ---
# If running locally, use localhost. If deployed, use the URL.
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# --- STYLING ---
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
    }
    .report-box {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- UI HEADER ---
st.title("🚀 AutoStrat: Autonomous Market Researcher")
st.markdown("Enter a topic, and our **AI Agent Team** (Researcher, Analyst, Strategist) will generate a comprehensive report for you.")

# --- INPUT AREA ---
topic = st.text_input("Enter a research topic:", placeholder="e.g., The future of AI in Healthcare 2025")

# --- STATE MANAGEMENT ---
if "task_id" not in st.session_state:
    st.session_state.task_id = None
if "report" not in st.session_state:
    st.session_state.report = None

# --- MAIN LOGIC ---
if st.button("Generate Strategy"):
    if not topic:
        st.warning("Please enter a topic first.")
    else:
        try:
            # 1. Start the Task
            with st.spinner("Initializing Agents..."):
                response = requests.post(f"{BACKEND_URL}/generate-strategy", json={"topic": topic})
                
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.task_id = data["task_id"]
                    st.success(f"Agents Deployed! Task ID: {st.session_state.task_id}")
                else:
                    st.error(f"Failed to start: {response.text}")

            # 2. Poll for Results
            if st.session_state.task_id:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                while True:
                    # Check status
                    status_res = requests.get(f"{BACKEND_URL}/status/{st.session_state.task_id}")
                    status_data = status_res.json()
                    status = status_data["status"]
                    
                    if status == "processing":
                        status_text.text("🕵️ Agents are researching and analyzing... (This takes 30-60s)")
                        # Simple animation logic
                        time.sleep(4) 
                    elif status == "completed":
                        progress_bar.progress(100)
                        status_text.text("✅ Report Ready!")
                        st.session_state.report = status_data["result"]
                        break
                    elif status == "failed":
                        st.error(f"Task Failed: {status_data['result']}")
                        break
        
        except Exception as e:
            st.error(f"Connection Error: {e}. Is the Backend running?")

# --- DISPLAY RESULT ---
if st.session_state.report:
    st.markdown("---")
    st.subheader(f"📊 Strategy Report: {topic}")
    
    # Render the Markdown nicely
    st.markdown(f"""
    <div class="report-box">
        {st.session_state.report}
    </div>
    """, unsafe_allow_html=True)
    
    # Download Button
    st.download_button(
        label="📥 Download Report",
        data=st.session_state.report,
        file_name=f"strategy_report_{topic.replace(' ', '_')}.md",
        mime="text/markdown"
    )