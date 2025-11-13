"""
Device provisioning API endpoints
Generates provisioning scripts for devices
"""
import subprocess
import os
from typing import Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..database import get_db
from ..models.device import Device

router = APIRouter(prefix="/api/devices", tags=["provisioning"])


class ProvisionScriptRequest(BaseModel):
    device_id: int
    mac_address: str


class ProvisionScriptResponse(BaseModel):
    script: str
    filename: str
    wireguard_info: Dict


def generate_wireguard_keypair():
    """Generate a WireGuard key pair using wg command"""
    try:
        # Generate private key
        private_key = subprocess.check_output(["wg", "genkey"], text=True).strip()

        # Generate public key from private key
        public_key = subprocess.check_output(
            ["wg", "pubkey"],
            input=private_key,
            text=True
        ).strip()

        return private_key, public_key
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="WireGuard tools not installed on server"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating WireGuard keys: {str(e)}"
        )


def format_mac_for_tunnel(mac_address: str) -> str:
    """Format MAC address for tunnel naming: XX:XX:XX:XX:XX:XX -> xx_xx_xx_xx_xx_xx"""
    return mac_address.replace(':', '_').lower()


def generate_mikrotik_provisioning_script(
    device_name: str,
    mac_address: str,
    server_ip: str,
    server_port: int,
    server_public_key: str,
    device_private_key: str,
    device_vpn_ip: str,
    api_url: str
) -> str:
    """Generate MikroTik provisioning script"""

    tunnel_name = f"orcatun_{format_mac_for_tunnel(mac_address)}"

    # Use format() instead of f-string to avoid brace escaping issues
    script = '''# OrcheNet MikroTik Provisioning Script
# Generated automatically for device: {device_name}
# MAC Address: {mac_address}
# WireGuard Tunnel: {tunnel_name}

# Variables
:local orchenetServer "{server_ip}"
:local orchenetPort "{server_port}"
:local orchenetServerPublicKey "{server_public_key}"
:local devicePrivateKey "{device_private_key}"
:local deviceVpnIp "{device_vpn_ip}/32"
:local apiUrl "{api_url}/api/checkin"
:local tunnelName "{tunnel_name}"
:local sshUser "orchenet"
:local sshPassword "CHANGE_ME_IMMEDIATELY"

:put "===== OrcheNet Provisioning Script ====="
:put "Device: {device_name}"
:put "Tunnel: $tunnelName"
:put "Server: $orchenetServer"
:put ""

# 1. Configure WireGuard Interface
:put "Step 1: Configuring WireGuard interface..."
:do {{
    /interface wireguard add name=$tunnelName private-key=$devicePrivateKey listen-port=51821 comment="OrcheNet VPN"
    :put "  ✓ WireGuard interface '$tunnelName' created"
}} on-error={{
    :put "  ! Interface already exists or failed to create"
}}

# 2. Configure WireGuard Peer (OrcheNet Server)
:put "Step 2: Adding OrcheNet server as WireGuard peer..."
:do {{
    /interface wireguard peers add interface=$tunnelName \\
        public-key=$orchenetServerPublicKey \\
        endpoint-address=$orchenetServer \\
        endpoint-port=$orchenetPort \\
        allowed-address=10.99.0.0/24 \\
        persistent-keepalive=25s \\
        comment="OrcheNet Server"
    :put "  ✓ Server peer added"
}} on-error={{
    :put "  ! Peer already exists or failed to add"
}}

# 3. Assign IP Address to WireGuard Interface
:put "Step 3: Assigning IP address to WireGuard interface..."
:do {{
    /ip address add address=$deviceVpnIp interface=$tunnelName comment="OrcheNet VPN IP"
    :put "  ✓ IP address assigned: $deviceVpnIp"
}} on-error={{
    :put "  ! IP address already exists or failed to assign"
}}

# 4. Add Route to OrcheNet Server via WireGuard
:put "Step 4: Adding route to OrcheNet network..."
:do {{
    /ip route add dst-address=10.99.0.0/24 gateway=$tunnelName comment="OrcheNet VPN Route"
    :put "  ✓ Route added"
}} on-error={{
    :put "  ! Route already exists or failed to add"
}}

# 5. Create SSH User for OrcheNet
:put "Step 5: Creating SSH user for OrcheNet..."
:do {{
    /user add name=$sshUser password=$sshPassword group=full comment="OrcheNet Management"
    :put "  ✓ User '$sshUser' created"
    :put "  ⚠ IMPORTANT: Change password with: /user set $sshUser password=YOUR_SECURE_PASSWORD"
}} on-error={{
    :put "  ! User already exists or failed to create"
}}

# 6. Enable SSH Service
:put "Step 6: Enabling SSH service..."
:do {{
    /ip service set ssh disabled=no port=22
    :put "  ✓ SSH service enabled on port 22"
}} on-error={{
    :put "  ! SSH service configuration failed"
}}

# 7. Add Firewall Rule to Allow SSH from OrcheNet VPN
:put "Step 7: Configuring firewall for OrcheNet access..."
:do {{
    /ip firewall filter add chain=input protocol=tcp dst-port=22 \\
        src-address=10.99.0.0/24 in-interface=$tunnelName \\
        action=accept place-before=0 \\
        comment="Allow SSH from OrcheNet VPN"
    :put "  ✓ Firewall rule added"
}} on-error={{
    :put "  ! Firewall rule already exists or failed to add"
}}

# 8. Create Check-in Script
:put "Step 8: Creating check-in script..."
:local checkinScriptSource ":local apiUrl \\"$apiUrl\\"\\n\\
:local deviceName [/system identity get name]\\n\\
:local macAddress \\"{mac_address}\\"\\n\\
:local serialNumber [/system routerboard get serial-number]\\n\\
:local firmwareVersion [/system package get system version]\\n\\
:local uptimeSeconds [/system resource get uptime]\\n\\
:local cpuLoad [/system resource get cpu-load]\\n\\
:local freeMemory [/system resource get free-memory]\\n\\
:local totalMemory [/system resource get total-memory]\\n\\
:local wgStatus \\"down\\"\\n\\
:if ([/interface get [find name=\\"$tunnelName\\"] running]) do={{:set wgStatus \\"up\\"}}\\n\\
:local jsonData \\"{{\\\\\\\"device_name\\\\\\\":\\\\\\\"\$deviceName\\\\\\",\\\\\\\"vendor\\\\\\\":\\\\\\\"mikrotik\\\\\\",\\\\\\\"mac_address\\\\\\\":\\\\\\\"\$macAddress\\\\\\",\\\\\\\"serial_number\\\\\\\":\\\\\\\"\$serialNumber\\\\\\",\\\\\\\"firmware_version\\\\\\\":\\\\\\\"\$firmwareVersion\\\\\\",\\\\\\\"status_data\\\\\\\":{{\\\\\\\"uptime\\\\\\\":\$uptimeSeconds,\\\\\\\"cpu_load\\\\\\\":\$cpuLoad,\\\\\\\"free_memory\\\\\\\":\$freeMemory,\\\\\\\"total_memory\\\\\\\":\$totalMemory,\\\\\\\"wireguard_status\\\\\\\":\\\\\\\"\$wgStatus\\\\\\\"}}}}}\\"\\n\\
:do {{\\n\\
    /tool fetch url=\$apiUrl mode=https http-method=post http-header-field=\\"Content-Type: application/json\\" http-data=\$jsonData dst-path=checkin-response.json\\n\\
    :log info \\"OrcheNet: Check-in successful\\"\\n\\
}} on-error={{\\n\\
    :log error \\"OrcheNet: Check-in failed\\"\\n\\
}}"

:do {{
    /system script add name=orchenet-checkin owner=admin policy=read,write,policy,test source=$checkinScriptSource comment="OrcheNet automatic check-in"
    :put "  ✓ Check-in script created"
}} on-error={{
    :put "  ! Check-in script already exists or failed to create"
}}

# 9. Schedule Check-in Script
:put "Step 9: Scheduling automatic check-ins..."
:do {{
    /system scheduler add name=orchenet-checkin \\
        interval=5m \\
        on-event="/system script run orchenet-checkin" \\
        start-time=startup \\
        comment="OrcheNet periodic check-in (every 5 minutes)"
    :put "  ✓ Scheduler created (5 minute interval)"
}} on-error={{
    :put "  ! Scheduler already exists or failed to create"
}}

# 10. Test WireGuard Connection
:put "Step 10: Testing WireGuard connection..."
:delay 3s
:if ([/interface get [find name=$tunnelName] running]) do={{
    :put "  ✓ WireGuard interface '$tunnelName' is UP"
    :do {{
        /ping 10.99.0.1 count=3
        :put "  ✓ Ping to OrcheNet server successful"
    }} on-error={{
        :put "  ⚠ WARNING: Ping to OrcheNet server failed (check firewall/routing)"
    }}
}} else={{
    :put "  ⚠ WARNING: WireGuard interface is DOWN"
}}

# 11. Run initial check-in
:put "Step 11: Performing initial check-in..."
:delay 2s
:do {{
    /system script run orchenet-checkin
    :put "  ✓ Initial check-in completed"
}} on-error={{
    :put "  ⚠ WARNING: Initial check-in failed (device will retry in 5 minutes)"
}}

:put ""
:put "===== Provisioning Complete ====="
:put "Tunnel Name: $tunnelName"
:put "Device VPN IP: {device_vpn_ip}"
:put "Server VPN IP: 10.99.0.1"
:put ""
:put "⚠ CRITICAL NEXT STEPS:"
:put "  1. Change SSH password: /user set $sshUser password=YOUR_SECURE_PASSWORD"
:put "  2. Verify device appears in OrcheNet web interface (within 5 minutes)"
:put "  3. Test SSH access: ssh $sshUser@{device_vpn_ip}"
:put ""
:put "Tunnel interface: $tunnelName"
:put "Check-in interval: 5 minutes"
:put "Script can be re-run safely (existing configs won't be duplicated)"
:put ""
'''.format(
        device_name=device_name,
        mac_address=mac_address,
        tunnel_name=tunnel_name,
        server_ip=server_ip,
        server_port=server_port,
        server_public_key=server_public_key,
        device_private_key=device_private_key,
        device_vpn_ip=device_vpn_ip,
        api_url=api_url
    )

    return script


