from pydantic import BaseModel
from typing import Optional

from enum import Enum

class TaskStatus(str, Enum):
    pending = 'pending'
    completed = 'completed'


class CreateTask(BaseModel):
    task_name: str
    task_description: str
    task_status: TaskStatus = TaskStatus.pending


class UpdateTask(BaseModel):
    task_name: Optional[str] = None
    task_description: Optional[str] = None
    task_status: Optional[TaskStatus] = None




