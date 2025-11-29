import streamlit as st
import requests
import time
import os

# Setup page config
st.set_page_config(
    page_title="AutoStrat | AI Research Agent",
    page_icon="🚀",
    layout="wide"
)

# --- CONSTANTS ---
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# --- CUSTOM STYLING ---
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stTextInput>div>div>input {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        font-size: 16px;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #FF4B4B 0%, #C73636 100%);
        color: white;
        font-weight: bold;
        padding: 15px;
        border-radius: 10px;
        border: none;
        font-size: 18px;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.4);
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 75, 75, 0.6);
    }
    .report-container {
        background-color: white;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        margin-top: 20px;
    }
    .stage-indicator {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        margin: 20px 0;
    }
    .info-box {
        background-color: #e7f3ff;
        border-left: 4px solid #2196F3;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("<h1 style='text-align: center; color: white;'>🚀 AutoStrat</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: white;'>Autonomous AI Market Research Agent</h3>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- DESCRIPTION ---
with st.container():
    st.markdown("""
    <div class='info-box'>
    <strong>How it works:</strong><br>
    1. 🔍 <strong>Senior Researcher</strong> searches 10-15 sources using Tavily Search<br>
    2. 📊 <strong>Data Analyst</strong> extracts trends, statistics, and insights<br>
    3. ✍️ <strong>Content Strategist</strong> creates a comprehensive market report<br><br>
    <em>⏱️ Typical processing time: 30-90 seconds</em>
    </div>
    """, unsafe_allow_html=True)

# --- INPUT SECTION ---
st.markdown("<br>", unsafe_allow_html=True)
topic = st.text_input(
    "Enter your research topic:",
    placeholder="e.g., The future of quantum computing in finance",
    help="Be specific for best results. Examples: 'AI in healthcare 2025', 'Sustainable energy trends'"
)

# --- SESSION STATE INITIALIZATION ---
if "task_id" not in st.session_state:
    st.session_state.task_id = None
if "report_data" not in st.session_state:
    st.session_state.report_data = None
if "processing" not in st.session_state:
    st.session_state.processing = False

# --- MAIN BUTTON ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    generate_button = st.button("🚀 Generate Strategy Report", disabled=st.session_state.processing)

# --- PROCESSING LOGIC ---
if generate_button:
    if not topic or len(topic.strip()) < 5:
        st.markdown("<div class='warning-box'>⚠️ Please enter a topic (minimum 5 characters)</div>", unsafe_allow_html=True)
    else:
        st.session_state.processing = True
        st.session_state.report_data = None
        
        try:
            # 1. START THE TASK
            with st.spinner("🔄 Deploying AI agents..."):
                response = requests.post(
                    f"{BACKEND_URL}/generate-strategy",
                    json={"topic": topic.strip()},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.task_id = data["task_id"]
                    
                    st.markdown(f"""
                    <div class='success-box'>
                    ✅ <strong>Task Created Successfully!</strong><br>
                    Task ID: <code>{st.session_state.task_id[:8]}...</code>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error(f"❌ Failed to start task: {response.text}")
                    st.session_state.processing = False
                    st.stop()

            # 2. POLL FOR RESULTS WITH PROGRESS
            if st.session_state.task_id:
                progress_bar = st.progress(0)
                status_container = st.empty()
                stage_container = st.empty()
                
                poll_count = 0
                max_polls = 60  # 60 polls × 3 seconds = 3 minutes max
                
                while poll_count < max_polls:
                    try:
                        # Check status
                        status_res = requests.get(
                            f"{BACKEND_URL}/status/{st.session_state.task_id}",
                            timeout=5
                        )
                        status_data = status_res.json()
                        status = status_data["status"]
                        
                        # Update progress (simulated)
                        progress = min(95, (poll_count / max_polls) * 100)
                        progress_bar.progress(int(progress))
                        
                        if status == "processing":
                            # Show animated status
                            dots = "." * ((poll_count % 3) + 1)
                            stage_container.markdown(f"""
                            <div class='stage-indicator'>
                            🔄 Multi-Agent System Processing{dots}<br>
                            <small>Researcher → Analyst → Strategist</small>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            status_container.info(f"⏳ Processing... ({poll_count * 3}s elapsed)")
                            time.sleep(3)
                            poll_count += 1
                            
                        elif status == "completed":
                            progress_bar.progress(100)
                            stage_container.markdown("""
                            <div class='stage-indicator' style='background: linear-gradient(135deg, #28a745 0%, #20c997 100%);'>
                            ✅ Report Generation Complete!
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.session_state.report_data = status_data["result"]
                            st.session_state.processing = False
                            status_container.success("✨ Your comprehensive report is ready!")
                            time.sleep(1)
                            st.rerun()
                            
                        elif status == "failed":
                            progress_bar.empty()
                            error_msg = status_data.get("result", {}).get("error", "Unknown error")
                            st.error(f"❌ Task Failed: {error_msg}")
                            st.session_state.processing = False
                            break
                            
                    except requests.exceptions.Timeout:
                        status_container.warning("⚠️ Connection timeout. Retrying...")
                        time.sleep(2)
                        poll_count += 1
                        continue
                        
                    except Exception as e:
                        st.error(f"❌ Error checking status: {e}")
                        st.session_state.processing = False
                        break
                
                if poll_count >= max_polls:
                    st.error("⏰ Task timeout (3 minutes exceeded). Please try again with a simpler topic.")
                    st.session_state.processing = False
        
        except requests.exceptions.ConnectionError:
            st.error(f"❌ Cannot connect to backend at {BACKEND_URL}. Is the server running?")
            st.markdown("""
            <div class='warning-box'>
            <strong>To start the backend:</strong><br>
            <code>cd backend && uvicorn main:app --reload</code>
            </div>
            """, unsafe_allow_html=True)
            st.session_state.processing = False
            
        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")
            st.session_state.processing = False

# --- DISPLAY RESULTS ---
if st.session_state.report_data and not st.session_state.processing:
    data = st.session_state.report_data
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    
    # MAIN REPORT
    st.markdown("<div class='report-container'>", unsafe_allow_html=True)
    st.markdown(f"## 📊 Market Research Report: {topic}")
    st.markdown(data.get("report", "No report generated"))
    st.markdown("</div>", unsafe_allow_html=True)
    
    # DOWNLOAD BUTTON
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.download_button(
            label="📥 Download Report (Markdown)",
            data=data.get("report", ""),
            file_name=f"autostrat_report_{topic[:30]}.md",
            mime="text/markdown",
            use_container_width=True
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # DEVELOPER VIEW (COLLAPSIBLE)
    st.markdown("---")
    st.subheader("🔍 Agent Pipeline Transparency")
    st.info("Expand sections below to see what each agent produced")
    
    with st.expander("🌐 **Step 1: Researcher's Data Gathering**", expanded=False):
        st.markdown("**Raw search results and source summaries:**")
        research_data = data.get("research", "No research data found")
        st.markdown(research_data)
        st.caption(f"📏 Length: {len(research_data)} characters")
    
    with st.expander("📊 **Step 2: Analyst's Insights**", expanded=False):
        st.markdown("**Structured analysis of trends and patterns:**")
        analysis_data = data.get("analysis", "No analysis found")
        st.markdown(analysis_data)
        st.caption(f"📏 Length: {len(analysis_data)} characters")
    
    with st.expander("✍️ **Step 3: Strategist's Final Report**", expanded=False):
        st.markdown("**Complete content strategy document:**")
        st.markdown(data.get("report", "No report found"))
    
    # RESET BUTTON
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Generate New Report"):
        st.session_state.task_id = None
        st.session_state.report_data = None
        st.session_state.processing = False
        st.rerun()

# --- FOOTER ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: white;'>
<small>
Powered by LangGraph, Google Gemini 2.5 Flash & Tavily Search<br>
Built with FastAPI + Streamlit | Multi-Agent Autonomous Research System
</small>
</div>
""", unsafe_allow_html=True)