@router.post("/provision-script", response_model=ProvisionScriptResponse)
async def generate_provision_script(
    request: ProvisionScriptRequest,
    db: Session = Depends(get_db)
):
    """
    Generate a provisioning script for a device.
    This will:
    1. Generate WireGuard keypair for the device
    2. Enable WireGuard and allocate VPN IP
    3. Generate MikroTik provisioning script with all configs
    """
    # Get device
    device = db.query(Device).filter(Device.id == request.device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with id {request.device_id} not found"
        )

    # Only MikroTik supported for now
    if device.vendor != "mikrotik":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provisioning scripts only supported for MikroTik devices currently"
        )

    # Generate WireGuard keypair for device
    device_private_key, device_public_key = generate_wireguard_keypair()

    # Enable WireGuard for device (this allocates VPN IP and configures server)
    from ..routers.wireguard import WireGuardPeerRequest, enable_wireguard_for_device, get_wireguard_info

    peer_request = WireGuardPeerRequest(
        device_id=request.device_id,
        public_key=device_public_key
    )

    # Call enable_wireguard_for_device
    peer_response = await enable_wireguard_for_device(peer_request, db)

    # Get server info
    wireguard_info = await get_wireguard_info()

    # Get server IP from environment or config
    import socket
    server_ip = os.getenv('ORCHENET_PUBLIC_IP', None)
    if not server_ip:
        # Try to get server IP from hostname
        try:
            server_ip = socket.gethostbyname(socket.gethostname())
        except:
            server_ip = "YOUR_SERVER_IP"

    api_url = os.getenv('ORCHENET_API_URL', f"http://{server_ip}:8000")

    # Generate provisioning script
    script = generate_mikrotik_provisioning_script(
        device_name=device.name,
        mac_address=request.mac_address,
        server_ip=server_ip,
        server_port=wireguard_info.listen_port,
        server_public_key=wireguard_info.server_public_key,
        device_private_key=device_private_key,
        device_vpn_ip=peer_response.private_ip,
        api_url=api_url
    )

    # Generate filename
    tunnel_name = f"orcatun_{format_mac_for_tunnel(request.mac_address)}"
    filename = f"provision_{tunnel_name}.rsc"

    return {
        "script": script,
        "filename": filename,
        "wireguard_info": {
            "vpn_ip": peer_response.private_ip,
            "server_ip": "10.99.0.1",
            "tunnel_name": tunnel_name,
            "public_key": device_public_key
        }
    }
