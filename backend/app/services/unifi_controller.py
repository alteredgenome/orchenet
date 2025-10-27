"""
UniFi Controller Integration Service
Communicates with UniFi Controller API for device management.
"""
import asyncio
import logging
from typing import Optional, List, Dict, Any
import aiohttp
import json

logger = logging.getLogger(__name__)


class UniFiControllerError(Exception):
    """UniFi Controller related errors"""
    pass


class UniFiController:
    """
    UniFi Controller API client.
    Handles authentication, device discovery, and configuration management.
    """

    def __init__(
        self,
        controller_url: str,
        username: str,
        password: str,
        site: str = "default",
        verify_ssl: bool = True
    ):
        """
        Initialize UniFi Controller client.

        Args:
            controller_url: Controller URL (e.g., https://unifi.example.com:8443)
            username: Controller admin username
            password: Controller admin password
            site: Site name (default: "default")
            verify_ssl: Whether to verify SSL certificates
        """
        self.controller_url = controller_url.rstrip('/')
        self.username = username
        self.password = password
        self.site = site
        self.verify_ssl = verify_ssl
        self._session: Optional[aiohttp.ClientSession] = None
        self._authenticated = False

    async def __aenter__(self):
        """Async context manager entry"""
        await self.login()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.logout()

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(ssl=self.verify_ssl)
            self._session = aiohttp.ClientSession(connector=connector)
        return self._session

    async def login(self) -> bool:
        """
        Authenticate with UniFi Controller.

        Returns:
            True if authentication successful

        Raises:
            UniFiControllerError: If authentication fails
        """
        session = await self._get_session()

        login_data = {
            "username": self.username,
            "password": self.password,
            "remember": False
        }

        try:
            async with session.post(
                f"{self.controller_url}/api/login",
                json=login_data
            ) as response:
                if response.status == 200:
                    self._authenticated = True
                    logger.info(f"Successfully authenticated to UniFi Controller at {self.controller_url}")
                    return True
                else:
                    error_text = await response.text()
                    raise UniFiControllerError(
                        f"Authentication failed: HTTP {response.status} - {error_text}"
                    )

        except aiohttp.ClientError as e:
            raise UniFiControllerError(f"Failed to connect to controller: {str(e)}")

    async def logout(self):
        """Logout from UniFi Controller"""
        if self._session and not self._session.closed:
            try:
                async with self._session.post(f"{self.controller_url}/api/logout") as response:
                    self._authenticated = False
                    logger.info("Logged out from UniFi Controller")
            except:
                pass
            finally:
                await self._session.close()

    async def get_devices(self, device_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all devices from controller.

        Args:
            device_type: Filter by device type (uap, usw, ugw, etc.)

        Returns:
            List of device dictionaries

        Raises:
            UniFiControllerError: If request fails
        """
        if not self._authenticated:
            await self.login()

        session = await self._get_session()

        try:
            async with session.get(
                f"{self.controller_url}/api/s/{self.site}/stat/device"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    devices = data.get("data", [])

                    # Filter by device type if specified
                    if device_type:
                        devices = [d for d in devices if d.get("type") == device_type]

                    return devices
                else:
                    raise UniFiControllerError(f"Failed to get devices: HTTP {response.status}")

        except aiohttp.ClientError as e:
            raise UniFiControllerError(f"Failed to get devices: {str(e)}")

    async def get_device_status(self, device_mac: str) -> Dict[str, Any]:
        """
        Get status of a specific device.

        Args:
            device_mac: Device MAC address

        Returns:
            Device status dictionary
        """
        devices = await self.get_devices()
        for device in devices:
            if device.get("mac") == device_mac:
                return device

        raise UniFiControllerError(f"Device with MAC {device_mac} not found")

    async def apply_configuration(self, operations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Apply configuration operations to UniFi Controller.

        Args:
            operations: List of API operation dictionaries
                Each dict should have: endpoint, method, data

        Returns:
            List of operation results

        Raises:
            UniFiControllerError: If operations fail
        """
        if not self._authenticated:
            await self.login()

        session = await self._get_session()
        results = []

        for operation in operations:
            endpoint = operation.get("endpoint", "").replace("{site}", self.site)
            method = operation.get("method", "POST").upper()
            data = operation.get("data", {})

            url = f"{self.controller_url}{endpoint}"

            try:
                async with session.request(
                    method,
                    url,
                    json=data
                ) as response:
                    result = {
                        "endpoint": endpoint,
                        "method": method,
                        "status": response.status,
                        "success": response.status in [200, 201]
                    }

                    if response.status in [200, 201]:
                        result["data"] = await response.json()
                    else:
                        result["error"] = await response.text()

                    results.append(result)
                    logger.info(f"Applied operation {method} {endpoint}: HTTP {response.status}")

            except aiohttp.ClientError as e:
                results.append({
                    "endpoint": endpoint,
                    "method": method,
                    "success": False,
                    "error": str(e)
                })
                logger.error(f"Failed to apply operation {method} {endpoint}: {str(e)}")

        return results

    async def create_network(self, name: str, vlan_id: int, **kwargs) -> Dict[str, Any]:
        """
        Create a new network.

        Args:
            name: Network name
            vlan_id: VLAN ID
            **kwargs: Additional network parameters

        Returns:
            Created network data
        """
        network_data = {
            "name": name,
            "vlan": vlan_id,
            "enabled": kwargs.get("enabled", True),
            "purpose": kwargs.get("purpose", "corporate"),
            **kwargs
        }

        operations = [{
            "endpoint": f"/api/s/{self.site}/rest/networkconf",
            "method": "POST",
            "data": network_data
        }]

        results = await self.apply_configuration(operations)
        if results and results[0].get("success"):
            return results[0].get("data", {})
        else:
            raise UniFiControllerError(f"Failed to create network: {results[0].get('error')}")

    async def create_wlan(self, ssid: str, password: str, **kwargs) -> Dict[str, Any]:
        """
        Create a wireless network (WLAN).

        Args:
            ssid: Network SSID
            password: WPA2 password
            **kwargs: Additional WLAN parameters

        Returns:
            Created WLAN data
        """
        wlan_data = {
            "name": ssid,
            "enabled": kwargs.get("enabled", True),
            "security": kwargs.get("security", "wpapsk"),
            "wpa_mode": "wpa2",
            "wpa_enc": "ccmp",
            "x_passphrase": password,
            "usergroup_id": kwargs.get("usergroup_id", ""),
            "wlangroup_id": kwargs.get("wlangroup_id", ""),
            **kwargs
        }

        operations = [{
            "endpoint": f"/api/s/{self.site}/rest/wlanconf",
            "method": "POST",
            "data": wlan_data
        }]

        results = await self.apply_configuration(operations)
        if results and results[0].get("success"):
            return results[0].get("data", {})
        else:
            raise UniFiControllerError(f"Failed to create WLAN: {results[0].get('error')}")

    async def create_firewall_rule(self, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a firewall rule.

        Args:
            rule_data: Firewall rule configuration

        Returns:
            Created rule data
        """
        operations = [{
            "endpoint": f"/api/s/{self.site}/rest/firewallrule",
            "method": "POST",
            "data": rule_data
        }]

        results = await self.apply_configuration(operations)
        if results and results[0].get("success"):
            return results[0].get("data", {})
        else:
            raise UniFiControllerError(f"Failed to create firewall rule: {results[0].get('error')}")

    async def get_site_settings(self) -> Dict[str, Any]:
        """Get site settings"""
        if not self._authenticated:
            await self.login()

        session = await self._get_session()

        async with session.get(
            f"{self.controller_url}/api/s/{self.site}/get/setting"
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("data", {})
            else:
                raise UniFiControllerError(f"Failed to get site settings: HTTP {response.status}")

    async def adopt_device(self, device_mac: str) -> bool:
        """
        Adopt a device into the controller.

        Args:
            device_mac: Device MAC address

        Returns:
            True if adoption successful
        """
        operations = [{
            "endpoint": f"/api/s/{self.site}/cmd/devmgr",
            "method": "POST",
            "data": {
                "cmd": "adopt",
                "mac": device_mac
            }
        }]

        results = await self.apply_configuration(operations)
        return results and results[0].get("success", False)


# Global controller instance (to be initialized with config)
_controller_instance: Optional[UniFiController] = None


def get_controller(
    controller_url: str,
    username: str,
    password: str,
    site: str = "default"
) -> UniFiController:
    """Get or create UniFi Controller instance"""
    global _controller_instance

    if _controller_instance is None:
        _controller_instance = UniFiController(
            controller_url=controller_url,
            username=username,
            password=password,
            site=site
        )

    return _controller_instance
