"""
Configuration Executor Service
Executes configuration changes on network devices using vendor-specific translators.
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..models.device import Device, DeviceVendor
from ..vendors.mikrotik.translator import MikroTikTranslator
from ..vendors.fortinet.translator import FortinetTranslator
from ..vendors.ubiquiti.translator import UniFiTranslator
from ..vendors.watchguard.translator import WatchGuardTranslator
from .ssh_manager import ssh_manager, SSHConnectionError
from .unifi_controller import UniFiController

logger = logging.getLogger(__name__)


class ConfigExecutorError(Exception):
    """Configuration execution related errors"""
    pass


class ConfigExecutor:
    """
    Executes configuration changes on network devices.
    Handles translation from unified YAML to vendor-specific commands/API calls.
    """

    def __init__(self):
        self.translators = {
            DeviceVendor.MIKROTIK: MikroTikTranslator(),
            DeviceVendor.FORTINET: FortinetTranslator(),
            DeviceVendor.UBIQUITI: UniFiTranslator(),
            DeviceVendor.WATCHGUARD: WatchGuardTranslator()
        }

    async def execute_config(
        self,
        device: Device,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute configuration on a device.

        Args:
            device: Device object
            config: Unified YAML configuration as dictionary

        Returns:
            Execution result dictionary with status and details

        Raises:
            ConfigExecutorError: If execution fails
        """
        logger.info(f"Executing configuration on device {device.name} ({device.vendor})")

        # Get appropriate translator
        translator = self.translators.get(device.vendor)
        if not translator:
            raise ConfigExecutorError(f"No translator found for vendor: {device.vendor}")

        # Validate configuration
        is_valid, error_msg = translator.validate_config(config)
        if not is_valid:
            raise ConfigExecutorError(f"Configuration validation failed: {error_msg}")

        # Translate configuration
        try:
            commands = translator.yaml_to_commands(config)
            logger.info(f"Translated configuration to {len(commands)} commands/operations")
        except Exception as e:
            raise ConfigExecutorError(f"Configuration translation failed: {str(e)}")

        # Execute based on vendor
        if device.vendor == DeviceVendor.UBIQUITI:
            result = await self._execute_unifi(device, commands)
        else:
            result = await self._execute_ssh(device, commands)

        # Update device status
        result["executed_at"] = datetime.utcnow().isoformat()
        result["command_count"] = len(commands)

        return result

    async def _execute_ssh(
        self,
        device: Device,
        commands: List[str]
    ) -> Dict[str, Any]:
        """
        Execute commands via SSH.

        Args:
            device: Device object
            commands: List of CLI commands

        Returns:
            Execution result
        """
        if not device.ip_address:
            raise ConfigExecutorError("Device IP address not configured")

        if not device.ssh_username:
            raise ConfigExecutorError("SSH username not configured")

        try:
            # Execute commands via SSH
            outputs = await ssh_manager.execute_commands(
                host=device.ip_address,
                username=device.ssh_username,
                password=device.ssh_password,
                key_path=device.ssh_key,
                commands=commands,
                port=device.ssh_port or 22,
                timeout=60
            )

            # Check for errors in output
            errors = []
            for idx, output in enumerate(outputs):
                if output and ("error" in output.lower() or "failed" in output.lower()):
                    errors.append({
                        "command_index": idx,
                        "command": commands[idx],
                        "output": output
                    })

            success = len(errors) == 0

            return {
                "success": success,
                "method": "ssh",
                "commands_executed": len(commands),
                "outputs": outputs,
                "errors": errors if errors else None
            }

        except SSHConnectionError as e:
            logger.error(f"SSH connection failed for {device.name}: {str(e)}")
            return {
                "success": False,
                "method": "ssh",
                "error": str(e),
                "commands_executed": 0
            }

    async def _execute_unifi(
        self,
        device: Device,
        operations: List[str]
    ) -> Dict[str, Any]:
        """
        Execute configuration via UniFi Controller API.

        Args:
            device: Device object
            operations: List of API operations (JSON strings)

        Returns:
            Execution result
        """
        if not device.api_url:
            raise ConfigExecutorError("UniFi Controller URL not configured")

        if not device.api_key and not device.ssh_password:
            raise ConfigExecutorError("UniFi Controller credentials not configured")

        try:
            import json

            # Parse operations
            parsed_ops = []
            for op_str in operations:
                try:
                    parsed_ops.append(json.loads(op_str))
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse operation: {op_str}")

            # Execute via UniFi Controller
            async with UniFiController(
                controller_url=device.api_url,
                username=device.ssh_username or "admin",
                password=device.ssh_password or device.api_key,
                site=device.metadata.get("unifi_site", "default") if device.metadata else "default"
            ) as controller:
                results = await controller.apply_configuration(parsed_ops)

            # Check for failures
            errors = [r for r in results if not r.get("success")]
            success = len(errors) == 0

            return {
                "success": success,
                "method": "unifi_api",
                "operations_executed": len(parsed_ops),
                "results": results,
                "errors": errors if errors else None
            }

        except Exception as e:
            logger.error(f"UniFi API execution failed for {device.name}: {str(e)}")
            return {
                "success": False,
                "method": "unifi_api",
                "error": str(e),
                "operations_executed": 0
            }

    async def test_connection(self, device: Device) -> bool:
        """
        Test connection to a device.

        Args:
            device: Device object

        Returns:
            True if connection successful
        """
        try:
            if device.vendor == DeviceVendor.UBIQUITI:
                # Test UniFi Controller connection
                if not device.api_url:
                    return False

                async with UniFiController(
                    controller_url=device.api_url,
                    username=device.ssh_username or "admin",
                    password=device.ssh_password or device.api_key,
                    site=device.metadata.get("unifi_site", "default") if device.metadata else "default"
                ) as controller:
                    await controller.get_devices()
                return True

            else:
                # Test SSH connection
                if not device.ip_address or not device.ssh_username:
                    return False

                return await ssh_manager.test_connection(
                    host=device.ip_address,
                    username=device.ssh_username,
                    password=device.ssh_password,
                    key_path=device.ssh_key,
                    port=device.ssh_port or 22
                )

        except Exception as e:
            logger.error(f"Connection test failed for {device.name}: {str(e)}")
            return False

    async def get_device_status(self, device: Device) -> Dict[str, Any]:
        """
        Retrieve current status from a device.

        Args:
            device: Device object

        Returns:
            Device status dictionary
        """
        translator = self.translators.get(device.vendor)
        if not translator:
            raise ConfigExecutorError(f"No translator found for vendor: {device.vendor}")

        try:
            if device.vendor == DeviceVendor.UBIQUITI:
                # Get status via UniFi Controller
                async with UniFiController(
                    controller_url=device.api_url,
                    username=device.ssh_username or "admin",
                    password=device.ssh_password or device.api_key,
                    site=device.metadata.get("unifi_site", "default") if device.metadata else "default"
                ) as controller:
                    if device.mac_address:
                        status = await controller.get_device_status(device.mac_address)
                        return translator.parse_device_status(str(status))
                    else:
                        devices = await controller.get_devices()
                        if devices:
                            return translator.parse_device_status(str(devices[0]))
                        return {"status": "unknown"}

            else:
                # Get status via SSH
                status_commands = translator.get_status_commands()
                outputs = await ssh_manager.execute_commands(
                    host=device.ip_address,
                    username=device.ssh_username,
                    password=device.ssh_password,
                    key_path=device.ssh_key,
                    commands=status_commands,
                    port=device.ssh_port or 22,
                    timeout=30
                )

                # Parse status from output
                combined_output = "\n".join(outputs)
                return translator.parse_device_status(combined_output)

        except Exception as e:
            logger.error(f"Failed to get status for {device.name}: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }


# Global executor instance
config_executor = ConfigExecutor()
