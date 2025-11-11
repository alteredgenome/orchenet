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
    device_data = Column(JSON)  # Flexible field for vendor-specific data (renamed from metadata)

    # Connection credentials (encrypted in production)
    ssh_username = Column(String)
    ssh_password = Column(String)  # Should be encrypted
    ssh_key = Column(String)  # Path to SSH key or key content
    ssh_port = Column(Integer, default=22)

    # Vendor-specific connection info
    api_url = Column(String)  # For UniFi controller, etc.
    api_key = Column(String)  # API authentication
    api_token = Column(String)  # Alternative auth token

    # Check-in configuration
    check_in_method = Column(String)  # "http", "ssh", "controller"
    check_in_interval = Column(Integer, default=60)  # seconds

    # WireGuard VPN configuration
    wireguard_public_key = Column(String)  # Device's WireGuard public key
    wireguard_private_ip = Column(String)  # Assigned VPN IP address
    wireguard_enabled = Column(Integer, default=0)  # 0=disabled, 1=enabled
    wireguard_last_handshake = Column(DateTime, nullable=True)  # Last successful handshake
