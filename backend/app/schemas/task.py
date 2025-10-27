"""
Pydantic schemas for Task API
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel
from ..models.task import TaskStatus, TaskType


class TaskBase(BaseModel):
    """Base task schema"""
    device_id: int
    task_type: TaskType
    payload: Optional[Dict[str, Any]] = None


class TaskCreate(TaskBase):
    """Schema for creating a task"""
    max_retries: int = 3


class TaskUpdate(BaseModel):
    """Schema for updating a task"""
    status: Optional[TaskStatus] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class TaskResponse(TaskBase):
    """Schema for task responses"""
    id: int
    status: TaskStatus
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int
    max_retries: int

    class Config:
        from_attributes = True
