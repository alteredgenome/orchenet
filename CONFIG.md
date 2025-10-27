# OrcheNet Configuration Schema

This document defines the complete YAML configuration schema for managing network devices through OrcheNet. The schema is vendor-agnostic at the top level, with vendor-specific implementations handling the translation to device commands.

## MikroTik RouterOS Configuration

This section details all available configuration elements for MikroTik RouterOS devices.

---

## Table of Contents

- [System Configuration](#system-configuration)
- [Interfaces](#interfaces)
- [IP Configuration](#ip-configuration)
  - [IP Addresses](#ip-addresses)
  - [IP Routes](#ip-routes)
  - [DNS](#dns)
  - [DHCP Server](#dhcp-server)
  - [DHCP Client](#dhcp-client)
  - [IP Pools](#ip-pools)
  - [IP Services](#ip-services)
- [Firewall](#firewall)
  - [Filter Rules](#filter-rules)
  - [NAT Rules](#nat-rules)
  - [Mangle Rules](#mangle-rules)
  - [Address Lists](#address-lists)
- [Bridge](#bridge)
- [VLAN](#vlan)
- [Wireless](#wireless)
- [Routing](#routing)
  - [OSPF](#ospf)
  - [BGP](#bgp)
- [VPN](#vpn)
  - [IPsec](#ipsec)
  - [L2TP](#l2tp)
  - [PPTP](#pptp)
  - [OpenVPN](#openvpn)
  - [WireGuard](#wireguard)
- [Quality of Service (QoS)](#quality-of-service-qos)
- [SNMP](#snmp)
- [Logging](#logging)
- [Users and Access](#users-and-access)
- [Backup and Scheduling](#backup-and-scheduling)

---

## System Configuration

General system settings including identity, time, and services.

```yaml
system:
  # Device identity
  identity: "Router-Main"

  # Time and NTP
  clock:
    timezone: "America/New_York"
    time_zone_autodetect: true

  ntp:
    enabled: true
    servers:
      - "time.google.com"
      - "pool.ntp.org"
    vrf: "main"

  # Logging
  note: "Production router - Site A"

  # Router resource settings
  resource:
    cpu_affinity: true

  # Watchdog
  watchdog:
    enabled: true
    watchdog_timer: true
```

---

## Interfaces

Interface configuration for physical and virtual interfaces.

```yaml
interfaces:
  # Physical interface configuration
  - name: "ether1"
    enabled: true
    comment: "WAN interface"
    mtu: 1500
    mac_address: "auto"  # or specific MAC

  - name: "ether2"
    enabled: true
    comment: "LAN interface"
    mtu: 1500

  # VLAN interfaces
  - name: "vlan10"
    type: "vlan"
    vlan_id: 10
    interface: "ether2"
    enabled: true
    comment: "Management VLAN"

  # Bridge interfaces are defined in the bridge section

  # Bonding/Link aggregation
  - name: "bond1"
    type: "bonding"
    slaves:
      - "ether3"
      - "ether4"
    mode: "802.3ad"  # balance-rr, active-backup, 802.3ad, etc.
    enabled: true
    comment: "Link aggregation to switch"
```

---

## IP Configuration

### IP Addresses

IP address assignment to interfaces.

```yaml
ip:
  addresses:
    - interface: "ether1"
      address: "203.0.113.5/30"
      comment: "WAN IP"
      network: "203.0.113.4"  # Optional, auto-calculated

    - interface: "ether2"
      address: "192.168.1.1/24"
      comment: "LAN gateway"

    - interface: "vlan10"
      address: "10.0.10.1/24"
      comment: "Management network"
```

### IP Routes

Static and dynamic routing configuration.

```yaml
ip:
  routes:
    - dst_address: "0.0.0.0/0"
      gateway: "203.0.113.6"
      distance: 1
      comment: "Default route to ISP"
      check_gateway: "ping"
      scope: 30
      target_scope: 10

    - dst_address: "10.0.0.0/8"
      gateway: "192.168.1.254"
      distance: 10
      comment: "Route to internal network"

    - dst_address: "172.16.0.0/16"
      gateway: "192.168.1.253"
      type: "blackhole"
      comment: "Blackhole unused network"
```

### DNS

DNS server configuration.

```yaml
ip:
  dns:
    servers:
      - "1.1.1.1"
      - "8.8.8.8"
    allow_remote_requests: true
    cache_size: 4096
    max_udp_packet_size: 4096
    query_server_timeout: 2000
    query_total_timeout: 10000
```

### DHCP Server

DHCP server pools and networks.

```yaml
ip:
  dhcp_server:
    - name: "dhcp-lan"
      interface: "ether2"
      address_pool: "pool-lan"
      lease_time: "1d"
      authoritative: true
      bootp_support: "none"
      disabled: false

      # DHCP options
      dns_server: "192.168.1.1"
      ntp_server: "192.168.1.1"
      domain: "local.lan"
      wins_server: ""

      # Lease settings
      lease_script: ""

    # DHCP network configuration
    - name: "network-lan"
      type: "network"
      address: "192.168.1.0/24"
      gateway: "192.168.1.1"
      dns_server: "192.168.1.1"
      domain: "local.lan"
      netmask: 24
      comment: "LAN DHCP network"
```

### DHCP Client

DHCP client on WAN or other interfaces.

```yaml
ip:
  dhcp_client:
    - interface: "ether1"
      disabled: false
      use_peer_dns: true
      use_peer_ntp: true
      add_default_route: true
      default_route_distance: 1
      comment: "WAN DHCP client"
```

### IP Pools

Address pools for DHCP and VPN.

```yaml
ip:
  pools:
    - name: "pool-lan"
      ranges:
        - "192.168.1.100-192.168.1.250"
      comment: "LAN DHCP pool"

    - name: "pool-vpn"
      ranges:
        - "10.10.10.10-10.10.10.100"
      comment: "VPN client pool"
```

### IP Services

Control access to router services.

```yaml
ip:
  services:
    - name: "telnet"
      disabled: true

    - name: "ftp"
      disabled: true

    - name: "www"
      disabled: false
      port: 80
      address: "192.168.1.0/24"  # Restrict to LAN

    - name: "ssh"
      disabled: false
      port: 22
      address: "192.168.1.0/24"

    - name: "www-ssl"
      disabled: false
      port: 443
      address: "192.168.1.0/24"
      certificate: "router-cert"

    - name: "api"
      disabled: false
      port: 8728
      address: "192.168.1.0/24"

    - name: "api-ssl"
      disabled: false
      port: 8729
      address: "192.168.1.0/24"
      certificate: "router-cert"
```

---

## Firewall

Comprehensive firewall configuration including filter, NAT, and mangle rules.

### Filter Rules

Packet filtering rules.

```yaml
ip:
  firewall:
    filter:
      # Input chain - traffic to router
      - chain: "input"
        action: "accept"
        connection_state: "established,related"
        comment: "Accept established/related"

      - chain: "input"
        action: "drop"
        connection_state: "invalid"
        comment: "Drop invalid"

      - chain: "input"
        action: "accept"
        protocol: "icmp"
        comment: "Accept ICMP"

      - chain: "input"
        action: "accept"
        in_interface: "ether2"
        comment: "Accept from LAN"

      - chain: "input"
        action: "drop"
        comment: "Drop all other input"

      # Forward chain - traffic through router
      - chain: "forward"
        action: "accept"
        connection_state: "established,related"
        comment: "Accept established/related"

      - chain: "forward"
        action: "drop"
        connection_state: "invalid"
        comment: "Drop invalid"

      - chain: "forward"
        action: "accept"
        in_interface: "ether2"
        comment: "Accept from LAN to WAN"

      - chain: "forward"
        action: "drop"
        comment: "Drop all other forward"

      # Custom rules
      - chain: "forward"
        action: "accept"
        protocol: "tcp"
        dst_port: "80,443"
        in_interface: "ether2"
        comment: "Allow HTTP/HTTPS from LAN"

      - chain: "forward"
        action: "drop"
        protocol: "tcp"
        dst_port: "22"
        src_address: "!192.168.1.0/24"
        comment: "Block SSH except from LAN"

      # Advanced matching
      - chain: "forward"
        action: "drop"
        protocol: "tcp"
        tcp_flags: "syn,!ack"
        connection_limit: "10,32"
        comment: "SYN flood protection"

      - chain: "input"
        action: "add-src-to-address-list"
        protocol: "tcp"
        dst_port: "22"
        connection_state: "new"
        src_address_list: "!ssh_allowed"
        address_list: "ssh_blacklist"
        address_list_timeout: "1d"
        comment: "Blacklist unauthorized SSH attempts"
```

### NAT Rules

Network Address Translation rules.

```yaml
ip:
  firewall:
    nat:
      # Source NAT (masquerade)
      - chain: "srcnat"
        action: "masquerade"
        out_interface: "ether1"
        comment: "Masquerade WAN"

      # Destination NAT (port forwarding)
      - chain: "dstnat"
        action: "dst-nat"
        protocol: "tcp"
        dst_port: "8080"
        in_interface: "ether1"
        to_addresses: "192.168.1.100"
        to_ports: "80"
        comment: "Forward port 8080 to internal web server"

      - chain: "dstnat"
        action: "dst-nat"
        protocol: "tcp"
        dst_port: "2222"
        in_interface: "ether1"
        to_addresses: "192.168.1.10"
        to_ports: "22"
        comment: "SSH to internal server"

      # Redirect
      - chain: "dstnat"
        action: "redirect"
        protocol: "tcp"
        dst_port: "80"
        in_interface: "ether2"
        to_ports: "8080"
        comment: "Redirect HTTP to proxy"
```

### Mangle Rules

Packet marking and modification.

```yaml
ip:
  firewall:
    mangle:
      - chain: "prerouting"
        action: "mark-connection"
        protocol: "tcp"
        dst_port: "80,443"
        new_connection_mark: "http_traffic"
        passthrough: true
        comment: "Mark HTTP/HTTPS connections"

      - chain: "prerouting"
        action: "mark-packet"
        connection_mark: "http_traffic"
        new_packet_mark: "http_packet"
        passthrough: false
        comment: "Mark HTTP/HTTPS packets"

      - chain: "postrouting"
        action: "change-mss"
        protocol: "tcp"
        tcp_flags: "syn"
        new_mss: "1360"
        out_interface: "ether1"
        comment: "MSS clamping for VPN"
```

### Address Lists

Reusable address lists for firewall rules.

```yaml
ip:
  firewall:
    address_lists:
      - list: "management_ips"
        address: "192.168.1.10"
        comment: "Admin workstation"

      - list: "management_ips"
        address: "192.168.1.11"
        comment: "Secondary admin"

      - list: "blocked_countries"
        address: "203.0.113.0/24"
        timeout: "1d"
        comment: "Temporary block"

      - list: "vpn_clients"
        address: "10.10.10.0/24"
        comment: "VPN subnet"
```

---

## Bridge

Bridge configuration for switching and VLANs.

```yaml
bridge:
  bridges:
    - name: "bridge-lan"
      comment: "Main LAN bridge"
      vlan_filtering: true
      pvid: 1
      frame_types: "admit-all"
      ingress_filtering: false
      protocol_mode: "rstp"  # stp, rstp, mstp

  ports:
    - bridge: "bridge-lan"
      interface: "ether2"
      pvid: 1
      comment: "LAN port 1"

    - bridge: "bridge-lan"
      interface: "ether3"
      pvid: 10
      comment: "Management VLAN"

    - bridge: "bridge-lan"
      interface: "ether4"
      pvid: 1
      comment: "LAN port 2"

  vlans:
    - bridge: "bridge-lan"
      vlan_ids: "1"
      tagged:
        - "ether2"
      untagged:
        - "ether3"
      comment: "Default VLAN"

    - bridge: "bridge-lan"
      vlan_ids: "10"
      tagged:
        - "ether2"
        - "ether3"
      comment: "Management VLAN"

    - bridge: "bridge-lan"
      vlan_ids: "20,30,40"
      tagged:
        - "ether2"
      comment: "Guest and IoT VLANs"
```

---

## VLAN

VLAN interface configuration (also see Bridge VLAN section).

```yaml
vlans:
  - name: "vlan-guest"
    vlan_id: 20
    interface: "bridge-lan"
    comment: "Guest network VLAN"

  - name: "vlan-iot"
    vlan_id: 30
    interface: "bridge-lan"
    comment: "IoT devices VLAN"
```

---

## Wireless

Wireless interface and security configuration.

```yaml
wireless:
  # Security profiles
  security_profiles:
    - name: "default"
      mode: "none"

    - name: "wpa2-enterprise"
      mode: "dynamic-keys"
      authentication_types:
        - "wpa2-eap"
      eap_methods: "eap-tls"
      tls_mode: "verify-certificate"
      tls_certificate: "server-cert"

    - name: "wpa2-personal"
      mode: "dynamic-keys"
      authentication_types:
        - "wpa2-psk"
      wpa2_pre_shared_key: "your-wifi-password"
      group_ciphers: "aes-ccm"
      unicast_ciphers: "aes-ccm"

    - name: "wpa3-personal"
      mode: "dynamic-keys"
      authentication_types:
        - "wpa3-psk"
      wpa2_pre_shared_key: "your-wifi-password"
      group_ciphers: "aes-ccm"
      unicast_ciphers: "aes-ccm"

  # Wireless interfaces
  interfaces:
    - name: "wlan1"
      mode: "ap-bridge"  # ap-bridge, station, bridge, etc.
      ssid: "MyNetwork"
      band: "2ghz-b/g/n"
      channel_width: "20/40mhz-Ce"
      frequency: "auto"  # or specific frequency
      wireless_protocol: "802.11"
      security_profile: "wpa2-personal"
      enabled: true
      comment: "Main wireless network"

      # Advanced settings
      hide_ssid: false
      wps_mode: "disabled"
      bridge_mode: "enabled"
      default_forwarding: true

      # Radio settings
      tx_power: 20  # dBm
      tx_power_mode: "default"
      distance: "indoors"

      # Access list
      access_list:
        - mac_address: "AA:BB:CC:DD:EE:FF"
          action: "accept"
          comment: "Trusted device"
        - mac_address: "11:22:33:44:55:66"
          action: "reject"
          comment: "Blocked device"

    - name: "wlan2"
      mode: "ap-bridge"
      ssid: "GuestNetwork"
      band: "5ghz-a/n/ac"
      channel_width: "20/40/80mhz-Ceee"
      frequency: "auto"
      security_profile: "wpa2-personal"
      enabled: true
      comment: "Guest network - isolated"

  # Wireless provisioning
  provisioning:
    enabled: false

  # Channel scanning
  channels:
    save_selected: true
```

---

## Routing

Dynamic routing protocol configuration.

### OSPF

```yaml
routing:
  ospf:
    instances:
      - name: "default"
        router_id: "192.168.1.1"
        redistribute:
          - "connected"
          - "static"

    areas:
      - instance: "default"
        name: "backbone"
        area_id: "0.0.0.0"
        type: "default"

    networks:
      - area: "backbone"
        network: "192.168.1.0/24"

    interfaces:
      - instance: "default"
        interface: "ether2"
        cost: 10
        priority: 1
        hello_interval: 10
        dead_interval: 40
        authentication: "md5"
        authentication_key: "ospf-key-123"
```

### BGP

```yaml
routing:
  bgp:
    instance:
      name: "default"
      as: 65001
      router_id: "192.168.1.1"

    peers:
      - name: "isp-peer"
        remote_address: "203.0.113.6"
        remote_as: 65000
        multihop: false
        route_reflect: false
        hold_time: "3m"
        ttl: 255
        in_filter: "bgp-in"
        out_filter: "bgp-out"
        comment: "ISP BGP peer"

    networks:
      - network: "192.168.0.0/16"
        synchronize: false
        comment: "Advertise internal networks"
```

---

## VPN

VPN configuration for various protocols.

### IPsec

```yaml
vpn:
  ipsec:
    # Proposals
    proposals:
      - name: "default"
        auth_algorithms: "sha256"
        enc_algorithms: "aes-256-cbc"
        lifetime: "30m"
        pfs_group: "modp2048"

    # Peers
    peers:
      - name: "remote-office"
        address: "203.0.113.100/32"
        port: 500
        local_address: "203.0.113.5"
        auth_method: "pre-shared-key"
        secret: "your-preshared-key"
        exchange_mode: "ike2"
        passive: false
        send_initial_contact: true
        comment: "Site-to-site VPN"

    # Policies
    policies:
      - src_address: "192.168.1.0/24"
        dst_address: "192.168.2.0/24"
        protocol: "all"
        action: "encrypt"
        sa_src_address: "203.0.113.5"
        sa_dst_address: "203.0.113.100"
        proposal: "default"
        tunnel: true
        comment: "Policy for remote office"
```

### L2TP

```yaml
vpn:
  l2tp:
    server:
      enabled: true
      use_ipsec: true
      ipsec_secret: "l2tp-secret"
      default_profile: "default-encryption"
      authentication: "mschap2"
      keepalive_timeout: 30
      max_sessions: 10

    secrets:
      - name: "user1"
        password: "password1"
        local_address: "10.10.10.1"
        remote_address: "10.10.10.10"
        profile: "default-encryption"
        service: "l2tp"
```

### PPTP

```yaml
vpn:
  pptp:
    server:
      enabled: true
      authentication: "mschap2"
      default_profile: "default-encryption"
      keepalive_timeout: 30
      max_sessions: 10

    secrets:
      - name: "pptp-user1"
        password: "password1"
        local_address: "10.10.10.1"
        remote_address: "10.10.10.11"
        service: "pptp"
```

### OpenVPN

```yaml
vpn:
  ovpn:
    server:
      - name: "ovpn-server"
        port: 1194
        mode: "ip"
        protocol: "tcp"
        enabled: true
        cipher: "aes256"
        auth: "sha256"
        certificate: "server-cert"
        require_client_certificate: true
        netmask: 24

    client:
      - name: "remote-site"
        connect_to: "vpn.example.com"
        port: 1194
        mode: "ip"
        protocol: "tcp"
        cipher: "aes256"
        auth: "sha256"
        certificate: "client-cert"
        add_default_route: false
        comment: "VPN to headquarters"
```

### WireGuard

```yaml
vpn:
  wireguard:
    - name: "wg-server"
      mtu: 1420
      listen_port: 51820
      private_key: "private-key-here"
      comment: "WireGuard server interface"

      peers:
        - name: "client1"
          public_key: "client-public-key"
          allowed_address: "10.20.30.2/32"
          endpoint_port: 51820
          persistent_keepalive: 25
          comment: "Mobile client"

        - name: "client2"
          public_key: "client2-public-key"
          allowed_address: "10.20.30.3/32"
          persistent_keepalive: 25
          comment: "Remote office"
```

---

## Quality of Service (QoS)

Traffic shaping and prioritization.

```yaml
queue:
  # Queue types
  types:
    - name: "default"
      kind: "pfifo"

    - name: "priority-queue"
      kind: "pcq"
      pcq_rate: 0
      pcq_classifier: "src-address,dst-address"

  # Simple queues
  simple:
    - name: "guest-limit"
      target: "192.168.20.0/24"
      max_limit: "10M/10M"  # upload/download
      burst_limit: "15M/15M"
      burst_threshold: "8M/8M"
      burst_time: "8s/8s"
      priority: 8
      comment: "Limit guest network"

    - name: "voip-priority"
      target: "192.168.1.100/32"
      dst: "0.0.0.0/0"
      protocol: "udp"
      dst_port: "5060-5061"
      max_limit: "1M/1M"
      priority: 1
      comment: "Prioritize VoIP traffic"

  # Queue tree (more advanced)
  tree:
    - name: "download-parent"
      parent: "ether2"
      packet_mark: ""
      limit_at: 0
      max_limit: "100M"
      priority: 8

    - name: "download-http"
      parent: "download-parent"
      packet_mark: "http_packet"
      limit_at: "10M"
      max_limit: "50M"
      priority: 4
      comment: "HTTP traffic"
```

---

## SNMP

SNMP monitoring configuration.

```yaml
snmp:
  enabled: true
  contact: "admin@example.com"
  location: "Server Room A"
  engine_id: ""
  trap_version: 2
  trap_community: "public"
  trap_generators: "interfaces"
  trap_target:
    - "192.168.1.100"

  communities:
    - name: "public"
      addresses: "192.168.1.0/24"
      read_access: true
      write_access: false

    - name: "private"
      addresses: "192.168.1.10/32"
      read_access: true
      write_access: true
```

---

## Logging

System logging configuration.

```yaml
system:
  logging:
    # Log actions
    actions:
      - name: "memory"
        target: "memory"
        memory_lines: 1000

      - name: "disk"
        target: "disk"
        disk_file_name: "log"
        disk_lines_per_file: 1000
        disk_file_count: 2

      - name: "remote"
        target: "remote"
        remote: "192.168.1.100"
        remote_port: 514
        src_address: "192.168.1.1"
        bsd_syslog: true
        syslog_facility: "local7"

    # Log topics
    rules:
      - topics:
          - "info"
          - "error"
          - "warning"
        action: "memory"

      - topics:
          - "critical"
        action: "remote"
        prefix: "router"

      - topics:
          - "firewall"
        action: "disk"
```

---

## Users and Access

User accounts and permissions.

```yaml
users:
  - name: "admin"
    group: "full"
    password: "secure-password"
    comment: "Primary administrator"

  - name: "monitor"
    group: "read"
    password: "monitor-password"
    comment: "Read-only monitoring account"

  - name: "api-user"
    group: "api"
    password: "api-password"
    comment: "API access account"

groups:
  - name: "api"
    policy:
      - "read"
      - "write"
      - "api"
    comment: "API access group"

# SSH keys for public key authentication
user_ssh_keys:
  - user: "admin"
    key_data: "ssh-rsa AAAAB3NzaC1yc2EA... admin@workstation"
    comment: "Admin SSH key"
```

---

## Backup and Scheduling

Scheduled tasks and backups.

```yaml
system:
  scheduler:
    - name: "daily-backup"
      on_event: "/system backup save name=daily-backup"
      start_date: "2024-01-01"
      start_time: "03:00:00"
      interval: "1d"
      comment: "Daily configuration backup"

    - name: "weekly-email-backup"
      on_event: "/system backup save name=weekly; /tool e-mail send to=admin@example.com subject=\"Router Backup\" body=\"Weekly backup attached\" file=weekly.backup"
      start_date: "2024-01-01"
      start_time: "04:00:00"
      interval: "7d"
      comment: "Weekly backup via email"

    - name: "log-rotation"
      on_event: "/log print file=logs"
      start_time: "00:00:00"
      interval: "1d"
      comment: "Daily log export"

  # Email configuration for notifications
  email:
    server: "smtp.gmail.com"
    port: 587
    from: "router@example.com"
    user: "router@example.com"
    password: "email-password"
    tls: true
```

---

## Complete Example Configuration

Here's a complete example configuration for a typical small office router:

```yaml
# Complete MikroTik Router Configuration Example
# Small office with WAN, LAN, Guest WiFi, and VPN

system:
  identity: "Office-Router-Main"
  clock:
    timezone: "America/New_York"
  ntp:
    enabled: true
    servers:
      - "pool.ntp.org"

interfaces:
  - name: "ether1"
    enabled: true
    comment: "WAN"
  - name: "ether2"
    enabled: true
    comment: "LAN"
  - name: "ether3"
    enabled: true
    comment: "LAN"
  - name: "ether4"
    enabled: true
    comment: "LAN"
  - name: "wlan1"
    enabled: true
    comment: "WiFi"

bridge:
  bridges:
    - name: "bridge-lan"
      comment: "LAN bridge"
      vlan_filtering: true

  ports:
    - bridge: "bridge-lan"
      interface: "ether2"
    - bridge: "bridge-lan"
      interface: "ether3"
    - bridge: "bridge-lan"
      interface: "ether4"
    - bridge: "bridge-lan"
      interface: "wlan1"

ip:
  addresses:
    - interface: "ether1"
      address: "dhcp-client"
    - interface: "bridge-lan"
      address: "192.168.88.1/24"

  pools:
    - name: "dhcp-lan"
      ranges:
        - "192.168.88.100-192.168.88.200"

  dhcp_server:
    - name: "dhcp1"
      interface: "bridge-lan"
      address_pool: "dhcp-lan"
      lease_time: "1d"
      dns_server: "192.168.88.1"

  dhcp_client:
    - interface: "ether1"
      disabled: false
      use_peer_dns: true
      add_default_route: true

  dns:
    servers:
      - "1.1.1.1"
      - "8.8.8.8"
    allow_remote_requests: true

  firewall:
    filter:
      - chain: "input"
        action: "accept"
        connection_state: "established,related"
      - chain: "input"
        action: "drop"
        connection_state: "invalid"
      - chain: "input"
        action: "accept"
        protocol: "icmp"
      - chain: "input"
        action: "accept"
        in_interface: "bridge-lan"
      - chain: "input"
        action: "drop"

      - chain: "forward"
        action: "accept"
        connection_state: "established,related"
      - chain: "forward"
        action: "drop"
        connection_state: "invalid"
      - chain: "forward"
        action: "accept"
        in_interface: "bridge-lan"
      - chain: "forward"
        action: "drop"

    nat:
      - chain: "srcnat"
        action: "masquerade"
        out_interface: "ether1"

wireless:
  security_profiles:
    - name: "office-wifi"
      mode: "dynamic-keys"
      authentication_types:
        - "wpa2-psk"
      wpa2_pre_shared_key: "YourWiFiPassword123"

  interfaces:
    - name: "wlan1"
      mode: "ap-bridge"
      ssid: "Office-WiFi"
      band: "2ghz-b/g/n"
      security_profile: "office-wifi"

users:
  - name: "admin"
    group: "full"
    password: "change-me"
    comment: "Administrator"

system:
  scheduler:
    - name: "daily-backup"
      on_event: "/system backup save name=auto-backup"
      start_time: "03:00:00"
      interval: "1d"
```

---

## Notes and Best Practices

### Configuration Management

1. **Always use comments**: Every configuration element should have a descriptive comment
2. **Version control**: Store YAML configurations in git for tracking changes
3. **Test configurations**: Test on non-production devices before deploying
4. **Backup first**: Always create a backup before applying new configurations

### Security Best Practices

1. **Change default passwords**: Never use default or weak passwords
2. **Restrict management access**: Limit SSH/WebFig access to management network
3. **Use firewall rules**: Always implement input and forward chains
4. **Keep firmware updated**: Regularly update RouterOS to latest stable version
5. **Disable unused services**: Turn off services you don't need
6. **Use strong WiFi encryption**: Prefer WPA3, minimum WPA2
7. **Implement proper NAT**: Use masquerade for dynamic IPs

### Performance Considerations

1. **Firewall rule order**: Place most-matched rules at the top
2. **Connection tracking**: Use established/related rules early
3. **Queue priorities**: Lower numbers = higher priority (1-8)
4. **Bridge mode**: Enable hardware offload when possible
5. **VLAN filtering**: Has performance impact, use only if needed

### Validation

Before applying configurations:
- Validate YAML syntax
- Check for conflicting rules
- Verify IP address ranges don't overlap
- Ensure gateway addresses are correct
- Confirm interface names match device

---

## Schema Version

Schema Version: 1.0.0
Last Updated: 2024-10-27
Compatible with: MikroTik RouterOS 7.x
