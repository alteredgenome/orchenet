"""
WireGuard VPN Manager
Handles WireGuard server configuration and peer management
"""
import asyncio
import logging
import subprocess
import ipaddress
from typing import Optional, Dict, List, Tuple
from pathlib import Path
import re

logger = logging.getLogger(__name__)


class WireGuardError(Exception):
    """WireGuard-related errors"""
    pass


class WireGuardManager:
    """
    Manages WireGuard VPN server and device peers.
    Handles peer configuration, IP allocation, and server management.
    """

    def __init__(
        self,
        interface: str = "wg0",
        server_ip: str = "10.99.0.1",
        subnet: str = "10.99.0.0/24",
        listen_port: int = 51820,
        config_path: str = "/etc/wireguard",
    ):
        """
        Initialize WireGuard manager.

        Args:
            interface: WireGuard interface name (default: wg0)
            server_ip: Server VPN IP address
            subnet: VPN subnet in CIDR notation
            listen_port: UDP port for WireGuard
            config_path: Path to WireGuard configuration directory
        """
        self.interface = interface
        self.server_ip = server_ip
        self.subnet = subnet
        self.listen_port = listen_port
        self.config_path = Path(config_path)
        self.config_file = self.config_path / f"{interface}.conf"
        self.network = ipaddress.ip_network(subnet)

    async def setup_server(self, server_private_key: Optional[str] = None) -> Dict[str, str]:
        """
        Set up WireGuard server configuration.

        Args:
            server_private_key: Existing private key or None to generate new

        Returns:
            Dict with server_private_key, server_public_key, server_ip
        """
        try:
            # Generate or use provided private key
            if not server_private_key:
                server_private_key = await self._run_command("wg genkey")

            # Generate public key from private key
            server_public_key = await self._run_command(
                f"echo '{server_private_key}' | wg pubkey"
            )

            # Create configuration directory
            self.config_path.mkdir(parents=True, exist_ok=True)

            # Create server configuration
            config_content = f"""[Interface]
PrivateKey = {server_private_key}
Address = {self.server_ip}/{self.network.prefixlen}
ListenPort = {self.listen_port}
PostUp = iptables -A FORWARD -i {self.interface} -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i {self.interface} -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

# Peers will be added below
"""

            # Write configuration (requires root)
            self.config_file.write_text(config_content)
            self.config_file.chmod(0o600)

            logger.info(f"WireGuard server configuration created at {self.config_file}")

            return {
                "server_private_key": server_private_key,
                "server_public_key": server_public_key,
                "server_ip": self.server_ip,
                "listen_port": self.listen_port,
            }

        except Exception as e:
            logger.error(f"Failed to setup WireGuard server: {e}")
            raise WireGuardError(f"Server setup failed: {e}")

    async def add_peer(
        self,
        peer_name: str,
        peer_public_key: str,
        peer_ip: str,
        allowed_ips: Optional[str] = None,
    ) -> bool:
        """
        Add a peer to WireGuard configuration.

        Args:
            peer_name: Friendly name for the peer (comment)
            peer_public_key: Peer's WireGuard public key
            peer_ip: IP address to assign to peer
            allowed_ips: CIDR ranges allowed from peer (default: peer_ip/32)

        Returns:
            True if successful
        """
        try:
            if not allowed_ips:
                allowed_ips = f"{peer_ip}/32"

            # Add peer configuration to config file
            peer_config = f"""
# {peer_name}
[Peer]
PublicKey = {peer_public_key}
AllowedIPs = {allowed_ips}

"""

            # Append to config file
            with open(self.config_file, "a") as f:
                f.write(peer_config)

            # Add peer to running interface if active
            if await self._is_interface_up():
                await self._run_command(
                    f"wg set {self.interface} peer {peer_public_key} allowed-ips {allowed_ips}"
                )

            logger.info(f"Added WireGuard peer: {peer_name} ({peer_ip})")
            return True

        except Exception as e:
            logger.error(f"Failed to add peer {peer_name}: {e}")
            raise WireGuardError(f"Failed to add peer: {e}")

    async def remove_peer(self, peer_public_key: str) -> bool:
        """
        Remove a peer from WireGuard configuration.

        Args:
            peer_public_key: Public key of peer to remove

        Returns:
            True if successful
        """
        try:
            # Remove from running interface
            if await self._is_interface_up():
                await self._run_command(f"wg set {self.interface} peer {peer_public_key} remove")

            # Remove from config file
            config_content = self.config_file.read_text()

            # Find and remove peer section
            pattern = rf"# .*\n\[Peer\]\nPublicKey = {re.escape(peer_public_key)}\n.*?\n\n"
            config_content = re.sub(pattern, "", config_content, flags=re.MULTILINE)

            self.config_file.write_text(config_content)

            logger.info(f"Removed WireGuard peer: {peer_public_key}")
            return True

        except Exception as e:
            logger.error(f"Failed to remove peer: {e}")
            raise WireGuardError(f"Failed to remove peer: {e}")

    async def get_peer_status(self, peer_public_key: str) -> Optional[Dict]:
        """
        Get status of a specific peer.

        Args:
            peer_public_key: Public key of peer

        Returns:
            Dict with peer status or None if not found
        """
        try:
            if not await self._is_interface_up():
                return None

            output = await self._run_command(f"wg show {self.interface} dump")

            # Parse wg show output
            for line in output.strip().split("\n")[1:]:  # Skip header
                parts = line.split("\t")
                if len(parts) >= 5 and parts[0] == peer_public_key:
                    return {
                        "public_key": parts[0],
                        "preshared_key": parts[1] if parts[1] != "(none)" else None,
                        "endpoint": parts[2] if parts[2] != "(none)" else None,
                        "allowed_ips": parts[3],
                        "last_handshake": int(parts[4]) if parts[4] != "0" else None,
                        "rx_bytes": int(parts[5]) if len(parts) > 5 else 0,
                        "tx_bytes": int(parts[6]) if len(parts) > 6 else 0,
                    }

            return None

        except Exception as e:
            logger.error(f"Failed to get peer status: {e}")
            return None

    async def get_all_peers(self) -> List[Dict]:
        """
        Get status of all configured peers.

        Returns:
            List of peer status dicts
        """
        try:
            if not await self._is_interface_up():
                return []

            output = await self._run_command(f"wg show {self.interface} dump")
            peers = []

            for line in output.strip().split("\n")[1:]:  # Skip header
                parts = line.split("\t")
                if len(parts) >= 5:
                    peers.append({
                        "public_key": parts[0],
                        "endpoint": parts[2] if parts[2] != "(none)" else None,
                        "allowed_ips": parts[3],
                        "last_handshake": int(parts[4]) if parts[4] != "0" else None,
                        "rx_bytes": int(parts[5]) if len(parts) > 5 else 0,
                        "tx_bytes": int(parts[6]) if len(parts) > 6 else 0,
                    })

            return peers

        except Exception as e:
            logger.error(f"Failed to get all peers: {e}")
            return []

    async def start_interface(self) -> bool:
        """
        Start the WireGuard interface.

        Returns:
            True if successful
        """
        try:
            await self._run_command(f"wg-quick up {self.interface}")
            logger.info(f"WireGuard interface {self.interface} started")
            return True
        except Exception as e:
            logger.error(f"Failed to start WireGuard: {e}")
            return False

    async def stop_interface(self) -> bool:
        """
        Stop the WireGuard interface.

        Returns:
            True if successful
        """
        try:
            await self._run_command(f"wg-quick down {self.interface}")
            logger.info(f"WireGuard interface {self.interface} stopped")
            return True
        except Exception as e:
            logger.error(f"Failed to stop WireGuard: {e}")
            return False

    async def restart_interface(self) -> bool:
        """
        Restart the WireGuard interface.

        Returns:
            True if successful
        """
        await self.stop_interface()
        await asyncio.sleep(1)
        return await self.start_interface()

    async def allocate_ip(self, used_ips: List[str]) -> Optional[str]:
        """
        Allocate next available IP address from subnet.

        Args:
            used_ips: List of already allocated IPs

        Returns:
            Next available IP address or None if subnet exhausted
        """
        used_set = set(used_ips)
        used_set.add(self.server_ip)  # Reserve server IP

        for ip in self.network.hosts():
            ip_str = str(ip)
            if ip_str not in used_set:
                return ip_str

        return None

    async def generate_keypair(self) -> Tuple[str, str]:
        """
        Generate a new WireGuard key pair.

        Returns:
            Tuple of (private_key, public_key)
        """
        try:
            private_key = await self._run_command("wg genkey")
            public_key = await self._run_command(f"echo '{private_key}' | wg pubkey")
            return private_key.strip(), public_key.strip()
        except Exception as e:
            logger.error(f"Failed to generate keypair: {e}")
            raise WireGuardError(f"Keypair generation failed: {e}")

    async def generate_peer_config(
        self,
        peer_private_key: str,
        peer_ip: str,
        server_public_key: str,
        server_endpoint: str,
        dns: Optional[str] = None,
    ) -> str:
        """
        Generate client configuration for a peer.

        Args:
            peer_private_key: Peer's private key
            peer_ip: Peer's VPN IP address
            server_public_key: Server's public key
            server_endpoint: Server's public IP:port
            dns: DNS server (optional)

        Returns:
            WireGuard configuration string
        """
        config = f"""[Interface]
PrivateKey = {peer_private_key}
Address = {peer_ip}/32
"""

        if dns:
            config += f"DNS = {dns}\n"

        config += f"""
[Peer]
PublicKey = {server_public_key}
Endpoint = {server_endpoint}
AllowedIPs = {self.subnet}
PersistentKeepalive = 25
"""

        return config

    async def _is_interface_up(self) -> bool:
        """Check if WireGuard interface is up."""
        try:
            await self._run_command(f"ip link show {self.interface}")
            return True
        except:
            return False

    async def _run_command(self, command: str) -> str:
        """
        Run a shell command asynchronously.

        Args:
            command: Shell command to execute

        Returns:
            Command output (stdout)

        Raises:
            WireGuardError: If command fails
        """
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                error_msg = stderr.decode().strip()
                raise WireGuardError(f"Command failed: {error_msg}")

            return stdout.decode().strip()

        except WireGuardError:
            raise
        except Exception as e:
            raise WireGuardError(f"Command execution error: {e}")


# Global WireGuard manager instance
wireguard_manager = WireGuardManager()
