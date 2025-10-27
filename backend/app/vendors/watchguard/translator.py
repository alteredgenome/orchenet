"""
WatchGuard Fireware Configuration Translator
Translates unified YAML configuration to WatchGuard CLI commands.
"""
from typing import Dict, Any, List
import yaml
from ..base import VendorInterface


class WatchGuardTranslator(VendorInterface):
    """
    WatchGuard Fireware implementation of VendorInterface.
    Translates unified configuration to WatchGuard CLI commands.

    Note: WatchGuard primarily uses XML-based configuration,
    but also supports CLI for certain operations.
    """

    def yaml_to_commands(self, config: Dict[str, Any]) -> List[str]:
        """
        Convert unified YAML configuration to WatchGuard CLI commands.

        Args:
            config: Unified configuration dictionary

        Returns:
            List of WatchGuard CLI commands
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

        if "hostname" in system:
            commands.append(f"set hostname {system['hostname']}")

        if "timezone" in system:
            commands.append(f"set timezone {system['timezone']}")

        if "dns" in system and "servers" in system["dns"]:
            for idx, server in enumerate(system["dns"]["servers"]):
                commands.append(f"set dns-server {idx + 1} {server}")

        if "ntp" in system and "servers" in system["ntp"]:
            for server in system["ntp"]["servers"]:
                commands.append(f"set ntp-server {server}")

        return commands

    def _translate_interfaces(self, interfaces: List[Dict[str, Any]]) -> List[str]:
        """Translate interface configuration"""
        commands = []

        for iface in interfaces:
            name = iface.get("name")
            if not name:
                continue

            # Map interface name to WatchGuard format (eth0, eth1, etc.)
            wg_name = self._map_interface_name(name)

            if "description" in iface:
                commands.append(f"set interface {wg_name} description \"{iface['description']}\"")

            if "enabled" in iface:
                status = "enabled" if iface["enabled"] else "disabled"
                commands.append(f"set interface {wg_name} {status}")

            # Addressing
            if "addressing" in iface:
                addr = iface["addressing"]
                if addr.get("mode") == "static" and "ipv4" in addr:
                    ip = addr["ipv4"].get("address")
                    netmask = addr["ipv4"].get("netmask", "255.255.255.0")
                    commands.append(f"set interface {wg_name} ip {ip} netmask {netmask}")
                elif addr.get("mode") == "dhcp":
                    commands.append(f"set interface {wg_name} dhcp")

            # Zone assignment (WatchGuard uses zones: Trusted, Optional, External)
            if "zone" in iface:
                wg_zone = self._map_zone(iface["zone"])
                commands.append(f"set interface {wg_name} zone {wg_zone}")

        return commands

    def _translate_vlans(self, vlans: List[Dict[str, Any]]) -> List[str]:
        """Translate VLAN configuration"""
        commands = []

        for vlan in vlans:
            vlan_id = vlan.get("id")
            if not vlan_id:
                continue

            name = vlan.get("name", f"VLAN{vlan_id}")
            parent = vlan.get("interface", "eth0")

            commands.append(f"add vlan {vlan_id} name {name} interface {parent}")

            if "description" in vlan:
                commands.append(f"set vlan {vlan_id} description \"{vlan['description']}\"")

        return commands

    def _translate_firewall_policies(self, policies: List[Dict[str, Any]]) -> List[str]:
        """Translate firewall policies"""
        commands = []

        for idx, policy in enumerate(policies):
            policy_name = policy.get("name", f"Policy-{idx + 1}")

            # WatchGuard uses a different policy syntax
            # Create policy with from-zone to-zone action
            src_zone = policy.get("source_zone", "any")
            dst_zone = policy.get("destination_zone", "any")
            action = policy.get("action", "accept")

            # Map zones
            src_zone_wg = self._map_zone(src_zone) if src_zone != "any" else "any"
            dst_zone_wg = self._map_zone(dst_zone) if dst_zone != "any" else "any"

            # Create policy
            commands.append(f"add policy name \"{policy_name}\"")
            commands.append(f"set policy \"{policy_name}\" from {src_zone_wg} to {dst_zone_wg}")
            commands.append(f"set policy \"{policy_name}\" action {action}")

            # Source addresses
            src_addr = policy.get("source_address", ["any"])
            if isinstance(src_addr, str):
                src_addr = [src_addr]
            for addr in src_addr:
                if addr != "any":
                    commands.append(f"set policy \"{policy_name}\" source {addr}")

            # Destination addresses
            dst_addr = policy.get("destination_address", ["any"])
            if isinstance(dst_addr, str):
                dst_addr = [dst_addr]
            for addr in dst_addr:
                if addr != "any":
                    commands.append(f"set policy \"{policy_name}\" destination {addr}")

            # Services
            services = policy.get("service", ["any"])
            if isinstance(services, str):
                services = [services]
            for service in services:
                commands.append(f"set policy \"{policy_name}\" service {service}")

            # NAT
            if policy.get("nat"):
                commands.append(f"set policy \"{policy_name}\" nat enabled")

            # Logging
            if policy.get("log"):
                commands.append(f"set policy \"{policy_name}\" logging enabled")

            # Enable policy
            commands.append(f"set policy \"{policy_name}\" enabled")

        return commands

    def _translate_nat(self, nat: Dict[str, Any]) -> List[str]:
        """Translate NAT configuration"""
        commands = []

        # SNAT (Source NAT)
        if "source_nat" in nat:
            for rule in nat["source_nat"]:
                name = rule.get("name", "SNAT")
                commands.append(f"add nat-rule source name \"{name}\"")

                if "source_address" in rule:
                    commands.append(f"set nat-rule source \"{name}\" from {rule['source_address']}")

                if "translated_address" in rule:
                    commands.append(f"set nat-rule source \"{name}\" to {rule['translated_address']}")

        # DNAT (Port Forwarding)
        if "port_forwarding" in nat:
            for rule in nat["port_forwarding"]:
                name = rule.get("name", "Port Forward")
                commands.append(f"add nat-rule destination name \"{name}\"")

                ext_port = rule.get("external_port")
                int_addr = rule.get("internal_address")
                int_port = rule.get("internal_port")
                protocol = rule.get("protocol", "tcp")

                commands.append(f"set nat-rule destination \"{name}\" external-port {ext_port}")
                commands.append(f"set nat-rule destination \"{name}\" internal-address {int_addr}")
                commands.append(f"set nat-rule destination \"{name}\" internal-port {int_port}")
                commands.append(f"set nat-rule destination \"{name}\" protocol {protocol}")

        return commands

    def _translate_vpn(self, vpn: Dict[str, Any]) -> List[str]:
        """Translate VPN configuration"""
        commands = []

        if "ipsec" in vpn:
            for tunnel in vpn["ipsec"]:
                name = tunnel.get("name", "VPN")

                commands.append(f"add vpn ipsec name \"{name}\"")
                commands.append(f"set vpn ipsec \"{name}\" gateway {tunnel.get('remote_gateway')}")
                commands.append(f"set vpn ipsec \"{name}\" psk \"{tunnel.get('preshared_key', '')}\"")

                if "local_subnet" in tunnel:
                    commands.append(f"set vpn ipsec \"{name}\" local-network {tunnel['local_subnet']}")

                if "remote_subnet" in tunnel:
                    commands.append(f"set vpn ipsec \"{name}\" remote-network {tunnel['remote_subnet']}")

                # Phase 1 settings
                if "phase1" in tunnel:
                    p1 = tunnel["phase1"]
                    if "encryption" in p1:
                        commands.append(f"set vpn ipsec \"{name}\" phase1-encryption {p1['encryption']}")
                    if "authentication" in p1:
                        commands.append(f"set vpn ipsec \"{name}\" phase1-authentication {p1['authentication']}")
                    if "dh_group" in p1:
                        commands.append(f"set vpn ipsec \"{name}\" phase1-dhgroup {p1['dh_group']}")

                commands.append(f"set vpn ipsec \"{name}\" enabled")

        return commands

    def _translate_routing(self, routing: Dict[str, Any]) -> List[str]:
        """Translate routing configuration"""
        commands = []

        if "static" in routing:
            for route in routing["static"]:
                dest = route.get("destination", "0.0.0.0/0")
                gateway = route.get("gateway")
                distance = route.get("distance", 1)

                commands.append(f"add route {dest} gateway {gateway} metric {distance}")

        return commands

    def _map_interface_name(self, name: str) -> str:
        """Map generic interface name to WatchGuard format"""
        # Simple mapping - expand as needed
        mapping = {
            "wan": "eth0",
            "wan1": "eth0",
            "lan": "eth1",
            "lan1": "eth1",
            "dmz": "eth2"
        }
        return mapping.get(name.lower(), name)

    def _map_zone(self, zone: str) -> str:
        """Map generic zone to WatchGuard zone"""
        mapping = {
            "wan": "External",
            "lan": "Trusted",
            "dmz": "Optional",
            "guest": "Optional"
        }
        return mapping.get(zone.lower(), "Trusted")

    def validate_config(self, config: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate configuration before translation.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(config, dict):
            return False, "Configuration must be a dictionary"

        # Validate interfaces
        if "interfaces" in config:
            for iface in config["interfaces"]:
                if "name" not in iface:
                    return False, "All interfaces must have a name"

        return True, ""

    def parse_device_status(self, status_output: str) -> Dict[str, Any]:
        """Parse device status from CLI output"""
        # Parse WatchGuard status output
        return {
            "status": "online",
            "parsed_data": status_output
        }

    def get_status_commands(self) -> List[str]:
        """Get commands to retrieve device status"""
        return [
            "show system status",
            "show interface",
            "show policy"
        ]

    def supports_feature(self, feature: str) -> bool:
        """Check if WatchGuard supports a specific feature"""
        supported = {
            "firewall", "nat", "vpn", "routing", "vlan",
            "ips", "antivirus", "reputation_defense", "apt_blocker",
            "data_loss_prevention", "application_control"
        }
        return feature.lower() in supported
