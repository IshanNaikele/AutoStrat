from typing import Any,Optional,Dict
from pydantic import BaseModel

class ResearchRequest(BaseModel):
    topic:str

class ResearchResponse(BaseModel):
    task_id:str
    status:str
    message:str

class TaskStatus(BaseModel):
    task_id:str
    status:str
    result:Optional[Dict[str,Any]] = None