"""
Device check-in API endpoints
Handles periodic device check-ins and returns pending tasks.
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.device import Device, DeviceStatus
from ..models.task import Task, TaskStatus
from ..schemas.device import DeviceCheckIn
from ..schemas.task import TaskResponse

router = APIRouter(prefix="/api/checkin", tags=["checkin"])


@router.post("/", response_model=List[TaskResponse])
async def device_checkin(
    checkin_data: DeviceCheckIn,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Device check-in endpoint.

    Devices call this endpoint to:
    1. Report their status
    2. Update last check-in time
    3. Retrieve pending tasks

    Authentication via Authorization header (Bearer token or device-specific key).
    """
    # Find device by ID, name, or serial number
    device = None

    if checkin_data.device_id:
        device = db.query(Device).filter(Device.id == checkin_data.device_id).first()
    elif checkin_data.device_name:
        device = db.query(Device).filter(Device.name == checkin_data.device_name).first()
    elif checkin_data.serial_number:
        device = db.query(Device).filter(Device.serial_number == checkin_data.serial_number).first()

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    # TODO: Verify authorization token matches device

    # Update device status
    device.last_check_in = datetime.utcnow()
    device.status = DeviceStatus.ONLINE

    # Update firmware version if provided
    if checkin_data.firmware_version:
        device.firmware_version = checkin_data.firmware_version

    # Update status data in metadata
    if checkin_data.status_data:
        if not device.device_data:
            device.device_data = {}
        device.device_data["last_status"] = checkin_data.status_data
        device.device_data["last_status_time"] = datetime.utcnow().isoformat()

    db.commit()

    # Get pending tasks for this device
    pending_tasks = db.query(Task).filter(
        Task.device_id == device.id,
        Task.status == TaskStatus.PENDING
    ).order_by(Task.created_at).all()

    # Mark tasks as in progress
    for task in pending_tasks:
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.utcnow()

    db.commit()

    return pending_tasks


@router.post("/result/{task_id}")
async def submit_task_result(
    task_id: int,
    result: dict,
    success: bool = True,
    error_message: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Submit task execution result.

    Called by devices after executing a task to report the outcome.
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    # Update task with result
    task.result = result
    task.completed_at = datetime.utcnow()

    if success:
        task.status = TaskStatus.COMPLETED
    else:
        task.error_message = error_message

        # Retry logic
        if task.retry_count < task.max_retries:
            task.status = TaskStatus.PENDING
            task.retry_count += 1
            task.started_at = None
            task.completed_at = None
        else:
            task.status = TaskStatus.FAILED

    db.commit()

    return {"status": "success", "task_id": task_id}


@router.get("/pending/{device_id}", response_model=List[TaskResponse])
async def get_pending_tasks(device_id: int, db: Session = Depends(get_db)):
    """
    Get pending tasks for a device (alternative to check-in endpoint).
    """
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device {device_id} not found"
        )

    pending_tasks = db.query(Task).filter(
        Task.device_id == device_id,
        Task.status == TaskStatus.PENDING
    ).order_by(Task.created_at).all()

    return pending_tasks
