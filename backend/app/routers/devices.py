"""
Device management API endpoints
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.device import Device, DeviceStatus
from ..schemas.device import (
    DeviceCreate,
    DeviceUpdate,
    DeviceResponse,
    DeviceWithConfig
)

router = APIRouter(prefix="/api/devices", tags=["devices"])


@router.post("/", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
async def create_device(device: DeviceCreate, db: Session = Depends(get_db)):
    """
    Create a new device.
    """
    # Check if device with same name already exists
    existing = db.query(Device).filter(Device.name == device.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Device with name '{device.name}' already exists"
        )

    # Create new device
    db_device = Device(
        name=device.name,
        vendor=device.vendor,
        model=device.model,
        ip_address=device.ip_address,
        mac_address=device.mac_address,
        ssh_username=device.ssh_username,
        ssh_password=device.ssh_password,  # TODO: Encrypt in production
        ssh_key=device.ssh_key,
        ssh_port=device.ssh_port,
        api_url=device.api_url,
        api_key=device.api_key,
        api_token=device.api_token,
        check_in_method=device.check_in_method,
        check_in_interval=device.check_in_interval,
        desired_config=device.desired_config,
        status=DeviceStatus.PENDING
    )

    db.add(db_device)
    db.commit()
    db.refresh(db_device)

    return db_device


@router.get("/", response_model=List[DeviceResponse])
async def list_devices(
    vendor: Optional[str] = None,
    status: Optional[DeviceStatus] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all devices with optional filtering.
    """
    query = db.query(Device)

    if vendor:
        query = query.filter(Device.vendor == vendor)
    if status:
        query = query.filter(Device.status == status)

    devices = query.offset(skip).limit(limit).all()
    return devices


@router.get("/{device_id}", response_model=DeviceWithConfig)
async def get_device(device_id: int, db: Session = Depends(get_db)):
    """
    Get a specific device by ID, including configuration.
    """
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with id {device_id} not found"
        )
    return device


@router.put("/{device_id}", response_model=DeviceResponse)
async def update_device(
    device_id: int,
    device_update: DeviceUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a device.
    """
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with id {device_id} not found"
        )

    # Update fields
    update_data = device_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(device, field, value)

    device.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(device)

    return device


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(device_id: int, db: Session = Depends(get_db)):
    """
    Delete a device.
    """
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with id {device_id} not found"
        )

    db.delete(device)
    db.commit()
    return None


@router.put("/{device_id}/config", response_model=DeviceResponse)
async def update_device_config(
    device_id: int,
    config: dict,
    db: Session = Depends(get_db)
):
    """
    Update device configuration (sets desired_config).
    This will trigger a configuration push on next check-in.
    """
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with id {device_id} not found"
        )

    device.desired_config = config
    device.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(device)

    return device
