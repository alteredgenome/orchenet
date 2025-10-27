"""
Ubiquiti UniFi Configuration Translator
Translates unified YAML configuration to UniFi Controller API calls.
"""
from typing import Dict, Any, List
import yaml
from ..base import VendorInterface


class UniFiTranslator(VendorInterface):
    """
    Ubiquiti UniFi implementation of VendorInterface.
    Translates unified configuration to UniFi Controller API payloads.

    Note: UniFi doesn't use CLI commands; it uses the Controller API.
    Therefore, yaml_to_commands returns API operation dictionaries.
    """

    def yaml_to_commands(self, config: Dict[str, Any]) -> List[str]:
        """
        Convert unified YAML configuration to UniFi API operations.

        Returns list of JSON-serializable operation dictionaries describing
        API calls to be made against the UniFi Controller.

        Format:
        {
            "endpoint": "/api/s/{site}/rest/...",
            "method": "PUT/POST/DELETE",
            "data": {...}
        }
        """
        operations = []

        # System configuration
        if "system" in config:
            operations.extend(self._translate_system(config["system"]))

        # Network configuration (interfaces, VLANs)
        if "interfaces" in config or "vlans" in config:
            operations.extend(self._translate_networks(
                config.get("interfaces", []),
                config.get("vlans", [])
            ))

        # Firewall rules
        if "firewall" in config and "policies" in config["firewall"]:
            operations.extend(self._translate_firewall(config["firewall"]["policies"]))

        # Port forwarding (NAT)
        if "nat" in config:
            operations.extend(self._translate_nat(config["nat"]))

        # VPN
        if "vpn" in config:
            operations.extend(self._translate_vpn(config["vpn"]))

        # Wireless networks
        if "wireless" in config:
            operations.extend(self._translate_wireless(config["wireless"]))

        # Routing
        if "routing" in config:
            operations.extend(self._translate_routing(config["routing"]))

        # Convert to JSON strings for consistency with CLI-based vendors
        import json
        return [json.dumps(op) for op in operations]

    def _translate_system(self, system: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Translate system configuration"""
        operations = []

        site_config = {}

        if "hostname" in system:
            site_config["name"] = system["hostname"]

        if "timezone" in system:
            site_config["timezone"] = system["timezone"]

        if site_config:
            operations.append({
                "endpoint": "/api/s/{site}/rest/setting/mgmt",
                "method": "PUT",
                "data": site_config
            })

        # DNS settings
        if "dns" in system and "servers" in system["dns"]:
            operations.append({
                "endpoint": "/api/s/{site}/rest/setting/connectivity",
                "method": "PUT",
                "data": {
                    "x_ssh_enabled": True,
                    "x_ssh_bind_wildcard": False,
                    "x_ssh_auth_password_enabled": True,
                    "dns_suffix": system["dns"].get("domain", ""),
                    "uplink_type": "gateway"
                }
            })

        return operations

    def _translate_networks(
        self,
        interfaces: List[Dict[str, Any]],
        vlans: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Translate network/VLAN configuration"""
        operations = []

        # Combine interface and VLAN info
        networks_by_vlan = {}

        # Process VLANs
        for vlan in vlans:
            vlan_id = vlan.get("id")
            if not vlan_id:
                continue

            networks_by_vlan[vlan_id] = {
                "name": vlan.get("name", f"VLAN{vlan_id}"),
                "vlan_id": vlan_id,
                "enabled": vlan.get("enabled", True),
                "purpose": "corporate"
            }

        # Process interfaces to extract network info
        for iface in interfaces:
            if "vlan_id" in iface:
                vlan_id = iface["vlan_id"]
                if vlan_id not in networks_by_vlan:
                    networks_by_vlan[vlan_id] = {
                        "name": iface.get("name", f"VLAN{vlan_id}"),
                        "vlan_id": vlan_id
                    }

                # Add IP configuration
                if "addressing" in iface and iface["addressing"].get("mode") == "static":
                    ipv4 = iface["addressing"].get("ipv4", {})
                    if "address" in ipv4:
                        networks_by_vlan[vlan_id].update({
                            "dhcpd_enabled": True,
                            "dhcpd_start": ipv4.get("dhcp_start", ""),
                            "dhcpd_stop": ipv4.get("dhcp_end", ""),
                            "ip_subnet": ipv4["address"],
                            "gateway_type": "default"
                        })

        # Create network creation operations
        for network_data in networks_by_vlan.values():
            operations.append({
                "endpoint": "/api/s/{site}/rest/networkconf",
                "method": "POST",
                "data": network_data
            })

        return operations

    def _translate_firewall(self, policies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Translate firewall rules"""
        operations = []

        for policy in policies:
            rule_data = {
                "name": policy.get("name", "Firewall Rule"),
                "enabled": policy.get("enabled", True),
                "action": "accept" if policy.get("action") == "accept" else "drop",
                "protocol_match_excepted": False,
                "logging": policy.get("log", False),
                "state_established": True,
                "state_invalid": False,
                "state_new": True,
                "state_related": True
            }

            # Source
            if "source_address" in policy:
                src = policy["source_address"]
                if isinstance(src, list):
                    src = src[0]
                if src != "any":
                    rule_data["src_address"] = src

            # Destination
            if "destination_address" in policy:
                dst = policy["destination_address"]
                if isinstance(dst, list):
                    dst = dst[0]
                if dst != "any":
                    rule_data["dst_address"] = dst

            # Service/Protocol
            if "service" in policy:
                service = policy["service"]
                if isinstance(service, list):
                    service = service[0]

                # Map common services
                if service.lower() == "http":
                    rule_data["dst_port"] = "80"
                    rule_data["protocol"] = "tcp"
                elif service.lower() == "https":
                    rule_data["dst_port"] = "443"
                    rule_data["protocol"] = "tcp"
                elif service.lower() == "ssh":
                    rule_data["dst_port"] = "22"
                    rule_data["protocol"] = "tcp"

            operations.append({
                "endpoint": "/api/s/{site}/rest/firewallrule",
                "method": "POST",
                "data": rule_data
            })

        return operations

    def _translate_nat(self, nat: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Translate NAT/port forwarding configuration"""
        operations = []

        if "port_forwarding" in nat:
            for rule in nat["port_forwarding"]:
                pf_data = {
                    "name": rule.get("name", "Port Forward"),
                    "enabled": rule.get("enabled", True),
                    "src": "wan",
                    "dst_port": str(rule.get("external_port", "")),
                    "fwd": rule.get("internal_address", ""),
                    "fwd_port": str(rule.get("internal_port", "")),
                    "proto": rule.get("protocol", "tcp_udp"),
                    "log": rule.get("log", False)
                }

                operations.append({
                    "endpoint": "/api/s/{site}/rest/portforward",
                    "method": "POST",
                    "data": pf_data
                })

        return operations

    def _translate_vpn(self, vpn: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Translate VPN configuration"""
        operations = []

        if "ipsec" in vpn:
            for tunnel in vpn["ipsec"]:
                vpn_data = {
                    "name": tunnel.get("name", "VPN"),
                    "enabled": tunnel.get("enabled", True),
                    "ipsec_local_ip": tunnel.get("local_ip", ""),
                    "ipsec_peer_ip": tunnel.get("remote_gateway", ""),
                    "ipsec_preshared_key": tunnel.get("preshared_key", ""),
                    "ipsec_local_subnet": tunnel.get("local_subnet", ""),
                    "ipsec_remote_subnet": tunnel.get("remote_subnet", "")
                }

                operations.append({
                    "endpoint": "/api/s/{site}/rest/vpn/ipsec",
                    "method": "POST",
                    "data": vpn_data
                })

        if "wireguard" in vpn:
            # WireGuard support in newer UniFi versions
            for peer in vpn["wireguard"]:
                wg_data = {
                    "name": peer.get("name", "WireGuard"),
                    "enabled": peer.get("enabled", True),
                    "wireguard_public_key": peer.get("public_key", ""),
                    "wireguard_allowed_ips": peer.get("allowed_ips", [])
                }

                operations.append({
                    "endpoint": "/api/s/{site}/rest/vpn/wireguard",
                    "method": "POST",
                    "data": wg_data
                })

        return operations

    def _translate_wireless(self, wireless: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Translate wireless network configuration"""
        operations = []

        if "ssids" in wireless:
            for ssid in wireless["ssids"]:
                wlan_data = {
                    "name": ssid.get("ssid", "WiFi"),
                    "enabled": ssid.get("enabled", True),
                    "security": ssid.get("encryption", "wpapsk"),
                    "wpa_mode": "wpa2",
                    "wpa_enc": "ccmp",
                    "x_passphrase": ssid.get("psk", ""),
                    "usergroup_id": "",
                    "wlangroup_id": "",
                    "hide_ssid": ssid.get("hidden", False),
                    "is_guest": ssid.get("guest_network", False),
                    "vlan_enabled": "vlan_id" in ssid,
                }

                if "vlan_id" in ssid:
                    wlan_data["vlan"] = ssid["vlan_id"]

                operations.append({
                    "endpoint": "/api/s/{site}/rest/wlanconf",
                    "method": "POST",
                    "data": wlan_data
                })

        return operations

    def _translate_routing(self, routing: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Translate routing configuration"""
        operations = []

        if "static" in routing:
            for route in routing["static"]:
                route_data = {
                    "enabled": route.get("enabled", True),
                    "static-route_network": route.get("destination", "0.0.0.0/0"),
                    "static-route_nexthop": route.get("gateway", ""),
                    "static-route_distance": route.get("distance", 1),
                    "static-route_type": "nexthop-route"
                }

                operations.append({
                    "endpoint": "/api/s/{site}/rest/routing",
                    "method": "POST",
                    "data": route_data
                })

        return operations

    def validate_config(self, config: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate configuration before translation.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(config, dict):
            return False, "Configuration must be a dictionary"

        # Validate wireless SSIDs
        if "wireless" in config and "ssids" in config["wireless"]:
            for ssid in config["wireless"]["ssids"]:
                if "ssid" not in ssid:
                    return False, "All wireless networks must have an SSID"

        return True, ""

    def parse_device_status(self, status_output: str) -> Dict[str, Any]:
        """Parse device status from API response"""
        # For UniFi, status comes from Controller API, not CLI
        import json
        try:
            return json.loads(status_output)
        except:
            return {"status": "online", "raw": status_output}

    def get_status_commands(self) -> List[str]:
        """Get API endpoints to retrieve device status"""
        # Return API endpoints instead of commands
        return [
            "GET /api/s/{site}/stat/device",
            "GET /api/s/{site}/stat/sysinfo"
        ]

    def supports_feature(self, feature: str) -> bool:
        """Check if UniFi supports a specific feature"""
        supported = {
            "firewall", "nat", "vpn", "routing", "vlan",
            "wireless", "qos", "dpi", "threat_management", "guest_portal"
        }
        return feature.lower() in supported
