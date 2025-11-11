"""
WireGuard VPN Management API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

from ..database import get_db
from ..models.device import Device
from ..services.wireguard_manager import wireguard_manager, WireGuardError
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/wireguard", tags=["wireguard"])


# Request/Response Models
class WireGuardServerSetup(BaseModel):
    """Request model for server setup"""
    server_private_key: Optional[str] = None


class WireGuardServerInfo(BaseModel):
    """Response model for server info"""
    server_public_key: str
    server_ip: str
    listen_port: int
    interface: str


class WireGuardPeerRequest(BaseModel):
    """Request model for enabling WireGuard on a device"""
    device_id: int
    public_key: Optional[str] = None  # If None, will be generated


class WireGuardPeerInfo(BaseModel):
    """Response model for peer info"""
    device_id: int
    device_name: str
    public_key: str
    private_key: Optional[str]  # Only returned on creation
    private_ip: str
    enabled: bool
    last_handshake: Optional[datetime]
    client_config: Optional[str]  # WireGuard config for device


class WireGuardPeerStatus(BaseModel):
    """Response model for peer status"""
    device_id: int
    device_name: str
    public_key: str
    private_ip: str
    endpoint: Optional[str]
    last_handshake: Optional[int]
    rx_bytes: int
    tx_bytes: int


@router.post("/setup", response_model=WireGuardServerInfo)
async def setup_wireguard_server(
    setup: WireGuardServerSetup,
    db: Session = Depends(get_db)
):
    """
    Set up WireGuard server configuration.
    This should be run once during initial deployment.
    """
    try:
        result = await wireguard_manager.setup_server(setup.server_private_key)

        return WireGuardServerInfo(
            server_public_key=result["server_public_key"],
            server_ip=result["server_ip"],
            listen_port=result["listen_port"],
            interface=wireguard_manager.interface,
        )

    except WireGuardError as e:
        logger.error(f"WireGuard setup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info", response_model=WireGuardServerInfo)
async def get_wireguard_info():
    """
    Get WireGuard server information.
    """
    try:
        # Read server public key from config
        config_content = wireguard_manager.config_file.read_text()

        # Extract private key and derive public key
        import re
        match = re.search(r'PrivateKey = (.+)', config_content)
        if not match:
            raise HTTPException(status_code=404, detail="WireGuard not configured")

        private_key = match.group(1).strip()
        from ..services.wireguard_manager import WireGuardManager
        wg = WireGuardManager()
        public_key = await wg._run_command(f"echo '{private_key}' | wg pubkey")

        return WireGuardServerInfo(
            server_public_key=public_key,
            server_ip=wireguard_manager.server_ip,
            listen_port=wireguard_manager.listen_port,
            interface=wireguard_manager.interface,
        )

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="WireGuard not configured. Run /setup first.")
    except Exception as e:
        logger.error(f"Failed to get WireGuard info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/peers", response_model=WireGuardPeerInfo)
async def enable_wireguard_for_device(
    peer_request: WireGuardPeerRequest,
    db: Session = Depends(get_db),
    server_endpoint: Optional[str] = None,
):
    """
    Enable WireGuard VPN for a device.
    Generates keys, allocates IP, and creates peer configuration.
    """
    try:
        # Get device
        device = db.query(Device).filter(Device.id == peer_request.device_id).first()
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")

        # Generate or use provided public key
        if peer_request.public_key:
            public_key = peer_request.public_key
            private_key = None
        else:
            private_key, public_key = await wireguard_manager.generate_keypair()

        # Allocate IP address
        used_ips = [
            d.wireguard_private_ip
            for d in db.query(Device).filter(Device.wireguard_private_ip.isnot(None)).all()
        ]

        allocated_ip = await wireguard_manager.allocate_ip(used_ips)
        if not allocated_ip:
            raise HTTPException(status_code=500, detail="No available IP addresses in VPN subnet")

        # Add peer to WireGuard
        await wireguard_manager.add_peer(
            peer_name=device.name,
            peer_public_key=public_key,
            peer_ip=allocated_ip,
        )

        # Update device record
        device.wireguard_public_key = public_key
        device.wireguard_private_ip = allocated_ip
        device.wireguard_enabled = 1
        device.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(device)

        # Generate client config
        server_info = await get_wireguard_info()

        if not server_endpoint:
            # Try to determine server endpoint (you may want to make this configurable)
            server_endpoint = f"YOUR_SERVER_IP:{server_info.listen_port}"

        client_config = None
        if private_key:
            client_config = await wireguard_manager.generate_peer_config(
                peer_private_key=private_key,
                peer_ip=allocated_ip,
                server_public_key=server_info.server_public_key,
                server_endpoint=server_endpoint,
                dns="1.1.1.1",
            )

        return WireGuardPeerInfo(
            device_id=device.id,
            device_name=device.name,
            public_key=public_key,
            private_key=private_key,
            private_ip=allocated_ip,
            enabled=True,
            last_handshake=device.wireguard_last_handshake,
            client_config=client_config,
        )

    except WireGuardError as e:
        logger.error(f"Failed to enable WireGuard for device: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/peers/{device_id}")
async def disable_wireguard_for_device(
    device_id: int,
    db: Session = Depends(get_db)
):
    """
    Disable WireGuard VPN for a device.
    Removes peer from WireGuard configuration.
    """
    try:
        device = db.query(Device).filter(Device.id == device_id).first()
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")

        if not device.wireguard_enabled:
            raise HTTPException(status_code=400, detail="WireGuard not enabled for this device")

        # Remove peer from WireGuard
        await wireguard_manager.remove_peer(device.wireguard_public_key)

        # Update device record
        device.wireguard_enabled = 0
        device.wireguard_last_handshake = None
        device.updated_at = datetime.utcnow()
        # Keep public_key and private_ip for reference
        db.commit()

        return {"message": f"WireGuard disabled for device {device.name}"}

    except WireGuardError as e:
        logger.error(f"Failed to disable WireGuard: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/peers", response_model=List[WireGuardPeerStatus])
async def get_all_wireguard_peers(db: Session = Depends(get_db)):
    """
    Get status of all WireGuard peers.
    """
    try:
        # Get all devices with WireGuard enabled
        devices = db.query(Device).filter(Device.wireguard_enabled == 1).all()

        # Get peer statuses from WireGuard
        wg_peers = await wireguard_manager.get_all_peers()
        wg_peer_map = {p["public_key"]: p for p in wg_peers}

        peer_statuses = []
        for device in devices:
            wg_status = wg_peer_map.get(device.wireguard_public_key, {})

            peer_statuses.append(WireGuardPeerStatus(
                device_id=device.id,
                device_name=device.name,
                public_key=device.wireguard_public_key,
                private_ip=device.wireguard_private_ip,
                endpoint=wg_status.get("endpoint"),
                last_handshake=wg_status.get("last_handshake"),
                rx_bytes=wg_status.get("rx_bytes", 0),
                tx_bytes=wg_status.get("tx_bytes", 0),
            ))

        return peer_statuses

    except Exception as e:
        logger.error(f"Failed to get peer statuses: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/peers/{device_id}", response_model=WireGuardPeerStatus)
async def get_wireguard_peer_status(
    device_id: int,
    db: Session = Depends(get_db)
):
    """
    Get WireGuard status for a specific device.
    """
    try:
        device = db.query(Device).filter(Device.id == device_id).first()
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")

        if not device.wireguard_enabled:
            raise HTTPException(status_code=400, detail="WireGuard not enabled for this device")

        # Get peer status from WireGuard
        wg_status = await wireguard_manager.get_peer_status(device.wireguard_public_key)

        if not wg_status:
            wg_status = {}

        # Update last handshake in database if changed
        if wg_status.get("last_handshake"):
            handshake_time = datetime.fromtimestamp(wg_status["last_handshake"])
            if device.wireguard_last_handshake != handshake_time:
                device.wireguard_last_handshake = handshake_time
                db.commit()

        return WireGuardPeerStatus(
            device_id=device.id,
            device_name=device.name,
            public_key=device.wireguard_public_key,
            private_ip=device.wireguard_private_ip,
            endpoint=wg_status.get("endpoint"),
            last_handshake=wg_status.get("last_handshake"),
            rx_bytes=wg_status.get("rx_bytes", 0),
            tx_bytes=wg_status.get("tx_bytes", 0),
        )

    except Exception as e:
        logger.error(f"Failed to get peer status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/restart")
async def restart_wireguard():
    """
    Restart WireGuard interface.
    Useful after configuration changes.
    """
    try:
        success = await wireguard_manager.restart_interface()
        if success:
            return {"message": "WireGuard interface restarted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to restart WireGuard")
    except Exception as e:
        logger.error(f"Failed to restart WireGuard: {e}")
        raise HTTPException(status_code=500, detail=str(e))
