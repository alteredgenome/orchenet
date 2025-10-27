"""
Fortinet FortiOS Configuration Translator
Translates unified YAML configuration to FortiOS CLI commands.
"""
from typing import Dict, Any, List
import yaml
from ..base import VendorInterface


class FortinetTranslator(VendorInterface):
    """
    Fortinet FortiOS implementation of VendorInterface.
    Translates unified configuration to FortiOS CLI commands.
    """

    def yaml_to_commands(self, config: Dict[str, Any]) -> List[str]:
        """
        Convert unified YAML configuration to FortiOS CLI commands.

        Args:
            config: Unified configuration dictionary

        Returns:
            List of FortiOS CLI commands
        """
        commands = []

        # System configuration
        if "system" in config:
            commands.extend(self._translate_system(config["system"]))

        # Interfaces
        if "interfaces" in config:
            commands.extend(self._translate_interfaces(config["interfaces"]))

        # VLANs
        if "vlans" in config:
            commands.extend(self._translate_vlans(config["vlans"]))

        # Firewall zones
        if "zones" in config:
            commands.extend(self._translate_zones(config["zones"]))

        # Firewall policies
        if "firewall" in config and "policies" in config["firewall"]:
            commands.extend(self._translate_firewall_policies(config["firewall"]["policies"]))

        # NAT
        if "nat" in config:
            commands.extend(self._translate_nat(config["nat"]))

        # VPN
        if "vpn" in config:
            commands.extend(self._translate_vpn(config["vpn"]))

        # Routing
        if "routing" in config:
            commands.extend(self._translate_routing(config["routing"]))

        return commands

    def _translate_system(self, system: Dict[str, Any]) -> List[str]:
        """Translate system configuration"""
        commands = []

        commands.append("config system global")

        if "hostname" in system:
            commands.append(f"    set hostname {system['hostname']}")

        if "timezone" in system:
            commands.append(f"    set timezone {self._map_timezone(system['timezone'])}")

        if "dns" in system:
            dns = system["dns"]
            if "servers" in dns and len(dns["servers"]) > 0:
                commands.append(f"    set dns-server-1 {dns['servers'][0]}")
                if len(dns["servers"]) > 1:
                    commands.append(f"    set dns-server-2 {dns['servers'][1]}")

        if "ntp" in system:
            ntp = system["ntp"]
            if "servers" in ntp and len(ntp["servers"]) > 0:
                commands.append(f"    set ntp-server-1 {ntp['servers'][0]}")

        commands.append("end")

        return commands

    def _translate_interfaces(self, interfaces: List[Dict[str, Any]]) -> List[str]:
        """Translate interface configuration"""
        commands = []

        for iface in interfaces:
            name = iface.get("name")
            if not name:
                continue

            commands.append(f"config system interface")
            commands.append(f"    edit {name}")

            if "description" in iface:
                commands.append(f"        set description \"{iface['description']}\"")

            if "enabled" in iface:
                commands.append(f"        set status {'up' if iface['enabled'] else 'down'}")

            # Addressing
            if "addressing" in iface:
                addr = iface["addressing"]
                if addr.get("mode") == "static" and "ipv4" in addr:
                    ip = addr["ipv4"].get("address")
                    netmask = addr["ipv4"].get("netmask", "255.255.255.0")
                    commands.append(f"        set ip {ip} {netmask}")
                    commands.append(f"        set mode static")
                elif addr.get("mode") == "dhcp":
                    commands.append(f"        set mode dhcp")

            # VLAN
            if "vlan_id" in iface and "parent" in iface:
                commands.append(f"        set vlanid {iface['vlan_id']}")
                commands.append(f"        set interface {iface['parent']}")

            # Zone assignment
            if "zone" in iface:
                # Note: Zones are assigned separately in FortiOS via firewall zone config
                pass

            commands.append("    next")
            commands.append("end")

        return commands

    def _translate_zones(self, zones: List[Dict[str, Any]]) -> List[str]:
        """Translate firewall zones"""
        commands = []

        for zone in zones:
            name = zone.get("name")
            if not name:
                continue

            commands.append("config system zone")
            commands.append(f"    edit {name}")

            if "interfaces" in zone:
                for iface in zone["interfaces"]:
                    commands.append(f"        set interface {iface}")

            commands.append("    next")
            commands.append("end")

        return commands

    def _translate_firewall_policies(self, policies: List[Dict[str, Any]]) -> List[str]:
        """Translate firewall policies"""
        commands = []

        commands.append("config firewall policy")

        for idx, policy in enumerate(policies, start=1):
            policy_id = policy.get("id", idx)
            commands.append(f"    edit {policy_id}")

            if "name" in policy:
                commands.append(f"        set name \"{policy['name']}\"")

            # Source/Destination zones/interfaces
            src_zone = policy.get("source_zone", [])
            if isinstance(src_zone, str):
                src_zone = [src_zone]
            dst_zone = policy.get("destination_zone", [])
            if isinstance(dst_zone, str):
                dst_zone = [dst_zone]

            if src_zone:
                commands.append(f"        set srcintf {' '.join(src_zone)}")
            if dst_zone:
                commands.append(f"        set dstintf {' '.join(dst_zone)}")

            # Source/Destination addresses
            src_addr = policy.get("source_address", ["all"])
            if isinstance(src_addr, str):
                src_addr = [src_addr]
            dst_addr = policy.get("destination_address", ["all"])
            if isinstance(dst_addr, str):
                dst_addr = [dst_addr]

            commands.append(f"        set srcaddr {' '.join(src_addr)}")
            commands.append(f"        set dstaddr {' '.join(dst_addr)}")

            # Services
            services = policy.get("service", ["ALL"])
            if isinstance(services, str):
                services = [services]
            commands.append(f"        set service {' '.join(services)}")

            # Action
            action = policy.get("action", "accept")
            commands.append(f"        set action {action}")

            # NAT
            if policy.get("nat"):
                commands.append(f"        set nat enable")

            # Logging
            if policy.get("log"):
                commands.append(f"        set logtraffic all")

            commands.append("    next")

        commands.append("end")

        return commands

    def _translate_nat(self, nat: Dict[str, Any]) -> List[str]:
        """Translate NAT configuration"""
        # In FortiOS, NAT is typically configured within firewall policies
        # This is handled in _translate_firewall_policies
        return []

    def _translate_vpn(self, vpn: Dict[str, Any]) -> List[str]:
        """Translate VPN configuration"""
        commands = []

        if "ipsec" in vpn:
            for tunnel in vpn["ipsec"]:
                name = tunnel.get("name")
                if not name:
                    continue

                # Phase 1
                commands.append("config vpn ipsec phase1-interface")
                commands.append(f"    edit {name}")
                commands.append(f"        set interface {tunnel.get('interface', 'wan1')}")
                commands.append(f"        set remote-gw {tunnel.get('remote_gateway')}")
                commands.append(f"        set psk {tunnel.get('preshared_key', '')}")
                commands.append("    next")
                commands.append("end")

                # Phase 2
                commands.append("config vpn ipsec phase2-interface")
                commands.append(f"    edit {name}-p2")
                commands.append(f"        set phase1name {name}")

                if "local_subnet" in tunnel:
                    commands.append(f"        set src-subnet {tunnel['local_subnet']}")
                if "remote_subnet" in tunnel:
                    commands.append(f"        set dst-subnet {tunnel['remote_subnet']}")

                commands.append("    next")
                commands.append("end")

        return commands

    def _translate_vlans(self, vlans: List[Dict[str, Any]]) -> List[str]:
        """Translate VLAN configuration (handled in interface config)"""
        return []

    def _translate_routing(self, routing: Dict[str, Any]) -> List[str]:
        """Translate routing configuration"""
        commands = []

        if "static" in routing:
            for idx, route in enumerate(routing["static"]):
                commands.append("config router static")
                commands.append(f"    edit {idx + 1}")
                commands.append(f"        set dst {route.get('destination', '0.0.0.0/0')}")
                commands.append(f"        set gateway {route.get('gateway')}")

                if "interface" in route:
                    commands.append(f"        set device {route['interface']}")

                if "distance" in route:
                    commands.append(f"        set distance {route['distance']}")

                commands.append("    next")
                commands.append("end")

        return commands

    def _map_timezone(self, tz: str) -> str:
        """Map generic timezone to FortiOS timezone ID"""
        # Simplified mapping - expand as needed
        tz_map = {
            "UTC": "00",
            "America/New_York": "81",
            "America/Chicago": "82",
            "America/Los_Angeles": "84",
            "Europe/London": "26",
        }
        return tz_map.get(tz, "00")

    def validate_config(self, config: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate configuration before translation.

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Basic validation
        if not isinstance(config, dict):
            return False, "Configuration must be a dictionary"

        # Validate interfaces have required fields
        if "interfaces" in config:
            for iface in config["interfaces"]:
                if "name" not in iface:
                    return False, "All interfaces must have a name"

        return True, ""

    def parse_device_status(self, status_output: str) -> Dict[str, Any]:
        """Parse device status from CLI output"""
        # Parse FortiOS status output
        # This is a simplified implementation
        return {
            "status": "online",
            "parsed_data": status_output
        }

    def get_status_commands(self) -> List[str]:
        """Get commands to retrieve device status"""
        return [
            "get system status",
            "get system performance status",
            "diagnose hardware deviceinfo nic"
        ]

    def supports_feature(self, feature: str) -> bool:
        """Check if vendor supports a specific feature"""
        supported = {
            "firewall", "nat", "vpn", "routing", "vlan",
            "qos", "ips", "antivirus", "webfilter", "sdwan"
        }
        return feature.lower() in supported
