"""
MikroTik RouterOS YAML to command translator
"""
from typing import Dict, List, Any
from ..base import VendorInterface


class MikroTikTranslator(VendorInterface):
    """MikroTik RouterOS implementation of vendor interface"""

    SUPPORTED_FEATURES = {
        "interfaces",
        "ip_addresses",
        "ip_routes",
        "ip_firewall",
        "dhcp_server",
        "dhcp_client",
        "dns",
        "ntp",
        "wireless",
        "bridge",
        "vlan",
        "users",
        "snmp",
        "logging",
        "system",
    }

    def yaml_to_commands(self, config: Dict[str, Any]) -> List[str]:
        """Convert YAML config to RouterOS commands"""
        commands = []

        # Process each configuration section
        if "system" in config:
            commands.extend(self._translate_system(config["system"]))

        if "interfaces" in config:
            commands.extend(self._translate_interfaces(config["interfaces"]))

        if "ip" in config:
            commands.extend(self._translate_ip(config["ip"]))

        if "bridge" in config:
            commands.extend(self._translate_bridge(config["bridge"]))

        if "wireless" in config:
            commands.extend(self._translate_wireless(config["wireless"]))

        if "users" in config:
            commands.extend(self._translate_users(config["users"]))

        return commands

    def validate_config(self, config: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate MikroTik configuration"""
        errors = []

        # Check for unknown sections
        for section in config.keys():
            if section not in self.SUPPORTED_FEATURES:
                errors.append(f"Unknown configuration section: {section}")

        return (len(errors) == 0, errors)

    def parse_device_status(self, raw_status: str) -> Dict[str, Any]:
        """Parse RouterOS status output"""
        # TODO: Implement RouterOS status parsing
        return {}

    def get_status_commands(self) -> List[str]:
        """Get status collection commands for RouterOS"""
        return [
            "/system resource print",
            "/system identity print",
            "/interface print stats",
            "/ip address print",
            "/system routerboard print",
        ]

    def supports_feature(self, feature: str) -> bool:
        """Check if feature is supported"""
        return feature in self.SUPPORTED_FEATURES

    # Helper methods for translating specific sections

    def _translate_system(self, system: Dict[str, Any]) -> List[str]:
        """Translate system configuration"""
        commands = []

        if "identity" in system:
            commands.append(f"/system identity set name={system['identity']}")

        if "ntp" in system:
            ntp = system["ntp"]
            if "enabled" in ntp:
                enabled = "yes" if ntp["enabled"] else "no"
                commands.append(f"/system ntp client set enabled={enabled}")
            if "servers" in ntp:
                for server in ntp["servers"]:
                    commands.append(f"/system ntp client servers add address={server}")

        if "clock" in system:
            clock = system["clock"]
            if "timezone" in clock:
                commands.append(f"/system clock set time-zone-name={clock['timezone']}")

        return commands

    def _translate_interfaces(self, interfaces: List[Dict[str, Any]]) -> List[str]:
        """Translate interface configuration"""
        commands = []

        for iface in interfaces:
            name = iface.get("name")
            if not name:
                continue

            # Enable/disable
            if "enabled" in iface:
                disabled = "no" if iface["enabled"] else "yes"
                commands.append(f"/interface set {name} disabled={disabled}")

            # Comment
            if "comment" in iface:
                commands.append(f"/interface set {name} comment=\"{iface['comment']}\"")

            # MTU
            if "mtu" in iface:
                commands.append(f"/interface set {name} mtu={iface['mtu']}")

        return commands

    def _translate_ip(self, ip_config: Dict[str, Any]) -> List[str]:
        """Translate IP configuration"""
        commands = []

        # Addresses
        if "addresses" in ip_config:
            for addr in ip_config["addresses"]:
                interface = addr.get("interface")
                address = addr.get("address")
                if interface and address:
                    cmd = f"/ip address add interface={interface} address={address}"
                    if "comment" in addr:
                        cmd += f" comment=\"{addr['comment']}\""
                    commands.append(cmd)

        # Routes
        if "routes" in ip_config:
            for route in ip_config["routes"]:
                dst = route.get("dst_address", "0.0.0.0/0")
                gateway = route.get("gateway")
                if gateway:
                    cmd = f"/ip route add dst-address={dst} gateway={gateway}"
                    if "distance" in route:
                        cmd += f" distance={route['distance']}"
                    if "comment" in route:
                        cmd += f" comment=\"{route['comment']}\""
                    commands.append(cmd)

        # DNS
        if "dns" in ip_config:
            dns = ip_config["dns"]
            if "servers" in dns:
                servers = ",".join(dns["servers"])
                commands.append(f"/ip dns set servers={servers}")
            if "allow_remote_requests" in dns:
                allow = "yes" if dns["allow_remote_requests"] else "no"
                commands.append(f"/ip dns set allow-remote-requests={allow}")

        # DHCP Server
        if "dhcp_server" in ip_config:
            for dhcp in ip_config["dhcp_server"]:
                name = dhcp.get("name")
                interface = dhcp.get("interface")
                address_pool = dhcp.get("address_pool")

                if name and interface:
                    commands.append(f"/ip dhcp-server add name={name} interface={interface} address-pool={address_pool}")

                    if "lease_time" in dhcp:
                        commands.append(f"/ip dhcp-server set {name} lease-time={dhcp['lease_time']}")

        # Firewall
        if "firewall" in ip_config:
            commands.extend(self._translate_firewall(ip_config["firewall"]))

        return commands

    def _translate_firewall(self, firewall: Dict[str, Any]) -> List[str]:
        """Translate firewall configuration"""
        commands = []

        if "filter" in firewall:
            for rule in firewall["filter"]:
                cmd_parts = ["/ip firewall filter add"]

                if "chain" in rule:
                    cmd_parts.append(f"chain={rule['chain']}")
                if "action" in rule:
                    cmd_parts.append(f"action={rule['action']}")
                if "protocol" in rule:
                    cmd_parts.append(f"protocol={rule['protocol']}")
                if "src_address" in rule:
                    cmd_parts.append(f"src-address={rule['src_address']}")
                if "dst_address" in rule:
                    cmd_parts.append(f"dst-address={rule['dst_address']}")
                if "dst_port" in rule:
                    cmd_parts.append(f"dst-port={rule['dst_port']}")
                if "in_interface" in rule:
                    cmd_parts.append(f"in-interface={rule['in_interface']}")
                if "out_interface" in rule:
                    cmd_parts.append(f"out-interface={rule['out_interface']}")
                if "comment" in rule:
                    cmd_parts.append(f"comment=\"{rule['comment']}\"")

                commands.append(" ".join(cmd_parts))

        if "nat" in firewall:
            for rule in firewall["nat"]:
                cmd_parts = ["/ip firewall nat add"]

                if "chain" in rule:
                    cmd_parts.append(f"chain={rule['chain']}")
                if "action" in rule:
                    cmd_parts.append(f"action={rule['action']}")
                if "to_addresses" in rule:
                    cmd_parts.append(f"to-addresses={rule['to_addresses']}")
                if "to_ports" in rule:
                    cmd_parts.append(f"to-ports={rule['to_ports']}")
                if "protocol" in rule:
                    cmd_parts.append(f"protocol={rule['protocol']}")
                if "dst_port" in rule:
                    cmd_parts.append(f"dst-port={rule['dst_port']}")
                if "out_interface" in rule:
                    cmd_parts.append(f"out-interface={rule['out_interface']}")
                if "comment" in rule:
                    cmd_parts.append(f"comment=\"{rule['comment']}\"")

                commands.append(" ".join(cmd_parts))

        return commands

    def _translate_bridge(self, bridge: Dict[str, Any]) -> List[str]:
        """Translate bridge configuration"""
        commands = []

        if "bridges" in bridge:
            for br in bridge["bridges"]:
                name = br.get("name")
                if name:
                    cmd = f"/interface bridge add name={name}"
                    if "comment" in br:
                        cmd += f" comment=\"{br['comment']}\""
                    commands.append(cmd)

        if "ports" in bridge:
            for port in bridge["ports"]:
                br_name = port.get("bridge")
                interface = port.get("interface")
                if br_name and interface:
                    cmd = f"/interface bridge port add bridge={br_name} interface={interface}"
                    if "pvid" in port:
                        cmd += f" pvid={port['pvid']}"
                    commands.append(cmd)

        return commands

    def _translate_wireless(self, wireless: Dict[str, Any]) -> List[str]:
        """Translate wireless configuration"""
        commands = []

        if "security_profiles" in wireless:
            for profile in wireless["security_profiles"]:
                name = profile.get("name")
                if name:
                    cmd = f"/interface wireless security-profiles add name={name}"
                    if "mode" in profile:
                        cmd += f" mode={profile['mode']}"
                    if "authentication_types" in profile:
                        auth = ",".join(profile["authentication_types"])
                        cmd += f" authentication-types={auth}"
                    if "wpa2_pre_shared_key" in profile:
                        cmd += f" wpa2-pre-shared-key={profile['wpa2_pre_shared_key']}"
                    commands.append(cmd)

        if "interfaces" in wireless:
            for iface in wireless["interfaces"]:
                name = iface.get("name")
                if name:
                    if "ssid" in iface:
                        commands.append(f"/interface wireless set {name} ssid={iface['ssid']}")
                    if "mode" in iface:
                        commands.append(f"/interface wireless set {name} mode={iface['mode']}")
                    if "security_profile" in iface:
                        commands.append(f"/interface wireless set {name} security-profile={iface['security_profile']}")
                    if "frequency" in iface:
                        commands.append(f"/interface wireless set {name} frequency={iface['frequency']}")

        return commands

    def _translate_users(self, users: List[Dict[str, Any]]) -> List[str]:
        """Translate user configuration"""
        commands = []

        for user in users:
            name = user.get("name")
            if name:
                cmd = f"/user add name={name}"
                if "group" in user:
                    cmd += f" group={user['group']}"
                if "password" in user:
                    cmd += f" password={user['password']}"
                commands.append(cmd)

        return commands
