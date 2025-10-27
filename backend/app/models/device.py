"""
Device database model
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from ..database import Base


class DeviceStatus(str, enum.Enum):
    """Device status enumeration"""
    ONLINE = "online"
    OFFLINE = "offline"
    PENDING = "pending"
    ERROR = "error"


class DeviceVendor(str, enum.Enum):
    """Supported device vendors"""
    MIKROTIK = "mikrotik"
    FORTINET = "fortinet"
    WATCHGUARD = "watchguard"
    UBIQUITI = "ubiquiti"


class Device(Base):
    """Device model representing a managed network device"""
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    vendor = Column(SQLEnum(DeviceVendor), nullable=False)
    model = Column(String)

    # Network information
    ip_address = Column(String)
    mac_address = Column(String)

    # Status
    status = Column(SQLEnum(DeviceStatus), default=DeviceStatus.PENDING)
    last_check_in = Column(DateTime, nullable=True)
    last_config_update = Column(DateTime, nullable=True)

    # Configuration
    current_config = Column(JSON, nullable=True)  # YAML config as JSON
    desired_config = Column(JSON, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Additional device info
    firmware_version = Column(String)
    serial_number = Column(String)
    metadata = Column(JSON)  # Flexible field for vendor-specific data
