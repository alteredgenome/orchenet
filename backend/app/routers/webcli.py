"""
Web-based CLI API for remote device terminal access
Supports interactive SSH sessions via WebSocket
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict
import asyncio
import logging
import asyncssh

from ..database import get_db
from ..models.device import Device

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/webcli", tags=["webcli"])


class SSHSession:
    """Manages an interactive SSH session"""

    def __init__(self, device: Device):
        self.device = device
        self.connection = None
        self.process = None
        self.is_active = False

    async def connect(self):
        """Establish SSH connection and start interactive shell"""
        try:
            # Determine host (use WireGuard IP if available and enabled)
            host = self.device.wireguard_private_ip if self.device.wireguard_enabled else self.device.ip_address

            if not host:
                raise Exception("No IP address available for device")

            # Create SSH connection
            self.connection = await asyncssh.connect(
                host,
                port=self.device.ssh_port or 22,
                username=self.device.ssh_username,
                password=self.device.ssh_password,
                client_keys=[self.device.ssh_key] if self.device.ssh_key else None,
                known_hosts=None,
                connect_timeout=15,
            )

            # Start interactive shell
            self.process = await self.connection.create_process(term_type='xterm-256color')
            self.is_active = True

            logger.info(f"SSH session established to {self.device.name} ({host})")

        except Exception as e:
            logger.error(f"Failed to establish SSH session: {e}")
            raise

    async def send_input(self, data: str):
        """Send input to the SSH session"""
        if self.process and self.is_active:
            self.process.stdin.write(data)
            await self.process.stdin.drain()

    async def read_output(self, timeout: float = 0.1) -> str:
        """Read output from SSH session"""
        if not self.process or not self.is_active:
            return ""

        try:
            # Read with timeout to avoid blocking
            output = await asyncio.wait_for(
                self.process.stdout.read(4096),
                timeout=timeout
            )
            return output if output else ""
        except asyncio.TimeoutError:
            return ""
        except Exception as e:
            logger.error(f"Error reading output: {e}")
            return ""

    async def close(self):
        """Close the SSH session"""
        self.is_active = False

        if self.process:
            try:
                self.process.terminate()
                await self.process.wait_closed()
            except:
                pass

        if self.connection:
            try:
                self.connection.close()
                await self.connection.wait_closed()
            except:
                pass

        logger.info(f"SSH session closed for {self.device.name}")


# Active SSH sessions
active_sessions: Dict[str, SSHSession] = {}


@router.websocket("/ws/{device_id}")
async def websocket_cli(websocket: WebSocket, device_id: int):
    """
    WebSocket endpoint for interactive CLI access to a device.

    Protocol:
    - Client sends: {"type": "input", "data": "command\\n"}
    - Server sends: {"type": "output", "data": "response"}
    - Server sends: {"type": "error", "message": "error details"}
    - Client sends: {"type": "ping"} for keepalive
    - Server sends: {"type": "pong"}
    """
    await websocket.accept()
    session = None
    session_key = f"device_{device_id}"

    try:
        # Get device from database
        # Note: We can't use Depends(get_db) in WebSocket, so create session manually
        from ..database import SessionLocal
        db = SessionLocal()

        try:
            device = db.query(Device).filter(Device.id == device_id).first()
            if not device:
                await websocket.send_json({"type": "error", "message": "Device not found"})
                await websocket.close()
                return

            # Check if device has SSH credentials
            if not device.ssh_username:
                await websocket.send_json({"type": "error", "message": "Device has no SSH credentials configured"})
                await websocket.close()
                return

            # Create and connect SSH session
            session = SSHSession(device)
            await session.connect()

            active_sessions[session_key] = session

            # Send connection success message
            await websocket.send_json({
                "type": "connected",
                "message": f"Connected to {device.name}",
                "device": {
                    "id": device.id,
                    "name": device.name,
                    "vendor": device.vendor.value,
                    "model": device.model,
                }
            })

            # Start output reading task
            output_task = asyncio.create_task(read_and_send_output(websocket, session))

            # Main loop - receive input from WebSocket
            while session.is_active:
                try:
                    # Receive message from client
                    message = await asyncio.wait_for(websocket.receive_json(), timeout=0.1)

                    msg_type = message.get("type")

                    if msg_type == "input":
                        # Send input to SSH session
                        data = message.get("data", "")
                        await session.send_input(data)

                    elif msg_type == "ping":
                        # Respond to keepalive
                        await websocket.send_json({"type": "pong"})

                    elif msg_type == "resize":
                        # Handle terminal resize
                        width = message.get("width", 80)
                        height = message.get("height", 24)
                        if session.process:
                            try:
                                session.process.change_terminal_size(width, height)
                            except:
                                pass

                except asyncio.TimeoutError:
                    # No message received, continue loop
                    continue
                except WebSocketDisconnect:
                    logger.info(f"WebSocket disconnected for device {device_id}")
                    break

            # Cancel output task
            output_task.cancel()
            try:
                await output_task
            except asyncio.CancelledError:
                pass

        finally:
            db.close()

    except Exception as e:
        logger.error(f"WebSocket error for device {device_id}: {e}")
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except:
            pass

    finally:
        # Clean up session
        if session:
            await session.close()

        if session_key in active_sessions:
            del active_sessions[session_key]

        try:
            await websocket.close()
        except:
            pass


async def read_and_send_output(websocket: WebSocket, session: SSHSession):
    """
    Background task to continuously read SSH output and send to WebSocket.
    """
    try:
        while session.is_active:
            # Read output from SSH
            output = await session.read_output(timeout=0.05)

            if output:
                # Send to WebSocket client
                try:
                    await websocket.send_json({
                        "type": "output",
                        "data": output
                    })
                except:
                    # WebSocket closed
                    break

            # Small delay to avoid busy loop
            await asyncio.sleep(0.01)

    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.error(f"Error in output reader: {e}")


@router.get("/sessions")
async def get_active_sessions():
    """
    Get list of active CLI sessions.
    """
    sessions = []
    for key, session in active_sessions.items():
        sessions.append({
            "key": key,
            "device_name": session.device.name,
            "device_id": session.device.id,
            "is_active": session.is_active,
        })
    return {"sessions": sessions}


@router.delete("/sessions/{device_id}")
async def close_session(device_id: int):
    """
    Force close an active CLI session.
    """
    session_key = f"device_{device_id}"

    if session_key in active_sessions:
        session = active_sessions[session_key]
        await session.close()
        del active_sessions[session_key]
        return {"message": f"Session closed for device {device_id}"}
    else:
        raise HTTPException(status_code=404, detail="No active session found")
