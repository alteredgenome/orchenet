# OrcheNet Configuration Schema - Ubiquiti UniFi

This document defines the complete YAML configuration schema for managing Ubiquiti UniFi devices through OrcheNet. This includes UniFi Dream Machine/Gateway routers, UniFi Switches, and UniFi Access Points.

## UniFi Configuration Overview

UniFi devices are managed through the UniFi Controller/Network Application. OrcheNet translates vendor-agnostic YAML into UniFi API calls and configuration objects. Unlike traditional CLI-based devices, UniFi uses a centralized controller with a REST API.

---

## Table of Contents

### UniFi Dream Machine / Gateway
- [System Settings](#unifi-system-settings)
- [Networks (VLANs)](#unifi-networks)
- [WiFi Networks](#unifi-wifi-networks)
- [Port Forwarding](#unifi-port-forwarding)
- [Firewall Rules](#unifi-firewall-rules)
- [Traffic Routes](#unifi-traffic-routes)
- [VPN](#unifi-vpn)
- [DPI & Traffic Management](#unifi-dpi-traffic-management)
- [Threat Management](#unifi-threat-management)
- [User Groups](#unifi-user-groups)

### UniFi Switches
- [Switch Configuration](#unifi-switch-configuration)
- [Port Profiles](#unifi-port-profiles)
- [Port Overrides](#unifi-port-overrides)
- [Link Aggregation](#unifi-link-aggregation)
- [Storm Control](#unifi-storm-control)
- [Port Isolation](#unifi-port-isolation)

### UniFi Access Points
- [AP Configuration](#unifi-ap-configuration)
- [Radio Settings](#unifi-radio-settings)
- [WLAN Groups](#unifi-wlan-groups)
- [Guest Control](#unifi-guest-control)

---

# UniFi Dream Machine / Gateway Configuration

## UniFi System Settings

Global system configuration for UniFi Dream Machine or UniFi Gateway.

```yaml
unifi:
  system:
    site:
      name: "default"
      desc: "Main Site"
      timezone: "America/New_York"

    # Controller settings
    settings:
      # Site configuration
      name: "HQ Network"

      # Management
      advanced:
        # SSH
        ssh_enabled: true
        ssh_port: 22
        ssh_keys: []

      # Auto optimization
      auto_upgrade: false

      # Connectivity monitoring
      connectivity_monitor_enabled: true

      # DPI
      dpi:
        enabled: true

      # mDNS
      mdns_enabled: true
      upnp_enabled: false

      # NTP
      ntp:
        ntp_server_1: "pool.ntp.org"
        ntp_server_2: "time.google.com"
        ntp_server_3: ""
        ntp_server_4: ""

      # SNMP
      snmp:
        enabled: false
        community: "public"
        contact: "admin@example.com"
        location: "Datacenter"

    # Admin accounts
    admin:
      - name: "admin"
        email: "admin@example.com"
        password: "secure-password"
        role: "admin"
        permissions: []

      - name: "readonly"
        email: "readonly@example.com"
        password: "readonly-password"
        role: "readonly"
```

---

## UniFi Networks

Network/VLAN configuration (LAN, VLAN, WAN).

```yaml
unifi:
  networks:
    # Default LAN
    - name: "Default"
      purpose: "corporate"
      vlan_enabled: false
      dhcp_enabled: true
      dhcpd_start: "192.168.1.100"
      dhcpd_stop: "192.168.1.254"
      dhcpd_dns_1: "192.168.1.1"
      dhcpd_dns_2: "1.1.1.1"
      dhcpd_gateway: "192.168.1.1"
      dhcpd_leasetime: 86400
      dhcpd_boot_enabled: false
      ipv6_interface_type: "none"

      # Network addressing
      ip_subnet: "192.168.1.1/24"
      networkgroup: "LAN"

      # Domain
      domain_name: "local.lan"

      # IGMP Snooping
      igmp_snooping: true

      # Auto Scale
      auto_scale_enabled: false

    # Management VLAN
    - name: "Management"
      purpose: "corporate"
      vlan_enabled: true
      vlan: 10
      dhcp_enabled: true
      dhcpd_start: "192.168.10.100"
      dhcpd_stop: "192.168.10.200"
      dhcpd_dns_1: "192.168.10.1"
      dhcpd_dns_2: "1.1.1.1"
      dhcpd_gateway: "192.168.10.1"
      dhcpd_leasetime: 86400

      ip_subnet: "192.168.10.1/24"
      networkgroup: "LAN"
      igmp_snooping: true

    # Guest Network
    - name: "Guest"
      purpose: "guest"
      vlan_enabled: true
      vlan: 20
      dhcp_enabled: true
      dhcpd_start: "192.168.20.50"
      dhcpd_stop: "192.168.20.200"
      dhcpd_dns_1: "192.168.20.1"
      dhcpd_dns_2: "1.1.1.1"
      dhcpd_gateway: "192.168.20.1"
      dhcpd_leasetime: 3600

      ip_subnet: "192.168.20.1/24"
      networkgroup: "LAN"

      # Guest settings
      is_guest: true
      guest_portal_enabled: true
      guest_portal_customized: false

      # Isolation
      isolation: true

    # IoT Network
    - name: "IoT"
      purpose: "corporate"
      vlan_enabled: true
      vlan: 30
      dhcp_enabled: true
      dhcpd_start: "192.168.30.100"
      dhcpd_stop: "192.168.30.250"
      dhcpd_dns_1: "192.168.30.1"
      dhcpd_gateway: "192.168.30.1"
      dhcpd_leasetime: 86400

      ip_subnet: "192.168.30.1/24"
      networkgroup: "LAN"
      igmp_snooping: true
      isolation: false

    # WAN Network
    - name: "WAN"
      purpose: "wan"
      wan_networkgroup: "WAN"
      wan_type: "dhcp"  # dhcp, static, pppoe
      wan_dhcp_v6: false
      wan_egress_qos: 0
      wan_type_v6: "disabled"

      # For static WAN:
      # wan_type: "static"
      # wan_ip: "203.0.113.10"
      # wan_netmask: "255.255.255.252"
      # wan_gateway: "203.0.113.9"
      # wan_dns1: "1.1.1.1"
      # wan_dns2: "8.8.8.8"

    # WAN2 (Failover)
    - name: "WAN2"
      purpose: "wan"
      wan_networkgroup: "WAN2"
      wan_type: "dhcp"
      wan_load_balance_type: "failover-only"
      wan_load_balance_weight: 1

    # DHCP Relay
    - name: "ServerVLAN"
      purpose: "corporate"
      vlan_enabled: true
      vlan: 100
      dhcp_enabled: false
      dhcp_relay_enabled: true
      dhcpd_ip_1: "192.168.1.100"  # DHCP server IP

      ip_subnet: "192.168.100.1/24"
      networkgroup: "LAN"
```

---

## UniFi WiFi Networks

Wireless network (WLAN/SSID) configuration.

```yaml
unifi:
  wlans:
    # Corporate WiFi
    - name: "Corporate"
      enabled: true
      security: "wpapsk"  # open, wpapsk, wpaeap
      wpa_mode: "wpa2"  # wpa, wpa2, wpa3
      wpa_enc: "ccmp"  # ccmp (AES), tkip
      x_passphrase: "CorporateWiFiPassword123"

      # Network assignment
      networkconf_id: "Default"  # References network name
      usergroup_id: "Default"

      # VLAN (if different from network default)
      vlan_enabled: false

      # Broadcast
      hide_ssid: false

      # Band steering
      bandsteering_mode: "prefer-5g"  # off, equal, prefer-5g

      # AP group (optional - applies to specific APs)
      # ap_group_ids: ["default"]

      # Guest portal
      is_guest: false

      # Fast roaming
      fast_roaming_enabled: true

      # Rate limiting
      usergroup_id: "Default"

      # Multicast enhancement
      multicast_enhance_enabled: false

      # BSS transition
      bss_transition_enabled: true

      # UAPSD
      uapsd_enabled: false

      # Schedule
      schedule_enabled: false
      # schedule: []

    # Guest WiFi
    - name: "Guest"
      enabled: true
      security: "wpapsk"
      wpa_mode: "wpa2"
      wpa_enc: "ccmp"
      x_passphrase: "GuestPassword456"

      networkconf_id: "Guest"
      usergroup_id: "Guest"

      hide_ssid: false
      is_guest: true

      # Guest portal
      portal_enabled: true
      portal_customized: false
      portal_use_hostname: false

      # Guest policy
      auth_cache: 0

      # Isolation
      no2ghz_oui: false

      # Rate limiting (per client)
      usergroup_id: "Guest"

    # IoT WiFi (2.4GHz only)
    - name: "IoT"
      enabled: true
      security: "wpapsk"
      wpa_mode: "wpa2"
      wpa_enc: "ccmp"
      x_passphrase: "IoTSecurePass789"

      networkconf_id: "IoT"

      hide_ssid: true
      is_guest: false

      # Disable 5GHz
      ng_enabled: true   # 2.4GHz enabled
      na_enabled: false  # 5GHz disabled

      # Minimum RSSI
      minrssi_enabled: true
      minrssi: -75

    # Enterprise WiFi (802.1X)
    - name: "Enterprise"
      enabled: true
      security: "wpaeap"
      wpa_mode: "wpa2"
      wpa_enc: "ccmp"

      networkconf_id: "Default"

      # RADIUS settings
      radiusprofile_id: "radius_profile_1"

      # Advanced
      fast_roaming_enabled: true
      pmf_mode: "optional"  # disabled, optional, required

    # WPA3 WiFi
    - name: "Secure"
      enabled: true
      security: "wpapsk"
      wpa_mode: "wpa3"
      wpa_enc: "ccmp"
      x_passphrase: "WPA3SecurePassword!"

      networkconf_id: "Default"

      # WPA3 settings
      sae_enabled: true
      pmf_mode: "required"
```

---

## UniFi Port Forwarding

Port forwarding / destination NAT rules.

```yaml
unifi:
  portforward:
    - name: "Web Server"
      enabled: true
      src: "any"  # Source (any, or specific network name)
      dst_port: "80"
      fwd: "192.168.1.100"  # Internal IP
      fwd_port: "80"
      proto: "tcp_udp"  # tcp, udp, tcp_udp
      log: false

    - name: "HTTPS Server"
      enabled: true
      src: "any"
      dst_port: "443"
      fwd: "192.168.1.100"
      fwd_port: "443"
      proto: "tcp"
      log: true

    - name: "SSH Access"
      enabled: true
      src: "any"
      dst_port: "2222"
      fwd: "192.168.1.50"
      fwd_port: "22"
      proto: "tcp"
      log: true

    - name: "Port Range Forward"
      enabled: true
      src: "any"
      dst_port: "8000-8100"
      fwd: "192.168.1.200"
      fwd_port: "8000-8100"
      proto: "tcp"
      log: false
```

---

## UniFi Firewall Rules

Firewall rules for traffic control.

```yaml
unifi:
  firewallrules:
    # LAN In rules (traffic to router)
    - name: "Block Guest to LAN"
      enabled: true
      action: "drop"
      ruleset: "LAN_IN"
      rule_index: 2000

      # Source
      src_firewallgroup_ids: []
      src_mac_address: ""
      src_address: ""
      src_networkconf_id: "Guest"
      src_networkconf_type: "NETv4"

      # Destination
      dst_firewallgroup_ids: []
      dst_address: "192.168.1.0/24"
      dst_networkconf_type: "NETv4"

      # Protocol
      protocol: "all"

      # Logging
      logging: true

      # State
      state_established: false
      state_invalid: false
      state_new: false
      state_related: false

    # LAN Out rules (traffic from router)
    - name: "Allow Established"
      enabled: true
      action: "accept"
      ruleset: "LAN_OUT"
      rule_index: 2000

      protocol: "all"
      state_established: true
      state_related: true
      logging: false

    # WAN In rules (inbound from internet)
    - name: "Drop Invalid"
      enabled: true
      action: "drop"
      ruleset: "WAN_IN"
      rule_index: 2000

      protocol: "all"
      state_invalid: true
      logging: true

    # WAN Out rules (outbound to internet)
    - name: "Allow LAN to Internet"
      enabled: true
      action: "accept"
      ruleset: "WAN_OUT"
      rule_index: 2000

      src_networkconf_id: "Default"
      protocol: "all"
      logging: false

    # WAN Local rules (traffic to router from WAN)
    - name: "Block WAN Management"
      enabled: true
      action: "drop"
      ruleset: "WAN_LOCAL"
      rule_index: 2000

      protocol: "tcp"
      dst_port: "443"
      logging: true

    # Guest rules
    - name: "Allow Guest DNS"
      enabled: true
      action: "accept"
      ruleset: "GUEST_IN"
      rule_index: 2000

      src_networkconf_id: "Guest"
      dst_networkconf_id: "Default"
      protocol: "udp"
      dst_port: "53"
      logging: false

    - name: "Block Guest to Local"
      enabled: true
      action: "drop"
      ruleset: "GUEST_IN"
      rule_index: 2001

      src_networkconf_id: "Guest"
      dst_address: "192.168.0.0/16"
      protocol: "all"
      logging: true

    # IoT isolation
    - name: "Allow IoT to Gateway"
      enabled: true
      action: "accept"
      ruleset: "LAN_IN"
      rule_index: 2010

      src_networkconf_id: "IoT"
      dst_address: "192.168.30.1/32"
      protocol: "all"
      logging: false

    - name: "Block IoT to Other VLANs"
      enabled: true
      action: "drop"
      ruleset: "LAN_IN"
      rule_index: 2011

      src_networkconf_id: "IoT"
      dst_address: "192.168.0.0/16"
      protocol: "all"
      logging: true

    # Port-specific rules
    - name: "Allow HTTP/HTTPS"
      enabled: true
      action: "accept"
      ruleset: "LAN_OUT"
      rule_index: 2020

      protocol: "tcp"
      dst_port: "80,443"
      logging: false

    # IP group rules
    - name: "Block Malicious IPs"
      enabled: true
      action: "drop"
      ruleset: "WAN_IN"
      rule_index: 1000

      src_firewallgroup_ids: ["blocked_countries"]
      protocol: "all"
      logging: true
```

---

## UniFi Traffic Routes

Static routes and policy-based routing.

```yaml
unifi:
  routes:
    # Static routes
    - name: "Internal Network"
      enabled: true
      type: "static-route"
      static_route_distance: 1
      static_route_interface: "LAN"
      static_route_nexthop: "192.168.1.254"
      static_route_network: "10.0.0.0/8"
      static_route_type: "nexthop-route"

    - name: "Blackhole Route"
      enabled: true
      type: "static-route"
      static_route_distance: 1
      static_route_network: "192.168.100.0/24"
      static_route_type: "blackhole"

    # Policy-based routing
    - name: "Guest via WAN2"
      enabled: true
      type: "policy-route"
      target_devices:
        - network: "Guest"
      gateway_type: "gateway"
      gateway_device: "WAN2"
      matching_target: "DOMAIN"

    # Load balancing
    - name: "Load Balance WANs"
      enabled: true
      type: "load-balance"
      load_balance_type: "weighted"
      load_balance_group: "failover_only"  # failover_only, weighted
      interfaces:
        - interface: "WAN"
          weight: 2
        - interface: "WAN2"
          weight: 1
```

---

## UniFi VPN

VPN configuration for site-to-site and remote access.

```yaml
unifi:
  vpn:
    # Site-to-Site VPN (IPsec)
    site_to_site:
      - name: "Remote Office VPN"
        enabled: true

        # Type
        ipsec_profile: "ike2"  # ike1, ike2

        # Local
        ipsec_local_ip: "203.0.113.10"
        ipsec_peer_ip: "198.51.100.10"

        # Authentication
        ipsec_authentication: "psk"
        ipsec_preshared_key: "your-pre-shared-key"

        # Phase 1
        ipsec_encryption: "aes256"
        ipsec_hash: "sha256"
        ipsec_dh_group: 14

        # Phase 2
        ipsec_esp_encryption: "aes256"
        ipsec_esp_hash: "sha256"
        ipsec_pfs_dh_group: 14

        # Local network
        ipsec_local_network: "192.168.1.0/24"

        # Remote network
        ipsec_remote_network: "192.168.2.0/24"

        # DPD
        ipsec_dpd_enable: true
        ipsec_dpd_interval: 30

        # Routes
        ipsec_route_distance: 30

    # L2TP Remote Access VPN
    l2tp:
      enabled: true

      # Authentication
      l2tp_gateway: "203.0.113.10"
      l2tp_preshared_key: "l2tp-psk"

      # IP pool
      l2tp_pool_start: "10.10.10.10"
      l2tp_pool_stop: "10.10.10.100"

      # DNS
      l2tp_dns_1: "192.168.1.1"
      l2tp_dns_2: "1.1.1.1"

      # Network
      l2tp_allow_weak_ciphers: false

    # OpenVPN (if supported)
    openvpn:
      enabled: false
      port: 1194
      protocol: "udp"

      # Network
      server_network: "10.20.30.0/24"
      server_netmask: "255.255.255.0"

      # DNS
      push_dns: true
      dns_1: "192.168.1.1"

      # Routes
      push_routes:
        - "192.168.1.0/24"
        - "192.168.10.0/24"

      # Encryption
      cipher: "AES-256-CBC"
      hash: "SHA256"

    # RADIUS VPN authentication
    radius:
      - name: "VPN_RADIUS"
        auth_port: 1812
        acct_port: 1813
        ip: "192.168.1.100"
        x_secret: "radius-secret"
        interim_update_interval: 3600
```

---

## UniFi DPI & Traffic Management

Deep Packet Inspection and traffic shaping.

```yaml
unifi:
  dpi:
    # DPI settings
    settings:
      enabled: true

    # Traffic restrictions
    restrictions:
      - name: "Block Social Media"
        enabled: true
        app_categories:
          - "Social"
        action: "block"
        schedule: "Business_Hours"
        target_devices:
          - network: "Default"

      - name: "Limit Streaming"
        enabled: true
        app_categories:
          - "Streaming"
        action: "limit"
        download_limit_kbps: 5000
        upload_limit_kbps: 1000
        target_devices:
          - network: "Guest"

    # QoS
    qos:
      enabled: true

      # Smart Queues
      smart_queue:
        - name: "WAN_Upload"
          enabled: true
          interface: "WAN"
          direction: "upload"
          rate_kbps: 50000  # Your upload speed

        - name: "WAN_Download"
          enabled: true
          interface: "WAN"
          direction: "download"
          rate_kbps: 200000  # Your download speed

      # Traffic rules
      traffic_rules:
        - name: "Prioritize VoIP"
          enabled: true
          matching:
            app_category: ["VoIP"]
          action:
            priority: "high"

        - name: "Prioritize Video Conferencing"
          enabled: true
          matching:
            app_category: ["Video Conferencing"]
          action:
            priority: "high"

        - name: "Limit P2P"
          enabled: true
          matching:
            app_category: ["File Sharing"]
          action:
            priority: "low"
            rate_limit_kbps: 1000
```

---

## UniFi Threat Management

IDS/IPS and security features.

```yaml
unifi:
  threat_management:
    # IPS/IDS
    ips:
      enabled: true
      mode: "detection"  # detection, prevention

      # Categories
      categories:
        - "connectivity"
        - "dos"
        - "exploit"
        - "malware"
        - "policy"
        - "scan"
        - "web"

      # Suppress rules
      suppress:
        - signature_id: 2100498
          reason: "False positive"
        - signature_id: 2103461
          reason: "Known safe traffic"

    # Honeypot
    honeypot:
      enabled: false

    # Country blocking
    country_blocking:
      enabled: true
      block_countries:
        - "CN"
        - "RU"
        - "KP"
      whitelist_networks:
        - "192.168.1.0/24"

    # AdGuard/DNS filtering
    adguard:
      enabled: true
      categories:
        - "ads"
        - "malware"
        - "phishing"
        - "trackers"
      custom_blocklist: []
      custom_allowlist: []
```

---

## UniFi User Groups

User groups for bandwidth and access control.

```yaml
unifi:
  usergroups:
    - name: "Default"
      qos_rate_max_down: -1  # -1 = unlimited
      qos_rate_max_up: -1

    - name: "Guest"
      qos_rate_max_down: 10000  # kbps
      qos_rate_max_up: 2000

    - name: "Limited"
      qos_rate_max_down: 50000
      qos_rate_max_up: 10000

    - name: "Priority"
      qos_rate_max_down: -1
      qos_rate_max_up: -1
```

---

# UniFi Switch Configuration

## UniFi Switch Configuration

Switch-level configuration and management.

```yaml
unifi:
  switches:
    - mac: "00:00:00:00:00:01"  # Switch MAC address
      name: "Switch-Main"

      # General settings
      stp_version: "rstp"  # stp, rstp, disabled
      stp_priority: 32768

      # Jumbo frames
      jumboframe_enabled: false

      # IGMP Snooping
      igmp_snooping_enabled: true

      # Flow control
      flowctrl_enabled: false

      # LLDP
      lldp_enabled: true
      lldp_med_enabled: true
```

---

## UniFi Port Profiles

Reusable port configuration profiles.

```yaml
unifi:
  port_profiles:
    # All networks trunk
    - name: "All"
      forward: "all"  # all, customize, native
      native_networkconf_id: "Default"
      speed: "auto"  # auto, 10, 100, 1000, 2500, 5000, 10000
      full_duplex: true

      # PoE
      poe_mode: "auto"  # auto, pasv24, passthrough, off

      # Storm control
      stp_port_mode: true

      # Voice VLAN
      voice_networkconf_id: ""

    # Trunk with specific VLANs
    - name: "Trunk"
      forward: "customize"
      native_networkconf_id: "Default"
      tagged_networkconf_ids:
        - "Default"
        - "Management"
        - "Guest"
        - "IoT"
      speed: "auto"
      full_duplex: true
      poe_mode: "off"

    # Access port - Default
    - name: "LAN"
      forward: "native"
      native_networkconf_id: "Default"
      speed: "auto"
      full_duplex: true
      poe_mode: "auto"
      stp_port_mode: true
      isolation: false

    # Access port - Management
    - name: "Management"
      forward: "native"
      native_networkconf_id: "Management"
      speed: "auto"
      full_duplex: true
      poe_mode: "auto"
      stp_port_mode: true

    # Access port - Guest
    - name: "Guest"
      forward: "native"
      native_networkconf_id: "Guest"
      speed: "auto"
      full_duplex: true
      poe_mode: "auto"
      stp_port_mode: true
      isolation: true

    # Access port - IoT with PoE
    - name: "IoT-PoE"
      forward: "native"
      native_networkconf_id: "IoT"
      speed: "auto"
      full_duplex: true
      poe_mode: "auto"
      stp_port_mode: true

    # Disabled
    - name: "Disabled"
      forward: "native"
      op_mode: "switch"
      port_security_enabled: false
      speed: "auto"
      full_duplex: true
      poe_mode: "off"
```

---

## UniFi Port Overrides

Per-port configuration overrides.

```yaml
unifi:
  switches:
    - mac: "00:00:00:00:00:01"
      name: "Switch-Main"

      port_overrides:
        # Port 1 - Uplink
        - port_idx: 1
          portconf_id: "All"
          name: "Uplink to Gateway"

          # Aggregate
          aggregate_num_ports: 0  # 0 = no aggregation

          # STP
          stp_port_mode: true

        # Port 2 - Server
        - port_idx: 2
          portconf_id: "LAN"
          name: "Server"
          speed: "1000"
          full_duplex: true
          poe_mode: "off"

        # Port 3-10 - Workstations
        - port_idx: 3
          portconf_id: "LAN"
          name: "Workstation 1"

        - port_idx: 4
          portconf_id: "LAN"
          name: "Workstation 2"

        # Port 11 - IP Phone with PoE
        - port_idx: 11
          portconf_id: "LAN"
          name: "IP Phone"
          poe_mode: "auto"
          voice_networkconf_id: "Management"

        # Port 20 - Guest port
        - port_idx: 20
          portconf_id: "Guest"
          name: "Guest Port"

        # Port 24 - Disabled
        - port_idx: 24
          portconf_id: "Disabled"
          name: "Unused"
          op_mode: "switch"
          port_security_enabled: false
```

---

## UniFi Link Aggregation

LAG/port channel configuration.

```yaml
unifi:
  switches:
    - mac: "00:00:00:00:00:01"
      name: "Switch-Main"

      port_overrides:
        # LAG with 2 ports
        - port_idx: 23
          portconf_id: "All"
          name: "LAG to Core"
          aggregate_num_ports: 2  # This port + next port

        # Second port in LAG (automatically configured)
        - port_idx: 24
          # Automatically part of LAG starting at port 23
```

---

## UniFi Storm Control

Broadcast/multicast storm control.

```yaml
unifi:
  switches:
    - mac: "00:00:00:00:00:01"
      name: "Switch-Main"

      # Global storm control
      stp_version: "rstp"

      port_overrides:
        - port_idx: 10
          portconf_id: "LAN"

          # Storm control per port
          stormctrl_bcast_enabled: true
          stormctrl_bcast_level: 100  # Percentage
          stormctrl_mcast_enabled: true
          stormctrl_mcast_level: 100
          stormctrl_ucast_enabled: false
          stormctrl_type: "level"  # level, pps
```

---

## UniFi Port Isolation

Port isolation (Private VLAN).

```yaml
unifi:
  switches:
    - mac: "00:00:00:00:00:01"
      name: "Switch-Main"

      port_overrides:
        # Isolated ports (can't communicate with each other)
        - port_idx: 5
          portconf_id: "Guest"
          isolation: true

        - port_idx: 6
          portconf_id: "Guest"
          isolation: true

        - port_idx: 7
          portconf_id: "Guest"
          isolation: true
```

---

# UniFi Access Point Configuration

## UniFi AP Configuration

Access Point device configuration.

```yaml
unifi:
  access_points:
    - mac: "00:00:00:00:00:02"  # AP MAC address
      name: "AP-Office"

      # Wireless uplink (for mesh)
      uplink_type: "wired"  # wired, wireless

      # LED
      led_override: "default"  # default, on, off
      led_override_color: "#0000ff"
      led_override_color_brightness: 100

      # Location
      x: 50.5
      y: 75.2
      map_id: "floor1"

      # Power
      outlet_overrides:
        - index: 1
          name: "Port 1"
          relay_state: true
          cycle_enabled: false
```

---

## UniFi Radio Settings

Radio (2.4GHz and 5GHz) configuration.

```yaml
unifi:
  access_points:
    - mac: "00:00:00:00:00:02"
      name: "AP-Office"

      # 2.4GHz Radio
      radio_table:
        - name: "ng"  # 2.4GHz
          radio: "ng"

          # Channel
          channel: "auto"  # auto, or specific channel 1-11
          ht: "20"  # 20, 40

          # Power
          tx_power_mode: "auto"  # auto, medium, high, low, custom
          tx_power: ""  # dBm if custom

          # Min RSSI
          min_rssi_enabled: false
          min_rssi: -75

          # Rates
          min_rate_ng_enabled: false
          min_rate_ng_cck: 1
          min_rate_ng_ofdm: 6

          # Beacon rate
          min_rate_ng_beacon_rate_kbps: 1000

          # Advanced
          antenna_gain: 6
          sens_level_enabled: false

        # 5GHz Radio
        - name: "na"  # 5GHz
          radio: "na"

          channel: "auto"
          ht: "80"  # 20, 40, 80, 160

          tx_power_mode: "auto"

          min_rssi_enabled: false
          min_rssi: -70

          # DFS
          hard_noise_floor_enabled: false

          # Rates
          min_rate_na_enabled: false
          min_rate_na_beacon_rate_kbps: 6000
          min_rate_na_data_rate_kbps: 6000
          min_rate_na_mgmt_rate_kbps: 6000

    # AP with custom radio settings
    - mac: "00:00:00:00:00:03"
      name: "AP-Warehouse"

      radio_table:
        - name: "ng"
          radio: "ng"
          channel: 6  # Fixed channel
          ht: "20"
          tx_power_mode: "high"

        - name: "na"
          radio: "na"
          channel: 44
          ht: "40"
          tx_power_mode: "high"
```

---

## UniFi WLAN Groups

WLAN groups for applying SSIDs to specific APs.

```yaml
unifi:
  wlangroups:
    - name: "Default"
      wlan_ids:
        - "Corporate"
        - "Guest"
        - "IoT"

    - name: "Public-APs"
      wlan_ids:
        - "Guest"

    - name: "Office-Only"
      wlan_ids:
        - "Corporate"
        - "IoT"

  # Apply WLAN group to APs
  access_points:
    - mac: "00:00:00:00:00:02"
      name: "AP-Office"
      wlangroup_id: "Default"

    - mac: "00:00:00:00:00:03"
      name: "AP-Lobby"
      wlangroup_id: "Public-APs"
```

---

## UniFi Guest Control

Guest portal and hotspot configuration.

```yaml
unifi:
  guest_control:
    # Guest portal
    portal:
      enabled: true

      # Authentication
      auth: "simple"  # simple, hotspot, radius, facebook, google

      # Simple password
      password: "GuestAccess123"

      # Customization
      portal_customized: true
      x_portal_title: "Welcome"
      x_portal_message: "Please accept terms to continue"
      portal_use_hostname: false

      # Terms
      tos_enabled: true
      tos_text: "You agree to acceptable use policy..."

      # Vouchers
      voucher_enabled: false

      # Session
      auth_cache: 480  # minutes

      # Redirect
      redirect_enabled: false
      redirect_url: ""
      redirect_https: false

      # Rate limiting (handled by usergroup)

    # Hotspot
    hotspot:
      - name: "Guest-Hotspot"
        enabled: true

        # Vouchers
        voucher_enabled: true

        # Portal
        portal_customized: true
        x_portal_title: "Coffee Shop WiFi"

        # Payment (if supported)
        payment_enabled: false

    # Vouchers
    vouchers:
      - code: "GUEST2024"
        quota: 100  # Number of uses
        duration: 480  # minutes
        note: "Guest voucher"

      - code: "DAYPASS"
        quota: 1
        duration: 1440  # 24 hours
        note: "Day pass"
```

---

## Complete UniFi Example Configuration

Here's a complete example for a small office with UDM, switch, and APs:

```yaml
# Complete UniFi Configuration Example
# Small office with UDM Pro, USW-24-PoE, and 2x U6-LR APs

unifi:
  system:
    site:
      name: "default"
      desc: "Main Office"
      timezone: "America/New_York"

  # Networks
  networks:
    - name: "Default"
      purpose: "corporate"
      vlan_enabled: false
      dhcp_enabled: true
      dhcpd_start: "192.168.1.100"
      dhcpd_stop: "192.168.1.254"
      ip_subnet: "192.168.1.1/24"
      domain_name: "office.local"

    - name: "Guest"
      purpose: "guest"
      vlan_enabled: true
      vlan: 20
      dhcp_enabled: true
      dhcpd_start: "192.168.20.50"
      dhcpd_stop: "192.168.20.200"
      ip_subnet: "192.168.20.1/24"
      is_guest: true
      isolation: true

    - name: "WAN"
      purpose: "wan"
      wan_networkgroup: "WAN"
      wan_type: "dhcp"

  # WiFi Networks
  wlans:
    - name: "Office-WiFi"
      enabled: true
      security: "wpapsk"
      wpa_mode: "wpa2"
      x_passphrase: "SecurePassword123"
      networkconf_id: "Default"
      fast_roaming_enabled: true

    - name: "Guest-WiFi"
      enabled: true
      security: "wpapsk"
      wpa_mode: "wpa2"
      x_passphrase: "GuestPass456"
      networkconf_id: "Guest"
      is_guest: true
      portal_enabled: true

  # Port Forwarding
  portforward:
    - name: "Web Server"
      enabled: true
      dst_port: "443"
      fwd: "192.168.1.100"
      fwd_port: "443"
      proto: "tcp"

  # Firewall
  firewallrules:
    - name: "Block Guest to LAN"
      enabled: true
      action: "drop"
      ruleset: "LAN_IN"
      rule_index: 2000
      src_networkconf_id: "Guest"
      dst_address: "192.168.1.0/24"
      protocol: "all"

  # Port Profiles
  port_profiles:
    - name: "All"
      forward: "all"
      native_networkconf_id: "Default"

    - name: "LAN"
      forward: "native"
      native_networkconf_id: "Default"
      poe_mode: "auto"

  # Switch Configuration
  switches:
    - mac: "00:00:00:00:00:01"
      name: "Office-Switch"
      stp_version: "rstp"

      port_overrides:
        - port_idx: 1
          portconf_id: "All"
          name: "Uplink to UDM"

        - port_idx: 2
          portconf_id: "LAN"
          name: "Server"

        - port_idx: 10
          portconf_id: "LAN"
          name: "AP-1"
          poe_mode: "auto"

  # Access Points
  access_points:
    - mac: "00:00:00:00:00:02"
      name: "AP-Office-1"
      wlangroup_id: "Default"

      radio_table:
        - name: "ng"
          radio: "ng"
          channel: "auto"
          tx_power_mode: "auto"

        - name: "na"
          radio: "na"
          channel: "auto"
          tx_power_mode: "auto"

    - mac: "00:00:00:00:00:03"
      name: "AP-Office-2"
      wlangroup_id: "Default"
```

---

## Notes and Best Practices

### UniFi Controller Management

1. **API Access**: UniFi devices are managed via the controller's REST API
2. **Adoption**: Devices must be adopted into the controller first
3. **Provisioning**: Configuration changes trigger re-provisioning
4. **Backups**: Regular controller backups are essential
5. **Updates**: Keep controller and device firmware synchronized

### Network Design Best Practices

1. **VLANs**: Segment traffic by purpose (corporate, guest, IoT, management)
2. **Guest Networks**: Always isolate guest traffic from internal networks
3. **DHCP**: Use appropriate lease times (short for guests, long for corporate)
4. **DNS**: Configure both primary and secondary DNS servers
5. **Firewall**: Default deny, explicitly allow required traffic

### WiFi Best Practices

1. **Channel Planning**: Use auto channel selection or manually select non-overlapping channels
2. **Band Steering**: Enable to prefer 5GHz for capable clients
3. **Fast Roaming**: Enable 802.11r for seamless roaming
4. **Min RSSI**: Set minimum RSSI to prevent sticky clients
5. **Guest Portal**: Use vouchers or time-limited access for guests
6. **PMF**: Enable Protected Management Frames for WPA3

### Switch Best Practices

1. **Port Profiles**: Create reusable profiles for common configurations
2. **Trunking**: Use "All" profile for inter-switch and uplink connections
3. **PoE**: Enable auto PoE for APs and IP phones
4. **STP**: Use RSTP for faster convergence
5. **Storm Control**: Enable on access ports to prevent broadcast storms
6. **Port Naming**: Name all ports for easy identification

### Security Best Practices

1. **Firewall Rules**: Implement inter-VLAN firewall rules
2. **Guest Isolation**: Always isolate guest networks
3. **IoT Segmentation**: Place IoT devices on separate VLAN with restricted access
4. **Threat Management**: Enable IPS in prevention mode
5. **Country Blocking**: Block countries you don't do business with
6. **Strong Passwords**: Use complex passwords for all SSIDs
7. **Management Access**: Restrict controller access to trusted networks

### Performance Optimization

1. **DPI**: Enable for visibility, disable if performance issues arise
2. **QoS**: Configure smart queues with accurate WAN speeds
3. **Traffic Prioritization**: Prioritize VoIP and video conferencing
4. **Channel Width**: Use 20MHz on 2.4GHz, 40-80MHz on 5GHz
5. **Client Limits**: Set reasonable per-AP client limits

### UniFi-Specific Considerations

1. **Adoption**: New devices must be adopted through the controller
2. **SSH Access**: Limited SSH access compared to traditional CLI devices
3. **API Rate Limits**: Be aware of API rate limits when automating
4. **Controller Dependency**: Devices need controller for changes
5. **JSON Format**: UniFi API uses JSON, not traditional CLI commands

### Configuration Validation

Before applying:
- Verify VLAN IDs are consistent across all devices
- Ensure DHCP ranges don't overlap
- Check that firewall rules are ordered correctly
- Test guest portal before deployment
- Verify PoE budget for switches
- Confirm WiFi passwords meet security requirements

---

## Schema Version

Schema Version: 1.0.0
Last Updated: 2024-10-27
Compatible with: UniFi Network Application 8.x, UniFi OS 3.x
