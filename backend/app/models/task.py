"""
Task database model for device operations
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
import enum

from ..database import Base


class TaskStatus(str, enum.Enum):
    """Task status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(str, enum.Enum):
    """Task type enumeration"""
    CONFIG_UPDATE = "config_update"
    FIRMWARE_UPDATE = "firmware_update"
    COMMAND_EXECUTION = "command_execution"
    STATUS_COLLECTION = "status_collection"


class Task(Base):
    """Task model for operations to be executed on devices"""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)

    task_type = Column(SQLEnum(TaskType), nullable=False)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING)

    # Task details
    payload = Column(JSON)  # Task-specific data
    result = Column(JSON, nullable=True)  # Task execution result
    error_message = Column(String, nullable=True)

    # Timing
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Retry logic
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
