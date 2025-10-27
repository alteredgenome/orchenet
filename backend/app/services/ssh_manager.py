"""
SSH Connection Manager
Handles SSH connections to network devices with connection pooling and security.
"""
import asyncio
import logging
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
import asyncssh
from asyncssh import SSHClientConnection, SSHClientConnectionOptions

logger = logging.getLogger(__name__)


class SSHConnectionError(Exception):
    """SSH connection related errors"""
    pass


class SSHManager:
    """
    Manages SSH connections to network devices.
    Handles connection pooling, authentication, and command execution.
    """

    def __init__(self):
        self._connections: Dict[str, SSHClientConnection] = {}
        self._connection_locks: Dict[str, asyncio.Lock] = {}

    async def execute_commands(
        self,
        host: str,
        username: str,
        password: Optional[str] = None,
        key_path: Optional[str] = None,
        commands: List[str] = None,
        port: int = 22,
        timeout: int = 30
    ) -> List[str]:
        """
        Execute commands on a device via SSH.

        Args:
            host: Device IP or hostname
            username: SSH username
            password: SSH password (if not using key)
            key_path: Path to SSH private key (if not using password)
            commands: List of commands to execute
            port: SSH port (default 22)
            timeout: Command timeout in seconds

        Returns:
            List of command outputs

        Raises:
            SSHConnectionError: If connection or execution fails
        """
        if not commands:
            return []

        try:
            async with self._get_connection(host, username, password, key_path, port, timeout) as conn:
                results = []
                for command in commands:
                    logger.info(f"Executing on {host}: {command}")
                    result = await conn.run(command, check=False, timeout=timeout)

                    output = result.stdout if result.stdout else ""
                    if result.stderr:
                        logger.warning(f"Command stderr on {host}: {result.stderr}")

                    results.append(output)

                return results

        except asyncssh.Error as e:
            logger.error(f"SSH error for {host}: {str(e)}")
            raise SSHConnectionError(f"Failed to execute commands on {host}: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error for {host}: {str(e)}")
            raise SSHConnectionError(f"Unexpected error on {host}: {str(e)}")

    @asynccontextmanager
    async def _get_connection(
        self,
        host: str,
        username: str,
        password: Optional[str],
        key_path: Optional[str],
        port: int,
        timeout: int
    ):
        """
        Get or create an SSH connection.
        Uses context manager to ensure proper cleanup.
        """
        connection_key = f"{username}@{host}:{port}"

        # Ensure we have a lock for this connection
        if connection_key not in self._connection_locks:
            self._connection_locks[connection_key] = asyncio.Lock()

        async with self._connection_locks[connection_key]:
            try:
                # Create connection options
                options = SSHClientConnectionOptions(
                    username=username,
                    password=password if password else None,
                    client_keys=[key_path] if key_path else None,
                    known_hosts=None,  # Disable host key checking (configure appropriately for production)
                    connect_timeout=timeout,
                )

                # Create new connection
                conn = await asyncssh.connect(
                    host,
                    port=port,
                    options=options,
                )

                try:
                    yield conn
                finally:
                    # Close connection after use
                    conn.close()
                    await conn.wait_closed()

            except asyncssh.Error as e:
                raise SSHConnectionError(f"Failed to connect to {host}: {str(e)}")

    async def test_connection(
        self,
        host: str,
        username: str,
        password: Optional[str] = None,
        key_path: Optional[str] = None,
        port: int = 22
    ) -> bool:
        """
        Test if SSH connection can be established.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            await self.execute_commands(
                host=host,
                username=username,
                password=password,
                key_path=key_path,
                port=port,
                commands=["echo 'test'"],
                timeout=10
            )
            return True
        except SSHConnectionError:
            return False

    def close_all(self):
        """Close all cached connections"""
        for conn in self._connections.values():
            if conn and not conn.is_closed():
                conn.close()
        self._connections.clear()


# Global SSH manager instance
ssh_manager = SSHManager()
