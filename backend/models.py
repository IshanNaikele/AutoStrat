from pydantic import BaseModel
from typing import Optional, Dict, Any # <-- Import Any

class ResearchRequest(BaseModel):
    topic: str

class ResearchResponse(BaseModel):
    task_id: str
    status: str
    message: str

class TaskStatus(BaseModel):
    task_id: str
    status: str
    # CHANGED: Result is now a Dictionary, not just a string
    result: Optional[Dict[str, Any]] = None