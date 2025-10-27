"""
Base vendor interface for device abstraction
All vendor implementations must inherit from this base class.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any


class VendorInterface(ABC):
    """Abstract base class for vendor implementations"""

    @abstractmethod
    def yaml_to_commands(self, config: Dict[str, Any]) -> List[str]:
        """
        Convert YAML configuration to vendor-specific commands

        Args:
            config: Parsed YAML configuration dictionary

        Returns:
            List of vendor-specific commands to execute
        """
        pass

    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate YAML configuration for this vendor

        Args:
            config: Parsed YAML configuration dictionary

        Returns:
            Tuple of (is_valid, error_messages)
        """
        pass

    @abstractmethod
    def parse_device_status(self, raw_status: str) -> Dict[str, Any]:
        """
        Parse device status output into normalized format

        Args:
            raw_status: Raw status output from device

        Returns:
            Normalized status dictionary
        """
        pass

    @abstractmethod
    def get_status_commands(self) -> List[str]:
        """
        Get commands to retrieve device status

        Returns:
            List of status collection commands
        """
        pass

    @abstractmethod
    def supports_feature(self, feature: str) -> bool:
        """
        Check if vendor supports a specific feature

        Args:
            feature: Feature name to check

        Returns:
            True if feature is supported
        """
        pass
