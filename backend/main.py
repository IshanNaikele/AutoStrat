from fastapi import FastAPI, BackgroundTasks, HTTPException
from langchain_core.messages import HumanMessage
import uuid

# Import from our other files
from backend.agents import graph_app
from backend.models import ResearchRequest, ResearchResponse, TaskStatus

app = FastAPI(title="AutoStrat API")

# In-memory database (Reset when server restarts)
# Structure: { "task_id": { "status": "processing", "result": None } }
TASKS = {}

def run_agent_task(task_id: str, topic: str):
    """
    The heavy lifting function running in the background.
    """
    print(f"--> Starting background task {task_id} for: {topic}")
    try:
        input_msg = HumanMessage(content=topic)
        
        # Invoke the LangGraph application
        # recursion_limit=20 prevents infinite search loops
        result = graph_app.invoke({"messages": [input_msg]}, config={"recursion_limit": 20})
        
        final_content = result.get("final_report", "Error: No report generated.")
        
        # Update DB
        TASKS[task_id] = {
            "status": "completed",
            "result": final_content
        }
        print(f"--> Task {task_id} COMPLETED.")
        
    except Exception as e:
        print(f"--> Task {task_id} FAILED: {e}")
        TASKS[task_id] = {
            "status": "failed",
            "result": str(e)
        }

@app.post("/generate-strategy", response_model=ResearchResponse)
async def generate_strategy(request: ResearchRequest, background_tasks: BackgroundTasks):
    """
    Endpoint 1: Starts the job and returns an ID immediately.
    """
    task_id = str(uuid.uuid4())
    
    # Create initial record
    TASKS[task_id] = {
        "status": "processing",
        "result": None
    }
    
    # Hand off to background
    background_tasks.add_task(run_agent_task, task_id, request.topic)
    
    return ResearchResponse(
        task_id=task_id,
        status="processing",
        message="Research started in background."
    )

@app.get("/status/{task_id}", response_model=TaskStatus)
async def get_status(task_id: str):
    """
    Endpoint 2: Frontend polls this to check progress.
    """
    task = TASKS.get(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task ID not found")
        
    return TaskStatus(
        task_id=task_id,
        status=task["status"],
        result=task["result"]
    )