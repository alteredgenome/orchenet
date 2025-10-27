"""
Pydantic schemas for Device API
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from ..models.device import DeviceStatus, DeviceVendor


class DeviceBase(BaseModel):
    """Base device schema"""
    name: str = Field(..., min_length=1, max_length=255)
    vendor: DeviceVendor
    model: Optional[str] = None
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None


class DeviceCreate(DeviceBase):
    """Schema for creating a device"""
    ssh_username: Optional[str] = None
    ssh_password: Optional[str] = None
    ssh_key: Optional[str] = None
    ssh_port: int = 22
    api_url: Optional[str] = None
    api_key: Optional[str] = None
    api_token: Optional[str] = None
    check_in_method: str = "http"  # "http", "ssh", "controller"
    check_in_interval: int = 60
    desired_config: Optional[Dict[str, Any]] = None


class DeviceUpdate(BaseModel):
    """Schema for updating a device"""
    name: Optional[str] = None
    model: Optional[str] = None
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    ssh_username: Optional[str] = None
    ssh_password: Optional[str] = None
    ssh_key: Optional[str] = None
    ssh_port: Optional[int] = None
    api_url: Optional[str] = None
    api_key: Optional[str] = None
    api_token: Optional[str] = None
    check_in_method: Optional[str] = None
    check_in_interval: Optional[int] = None
    desired_config: Optional[Dict[str, Any]] = None
    status: Optional[DeviceStatus] = None


class DeviceResponse(DeviceBase):
    """Schema for device responses"""
    id: int
    status: DeviceStatus
    last_check_in: Optional[datetime] = None
    last_config_update: Optional[datetime] = None
    firmware_version: Optional[str] = None
    serial_number: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    check_in_method: Optional[str] = None
    check_in_interval: int

    class Config:
        from_attributes = True


class DeviceWithConfig(DeviceResponse):
    """Device response including configuration"""
    current_config: Optional[Dict[str, Any]] = None
    desired_config: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class DeviceCheckIn(BaseModel):
    """Schema for device check-in"""
    device_id: Optional[int] = None
    device_name: Optional[str] = None
    vendor: Optional[DeviceVendor] = None
    serial_number: Optional[str] = None
    firmware_version: Optional[str] = None
    status_data: Optional[Dict[str, Any]] = None
