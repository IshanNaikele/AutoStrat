from pydantic import BaseModel
from typing import Optional, Dict, Any

class ResearchRequest(BaseModel):
    topic: str

class ResearchResponse(BaseModel):
    task_id: str
    status: str
    message: str

class TaskStatus(BaseModel):
    task_id: str
    status: str # 'processing', 'completed', 'failed'
    result: Optional[str] = None
    