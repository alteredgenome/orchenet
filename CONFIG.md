# OrcheNet Unified Configuration Schema

This document defines the vendor-agnostic YAML configuration schema for OrcheNet. This unified schema can be translated to any supported vendor (MikroTik, Fortinet, Ubiquiti, WatchGuard).

## Philosophy

OrcheNet uses a **unified abstraction layer** that represents common networking concepts in a vendor-neutral way. When you write configuration in this schema, OrcheNet automatically translates it to the appropriate vendor-specific commands or API calls.

### Design Principles

1. **Vendor Agnostic**: Configuration describes *what* you want, not *how* to achieve it
2. **Common Denominator**: Focus on features supported across all vendors
3. **Extensible**: Vendor-specific features available through extensions
4. **Intuitive**: Use industry-standard terminology
5. **Declarative**: Describe desired state, not procedural steps

---

## Table of Contents

- [Device Identification](#device-identification)
- [System Configuration](#system-configuration)
- [Network Interfaces](#network-interfaces)
- [VLANs](#vlans)
- [IP Addressing](#ip-addressing)
- [DHCP Services](#dhcp-services)
- [DNS Configuration](#dns-configuration)
- [Static Routes](#static-routes)
- [Dynamic Routing](#dynamic-routing)
- [Firewall Rules](#firewall-rules)
- [NAT Configuration](#nat-configuration)
- [VPN Configuration](#vpn-configuration)
- [Wireless Networks](#wireless-networks)
- [Access Points](#access-points)
- [Switch Configuration](#switch-configuration)
- [Quality of Service](#quality-of-service)
- [User Authentication](#user-authentication)
- [Logging](#logging)
- [High Availability](#high-availability)
- [Vendor Extensions](#vendor-extensions)

---

## Device Identification

Specify the device being configured.

```yaml
device:
  # Device identification
  name: "router-hq-01"
  vendor: "mikrotik"  # mikrotik, fortinet, ubiquiti, watchguard
  model: "CCR1009"

  # Location
  location: "Headquarters"
  site: "main"

  # Management
  contact: "admin@example.com"
```

---

## System Configuration

Global system settings applicable to all vendors.

```yaml
system:
  # Device identity
  hostname: "Router-HQ-01"
  description: "Headquarters main router"

  # Time settings
  timezone: "America/New_York"

  ntp:
    enabled: true
    servers:
      - "pool.ntp.org"
      - "time.google.com"

  # Management access
  management:
    # Web interface
    web:
      enabled: true
      http_port: 80
      https_port: 443
      session_timeout: 30

    # SSH
    ssh:
      enabled: true
      port: 22

    # API (for automation)
    api:
      enabled: true
      port: 8728
      ssl_port: 8729

  # SNMP
  snmp:
    enabled: true
    community: "public"
    location: "Datacenter A"
    contact: "admin@example.com"

    trap_destinations:
      - host: "192.168.1.100"
        community: "public"
        port: 162

  # Users
  users:
    - username: "admin"
      password: "secure-password"
      role: "admin"

    - username: "readonly"
      password: "readonly-password"
      role: "readonly"
```

---

## Network Interfaces

Physical and logical interface configuration.

```yaml
interfaces:
  # Physical interface
  - name: "wan1"
    type: "physical"
    enabled: true
    description: "Primary WAN connection"

    # Addressing
    addressing:
      mode: "dhcp"  # static, dhcp, pppoe

      # For static mode:
      # mode: "static"
      # ipv4: "203.0.113.10/30"
      # gateway: "203.0.113.9"

    # Link settings
    speed: "auto"  # auto, 10, 100, 1000, 10000
    duplex: "auto"  # auto, half, full
    mtu: 1500

    # Role/zone
    zone: "wan"

  - name: "lan1"
    type: "physical"
    enabled: true
    description: "Main LAN interface"

    addressing:
      mode: "static"
      ipv4: "192.168.1.1/24"

    speed: "auto"
    duplex: "auto"
    mtu: 1500
    zone: "lan"

  # VLAN interface
  - name: "vlan10"
    type: "vlan"
    enabled: true
    description: "Management VLAN"

    vlan:
      id: 10
      parent: "lan1"

    addressing:
      mode: "static"
      ipv4: "192.168.10.1/24"

    zone: "lan"

  # Bridge interface
  - name: "bridge-lan"
    type: "bridge"
    enabled: true
    description: "LAN bridge"

    bridge:
      members:
        - "lan2"
        - "lan3"
        - "lan4"
      stp: true

    addressing:
      mode: "static"
      ipv4: "192.168.2.1/24"

    zone: "lan"

  # LAG/Bond interface
  - name: "bond1"
    type: "aggregate"
    enabled: true
    description: "Link aggregation to switch"

    aggregate:
      mode: "lacp"  # lacp, static
      members:
        - "lan5"
        - "lan6"

    addressing:
      mode: "static"
      ipv4: "192.168.100.1/24"

    zone: "lan"

  # Loopback
  - name: "loopback0"
    type: "loopback"
    enabled: true

    addressing:
      mode: "static"
      ipv4: "1.1.1.1/32"
```

---

## VLANs

VLAN definitions (can be defined inline with interfaces or separately).

```yaml
vlans:
  - id: 1
    name: "default"
    description: "Default VLAN"

  - id: 10
    name: "management"
    description: "Management network"

  - id: 20
    name: "guest"
    description: "Guest WiFi"

  - id: 30
    name: "iot"
    description: "IoT devices"

  - id: 100
    name: "servers"
    description: "Server network"
```

---

## IP Addressing

Additional IP address assignments.

```yaml
ip:
  # Additional addresses
  addresses:
    - interface: "lan1"
      address: "192.168.1.254/24"
      description: "Secondary address"

    - interface: "vlan10"
      address: "192.168.10.254/24"
      description: "Backup gateway"

  # Address pools (for DHCP, VPN, etc.)
  pools:
    - name: "lan-dhcp"
      start: "192.168.1.100"
      end: "192.168.1.200"

    - name: "guest-dhcp"
      start: "192.168.20.50"
      end: "192.168.20.200"

    - name: "vpn-pool"
      start: "10.10.10.10"
      end: "10.10.10.100"
```

---

## DHCP Services

DHCP server configuration.

```yaml
dhcp:
  servers:
    - name: "lan-dhcp"
      interface: "lan1"
      enabled: true

      # IP range
      pool: "lan-dhcp"  # Reference to pool above
      # OR specify inline:
      # start_ip: "192.168.1.100"
      # end_ip: "192.168.1.200"

      # Network settings
      gateway: "192.168.1.1"
      netmask: "255.255.255.0"

      # DNS
      dns_servers:
        - "192.168.1.1"
        - "1.1.1.1"

      # Domain
      domain_name: "local.lan"

      # Lease time
      lease_time: 86400  # seconds

      # DHCP options
      options:
        - code: 66
          value: "192.168.1.10"
          description: "TFTP server"

      # Static reservations
      reservations:
        - mac: "00:11:22:33:44:55"
          ip: "192.168.1.50"
          hostname: "server1"

    - name: "guest-dhcp"
      interface: "vlan20"
      enabled: true
      pool: "guest-dhcp"
      gateway: "192.168.20.1"
      netmask: "255.255.255.0"
      dns_servers:
        - "192.168.20.1"
        - "1.1.1.1"
      lease_time: 3600

  # DHCP relay
  relay:
    - interface: "vlan100"
      server: "192.168.1.100"
```

---

## DNS Configuration

DNS proxy and forwarding.

```yaml
dns:
  # DNS proxy/forwarder
  proxy:
    enabled: true

    # Upstream DNS servers
    servers:
      - "1.1.1.1"
      - "8.8.8.8"

    # Allow queries from these interfaces/zones
    allow_from:
      - "lan"
      - "vlan10"

  # Static DNS entries
  static:
    - hostname: "server1.local.lan"
      ip: "192.168.1.100"

    - hostname: "server2.local.lan"
      ip: "192.168.1.101"

  # DNS filtering (if supported)
  filtering:
    enabled: true
    block_malware: true
    block_ads: false
```

---

## Static Routes

Static routing configuration.

```yaml
routes:
  static:
    - name: "default"
      destination: "0.0.0.0/0"
      gateway: "203.0.113.9"
      interface: "wan1"
      distance: 1
      description: "Default route to ISP"

    - name: "internal-network"
      destination: "10.0.0.0/8"
      gateway: "192.168.1.254"
      interface: "lan1"
      distance: 10
      description: "Route to internal network"

    - name: "blackhole"
      destination: "192.168.100.0/24"
      type: "blackhole"
      distance: 254
      description: "Drop traffic to unused network"
```

---

## Dynamic Routing

OSPF and BGP configuration.

```yaml
routes:
  # OSPF
  ospf:
    enabled: true
    router_id: "1.1.1.1"

    areas:
      - id: "0.0.0.0"
        type: "standard"
        authentication: "none"  # none, simple, md5

        networks:
          - "192.168.1.0/24"
          - "192.168.10.0/24"

    interfaces:
      - name: "lan1"
        area: "0.0.0.0"
        cost: 10
        priority: 1
        hello_interval: 10
        dead_interval: 40

    redistribute:
      - protocol: "static"
        metric: 100
      - protocol: "connected"
        metric: 50

  # BGP
  bgp:
    enabled: false
    asn: 65001
    router_id: "1.1.1.1"

    neighbors:
      - ip: "203.0.113.9"
        remote_asn: 65000
        description: "ISP peer"

    networks:
      - "192.168.0.0/16"
```

---

## Firewall Rules

Unified firewall policy configuration.

```yaml
firewall:
  # Network/host aliases for reuse
  aliases:
    hosts:
      - name: "server1"
        ip: "192.168.1.100"

      - name: "server2"
        ip: "192.168.1.101"

    networks:
      - name: "lan-subnet"
        network: "192.168.1.0/24"

      - name: "guest-subnet"
        network: "192.168.20.0/24"

    groups:
      - name: "internal-servers"
        members:
          - "server1"
          - "server2"

  # Firewall rules
  rules:
    # Allow LAN to Internet
    - name: "lan-to-internet"
      enabled: true
      order: 100

      source:
        zones: ["lan"]
        addresses: ["lan-subnet"]

      destination:
        zones: ["wan"]
        addresses: ["any"]

      service:
        protocols: ["tcp", "udp"]
        ports: ["80", "443", "53"]

      action: "accept"

      # NAT
      nat:
        enabled: true
        type: "masquerade"

      # Logging
      log: true

      # Security services (if supported)
      security:
        antivirus: true
        ips: true
        web_filter: true

    # Block guest to LAN
    - name: "block-guest-to-lan"
      enabled: true
      order: 200

      source:
        zones: ["guest"]
        addresses: ["guest-subnet"]

      destination:
        zones: ["lan"]
        addresses: ["lan-subnet"]

      service:
        protocols: ["any"]

      action: "drop"
      log: true

    # Allow established/related
    - name: "allow-established"
      enabled: true
      order: 10

      source:
        zones: ["any"]

      destination:
        zones: ["any"]

      state: ["established", "related"]

      action: "accept"
      log: false

    # Drop invalid
    - name: "drop-invalid"
      enabled: true
      order: 20

      source:
        zones: ["any"]

      destination:
        zones: ["any"]

      state: ["invalid"]

      action: "drop"
      log: true

    # Custom application rule
    - name: "allow-ssh-from-mgmt"
      enabled: true
      order: 150

      source:
        zones: ["lan"]
        addresses: ["192.168.10.0/24"]

      destination:
        zones: ["lan"]
        addresses: ["internal-servers"]

      service:
        protocols: ["tcp"]
        ports: ["22"]

      action: "accept"
      log: true
```

---

## NAT Configuration

Network Address Translation.

```yaml
nat:
  # Source NAT (outbound)
  source:
    - name: "lan-internet"
      enabled: true

      source:
        zones: ["lan"]
        addresses: ["192.168.1.0/24"]

      destination:
        zones: ["wan"]

      translation:
        type: "masquerade"  # masquerade, static
        # OR for static:
        # type: "static"
        # address: "203.0.113.10"

  # Destination NAT (inbound/port forwarding)
  destination:
    - name: "web-server"
      enabled: true

      source:
        zones: ["wan"]
        addresses: ["any"]

      destination:
        zones: ["wan"]
        addresses: ["203.0.113.10"]

      service:
        protocols: ["tcp"]
        ports: ["443"]

      translation:
        address: "192.168.1.100"
        port: 443

    - name: "ssh-forward"
      enabled: true

      source:
        zones: ["wan"]

      destination:
        zones: ["wan"]
        addresses: ["203.0.113.10"]

      service:
        protocols: ["tcp"]
        ports: ["2222"]

      translation:
        address: "192.168.1.50"
        port: 22

  # 1-to-1 NAT
  static:
    - name: "mail-server"
      enabled: true
      external_ip: "203.0.113.11"
      internal_ip: "192.168.1.50"
```

---

## VPN Configuration

VPN tunnels and remote access.

```yaml
vpn:
  # Site-to-Site VPN
  site_to_site:
    - name: "branch-office"
      enabled: true
      type: "ipsec"

      # Local settings
      local:
        interface: "wan1"
        id: "203.0.113.10"
        subnets:
          - "192.168.1.0/24"
          - "192.168.10.0/24"

      # Remote settings
      remote:
        gateway: "198.51.100.10"
        id: "198.51.100.10"
        subnets:
          - "192.168.2.0/24"
          - "192.168.20.0/24"

      # Authentication
      authentication:
        method: "psk"
        preshared_key: "your-pre-shared-key"

      # Phase 1 (IKE)
      phase1:
        mode: "ikev2"  # ikev1, ikev2
        encryption: "aes256"
        hash: "sha256"
        dh_group: 14
        lifetime: 28800

      # Phase 2 (IPsec)
      phase2:
        encryption: "aes256"
        hash: "sha256"
        pfs_group: 14
        lifetime: 3600

      # Dead Peer Detection
      dpd:
        enabled: true
        interval: 30
        timeout: 120

  # Remote Access VPN
  remote_access:
    - name: "ssl-vpn"
      enabled: true
      type: "ssl"  # ssl, ipsec, l2tp

      # Server settings
      listen_port: 443

      # Client IP pool
      client_pool: "vpn-pool"
      # OR inline:
      # client_range:
      #   start: "10.10.10.10"
      #   end: "10.10.10.100"

      # Authentication
      authentication:
        method: "local"  # local, radius, ldap

        users:
          - username: "vpnuser1"
            password: "user-password"
          - username: "vpnuser2"
            password: "user-password"

      # Network access
      allowed_networks:
        - "192.168.1.0/24"
        - "192.168.10.0/24"

      # DNS for clients
      dns_servers:
        - "192.168.1.1"
        - "1.1.1.1"

      # Split tunnel
      split_tunnel: true
```

---

## Wireless Networks

WiFi/WLAN configuration (SSID definitions).

```yaml
wireless:
  # Wireless networks (SSIDs)
  networks:
    - name: "corporate"
      ssid: "CompanyWiFi"
      enabled: true

      # Security
      security:
        mode: "wpa2-psk"  # open, wpa2-psk, wpa2-enterprise, wpa3-psk
        passphrase: "SecurePassword123"
        # For enterprise:
        # mode: "wpa2-enterprise"
        # radius_server: "192.168.1.100"
        # radius_secret: "radius-secret"

      # Network assignment
      vlan: 1
      network: "lan1"

      # Broadcasting
      broadcast_ssid: true

      # Band
      bands: ["2.4ghz", "5ghz"]  # 2.4ghz, 5ghz, both

      # Fast roaming
      fast_roaming: true

      # Client limits
      max_clients: 100

    - name: "guest"
      ssid: "Guest WiFi"
      enabled: true

      security:
        mode: "wpa2-psk"
        passphrase: "GuestPassword456"

      # Guest settings
      guest_network: true

      # Captive portal
      portal:
        enabled: true
        type: "click-through"  # click-through, password, voucher
        session_timeout: 480  # minutes

      # Isolation
      client_isolation: true

      vlan: 20
      network: "vlan20"
      broadcast_ssid: true
      bands: ["2.4ghz", "5ghz"]

    - name: "iot"
      ssid: "IoT-Devices"
      enabled: true

      security:
        mode: "wpa2-psk"
        passphrase: "IoTPassword789"

      vlan: 30
      network: "vlan30"

      # IoT-specific: 2.4GHz only
      broadcast_ssid: false
      bands: ["2.4ghz"]
      max_clients: 100
```

---

## Access Points

Physical AP configuration.

```yaml
access_points:
  - name: "ap-office-1"
    mac: "00:00:00:00:00:01"
    enabled: true

    # Location
    location: "Office - Floor 1"

    # Networks (SSIDs) this AP broadcasts
    networks:
      - "corporate"
      - "guest"

    # Radio settings
    radios:
      # 2.4GHz radio
      - band: "2.4ghz"
        enabled: true
        channel: "auto"  # auto, or specific channel
        channel_width: 20  # 20, 40
        power: "auto"  # auto, or dBm value

      # 5GHz radio
      - band: "5ghz"
        enabled: true
        channel: "auto"
        channel_width: 80  # 20, 40, 80, 160
        power: "auto"

    # LED control
    led_enabled: true

  - name: "ap-office-2"
    mac: "00:00:00:00:00:02"
    enabled: true
    location: "Office - Floor 2"
    networks:
      - "corporate"
      - "guest"

    radios:
      - band: "2.4ghz"
        enabled: true
        channel: "auto"
        channel_width: 20
        power: "auto"
      - band: "5ghz"
        enabled: true
        channel: "auto"
        channel_width: 80
        power: "auto"
```

---

## Switch Configuration

Switch and port configuration.

```yaml
switches:
  - name: "switch-main"
    mac: "00:00:00:00:00:03"
    enabled: true

    # Global switch settings
    settings:
      stp:
        enabled: true
        mode: "rstp"  # stp, rstp, mstp
        priority: 32768

      igmp_snooping: true
      jumbo_frames: false

    # Port configuration
    ports:
      # Uplink port
      - port: 1
        name: "uplink-to-router"
        enabled: true

        mode: "trunk"
        native_vlan: 1
        allowed_vlans: [1, 10, 20, 30]

        speed: "auto"
        duplex: "auto"

        poe:
          enabled: false

      # Access ports
      - port: 2
        name: "workstation-1"
        enabled: true

        mode: "access"
        vlan: 1

        speed: "auto"
        duplex: "auto"

        poe:
          enabled: false

      # PoE port for AP
      - port: 10
        name: "ap-office-1"
        enabled: true

        mode: "access"
        vlan: 1

        speed: "auto"
        duplex: "auto"

        poe:
          enabled: true
          priority: "high"
          max_power: 30  # watts

      # Trunk port to another switch
      - port: 24
        name: "trunk-to-switch2"
        enabled: true

        mode: "trunk"
        native_vlan: 1
        allowed_vlans: [1, 10, 20, 30, 100]

        speed: "1000"
        duplex: "full"

    # Link aggregation
    lag:
      - name: "lag1"
        ports: [23, 24]
        mode: "lacp"  # lacp, static
```

---

## Quality of Service

Traffic prioritization and shaping.

```yaml
qos:
  enabled: true

  # Traffic classes
  classes:
    - name: "critical"
      priority: 1
      guaranteed_bandwidth: 20  # percent
      max_bandwidth: 100

    - name: "high"
      priority: 2
      guaranteed_bandwidth: 30
      max_bandwidth: 80

    - name: "medium"
      priority: 3
      guaranteed_bandwidth: 20
      max_bandwidth: 60

    - name: "low"
      priority: 4
      guaranteed_bandwidth: 10
      max_bandwidth: 40

  # Classification rules
  rules:
    - name: "voip-critical"
      enabled: true

      match:
        protocols: ["udp"]
        ports: ["5060-5061"]

      class: "critical"

    - name: "video-conferencing"
      enabled: true

      match:
        applications: ["zoom", "teams", "webex"]

      class: "high"

    - name: "bulk-transfer"
      enabled: true

      match:
        applications: ["bittorrent", "ftp"]

      class: "low"

  # Bandwidth limits
  limits:
    - interface: "wan1"
      upload: 50000  # kbps
      download: 200000
```

---

## User Authentication

User database and authentication services.

```yaml
authentication:
  # Local users
  local_users:
    - username: "admin"
      password: "admin-password"
      role: "admin"

    - username: "user1"
      password: "user-password"
      role: "user"

  # External authentication servers
  servers:
    # RADIUS
    - name: "radius-primary"
      type: "radius"
      enabled: true

      host: "192.168.1.100"
      port: 1812
      secret: "radius-secret"
      timeout: 5

    # LDAP / Active Directory
    - name: "active-directory"
      type: "ldap"
      enabled: true

      host: "192.168.1.50"
      port: 389
      use_ssl: false

      base_dn: "dc=example,dc=com"
      bind_dn: "cn=admin,dc=example,dc=com"
      bind_password: "ldap-password"

    # TACACS+
    - name: "tacacs-server"
      type: "tacacs"
      enabled: false

      host: "192.168.1.60"
      port: 49
      secret: "tacacs-secret"
```

---

## Logging

Logging and monitoring configuration.

```yaml
logging:
  # Local logging
  local:
    enabled: true
    level: "info"  # debug, info, warning, error, critical

  # Remote syslog
  syslog:
    enabled: true

    servers:
      - host: "192.168.1.101"
        port: 514
        protocol: "tcp"  # tcp, udp
        facility: "local0"
        level: "info"

  # Log types
  log_types:
    traffic: true
    security: true
    system: true
    debug: false

  # Alerts
  alerts:
    email:
      enabled: true
      smtp_server: "smtp.gmail.com"
      smtp_port: 587
      use_tls: true
      from: "router@example.com"
      username: "router@example.com"
      password: "email-password"

      recipients:
        - "admin@example.com"

      # Alert levels
      levels: ["critical", "error", "warning"]
```

---

## High Availability

Clustering and failover configuration.

```yaml
high_availability:
  enabled: true
  mode: "active-passive"  # active-passive, active-active

  # Cluster settings
  cluster:
    id: 1
    priority: 100  # Higher is preferred
    password: "ha-cluster-password"

  # Peer information
  peer:
    ip: "192.168.99.2"

  # Heartbeat
  heartbeat:
    interval: 1000  # milliseconds
    interfaces:
      - "lan1"
      - "dedicated-ha"

  # Virtual/shared IPs
  virtual_ips:
    - interface: "wan1"
      ip: "203.0.113.12/30"

    - interface: "lan1"
      ip: "192.168.1.1/24"

  # Monitoring
  monitoring:
    interfaces:
      - "wan1"
      - "lan1"

    check_interval: 5
    failure_threshold: 3

  # Failover
  failover:
    auto_failback: false
    failback_delay: 60  # seconds

  # State synchronization
  sync:
    connections: true
    dhcp_leases: true
    configuration: true
```

---

## Vendor Extensions

Vendor-specific features not covered by the unified schema.

```yaml
# Vendor extensions allow access to vendor-specific features
vendor_extensions:
  # MikroTik specific
  mikrotik:
    # Hotspot
    hotspot:
      enabled: true
      interface: "vlan20"
      address_pool: "guest-dhcp"

  # Fortinet specific
  fortinet:
    # SD-WAN
    sdwan:
      enabled: true
      members:
        - interface: "wan1"
          weight: 100
        - interface: "wan2"
          weight: 50

      health_checks:
        - name: "google-dns"
          server: "8.8.8.8"
          protocol: "ping"

  # Ubiquiti specific
  ubiquiti:
    # DPI
    dpi:
      enabled: true

    # Threat management
    threat_management:
      ips:
        enabled: true
        mode: "detection"

  # WatchGuard specific
  watchguard:
    # APT Blocker
    apt_blocker:
      enabled: true
      sensitivity: "medium"

    # Reputation Enabled Defense
    reputation:
      enabled: true
      threat_level: "moderate"
```

---

## Complete Example Configuration

Here's a complete unified configuration example:

```yaml
# Complete Unified Configuration Example
# Small office router with VLANs, WiFi, and VPN

device:
  name: "router-office-01"
  vendor: "mikrotik"  # Can be changed to any vendor
  location: "Main Office"

system:
  hostname: "Office-Router"
  timezone: "America/New_York"

  ntp:
    enabled: true
    servers:
      - "pool.ntp.org"

  users:
    - username: "admin"
      password: "secure-password"
      role: "admin"

interfaces:
  - name: "wan1"
    type: "physical"
    enabled: true
    description: "Internet connection"
    addressing:
      mode: "dhcp"
    zone: "wan"

  - name: "lan1"
    type: "physical"
    enabled: true
    description: "Main LAN"
    addressing:
      mode: "static"
      ipv4: "192.168.1.1/24"
    zone: "lan"

  - name: "vlan20"
    type: "vlan"
    enabled: true
    description: "Guest network"
    vlan:
      id: 20
      parent: "lan1"
    addressing:
      mode: "static"
      ipv4: "192.168.20.1/24"
    zone: "guest"

vlans:
  - id: 1
    name: "default"
  - id: 20
    name: "guest"

dhcp:
  servers:
    - name: "lan-dhcp"
      interface: "lan1"
      enabled: true
      start_ip: "192.168.1.100"
      end_ip: "192.168.1.200"
      gateway: "192.168.1.1"
      dns_servers:
        - "192.168.1.1"
        - "1.1.1.1"
      lease_time: 86400

    - name: "guest-dhcp"
      interface: "vlan20"
      enabled: true
      start_ip: "192.168.20.50"
      end_ip: "192.168.20.200"
      gateway: "192.168.20.1"
      dns_servers:
        - "192.168.20.1"
      lease_time: 3600

dns:
  proxy:
    enabled: true
    servers:
      - "1.1.1.1"
      - "8.8.8.8"

routes:
  static:
    - name: "default"
      destination: "0.0.0.0/0"
      gateway: "dhcp"
      interface: "wan1"

firewall:
  aliases:
    networks:
      - name: "lan-subnet"
        network: "192.168.1.0/24"
      - name: "guest-subnet"
        network: "192.168.20.0/24"

  rules:
    - name: "allow-established"
      enabled: true
      order: 10
      source:
        zones: ["any"]
      destination:
        zones: ["any"]
      state: ["established", "related"]
      action: "accept"

    - name: "lan-to-internet"
      enabled: true
      order: 100
      source:
        zones: ["lan"]
        addresses: ["lan-subnet"]
      destination:
        zones: ["wan"]
      service:
        protocols: ["any"]
      action: "accept"
      nat:
        enabled: true
        type: "masquerade"

    - name: "guest-to-internet"
      enabled: true
      order: 110
      source:
        zones: ["guest"]
        addresses: ["guest-subnet"]
      destination:
        zones: ["wan"]
      service:
        protocols: ["any"]
      action: "accept"
      nat:
        enabled: true
        type: "masquerade"

    - name: "block-guest-to-lan"
      enabled: true
      order: 200
      source:
        zones: ["guest"]
      destination:
        zones: ["lan"]
      service:
        protocols: ["any"]
      action: "drop"
      log: true

wireless:
  networks:
    - name: "office-wifi"
      ssid: "OfficeWiFi"
      enabled: true
      security:
        mode: "wpa2-psk"
        passphrase: "SecurePassword123"
      vlan: 1
      network: "lan1"
      broadcast_ssid: true
      bands: ["2.4ghz", "5ghz"]

    - name: "guest-wifi"
      ssid: "Guest"
      enabled: true
      security:
        mode: "wpa2-psk"
        passphrase: "GuestPass456"
      guest_network: true
      portal:
        enabled: true
        type: "click-through"
      client_isolation: true
      vlan: 20
      network: "vlan20"
      bands: ["2.4ghz", "5ghz"]

vpn:
  remote_access:
    - name: "ssl-vpn"
      enabled: true
      type: "ssl"
      listen_port: 443
      client_range:
        start: "10.10.10.10"
        end: "10.10.10.100"
      authentication:
        method: "local"
        users:
          - username: "vpnuser1"
            password: "vpn-password"
      allowed_networks:
        - "192.168.1.0/24"
      dns_servers:
        - "192.168.1.1"
      split_tunnel: true

logging:
  local:
    enabled: true
    level: "info"

  syslog:
    enabled: true
    servers:
      - host: "192.168.1.100"
        port: 514
        protocol: "udp"
```

---

## Vendor Translation Matrix

This table shows how unified schema elements map to vendor-specific configurations:

| Unified Element | MikroTik | Fortinet | Ubiquiti | WatchGuard |
|----------------|----------|----------|----------|------------|
| `system.hostname` | `/system identity` | `config system global set hostname` | `system.name` | `device_name` |
| `interfaces[].name` | `/interface` | `config system interface edit` | `networks[]` | `interfaces[]` |
| `vlans[].id` | `/interface vlan` | `config system interface` | `networks[].vlan` | `vlans[]` |
| `dhcp.servers[]` | `/ip dhcp-server` | `config system dhcp server` | `networks[].dhcpd_*` | `dhcp_servers[]` |
| `firewall.rules[]` | `/ip firewall filter` | `config firewall policy` | `firewallrules[]` | `policies[]` |
| `nat.source[]` | `/ip firewall nat` | `nat: enable` in policy | Built into firewall | `nat: true` in policy |
| `vpn.site_to_site[]` | `/interface ipsec` | `config vpn ipsec` | `vpn.site_to_site` | `bovpn[]` |
| `wireless.networks[]` | `/interface wireless` | `config wireless-controller vap` | `wlans[]` | `wireless_networks[]` |
| `routes.static[]` | `/ip route` | `config router static` | `routes.static` | `routes.static` |

---

## Best Practices for Unified Configuration

### 1. Use Zones Consistently

Define clear security zones and use them consistently:
- `wan` - Internet-facing interfaces
- `lan` - Trusted internal network
- `guest` - Guest/untrusted networks
- `dmz` - DMZ servers
- `vpn` - VPN clients

### 2. Leverage Aliases

Use aliases for IPs and networks that are referenced multiple times:

```yaml
firewall:
  aliases:
    networks:
      - name: "trusted-networks"
        network: "192.168.0.0/16"
```

### 3. Order Rules Properly

Use `order` field to control rule evaluation:
- 1-100: Allow established/related
- 100-500: Allow rules
- 500-1000: Deny rules
- 1000+: Cleanup rules

### 4. Be Explicit

Specify all parameters even if they have defaults:

```yaml
interfaces:
  - name: "wan1"
    type: "physical"
    enabled: true  # Explicit
    description: "Primary WAN"  # Descriptive
```

### 5. Test Vendor Portability

Test your configuration on multiple vendors to ensure portability:

```bash
# Test on MikroTik
orchenet apply config.yaml --vendor mikrotik --dry-run

# Test on Fortinet
orchenet apply config.yaml --vendor fortinet --dry-run
```

---

## Limitations and Vendor Differences

### Feature Parity

Not all vendors support all features equally:

| Feature | MikroTik | Fortinet | Ubiquiti | WatchGuard |
|---------|----------|----------|----------|------------|
| Basic Routing | ✅ | ✅ | ✅ | ✅ |
| OSPF | ✅ | ✅ | ❌ | ✅ |
| BGP | ✅ | ✅ | ❌ | ✅ |
| IPsec VPN | ✅ | ✅ | ✅ | ✅ |
| SSL VPN | ❌ | ✅ | ❌ | ✅ |
| IPS | ❌ | ✅ | ✅ | ✅ |
| Application Control | Limited | ✅ | ✅ | ✅ |
| SD-WAN | ❌ | ✅ | ✅ | ❌ |

### Translation Behavior

- **Best Effort**: OrcheNet translates configuration to the closest vendor equivalent
- **Warnings**: Unsupported features generate warnings
- **Errors**: Critical incompatibilities generate errors
- **Extensions**: Use `vendor_extensions` for vendor-specific features

### Validation

OrcheNet validates configuration before applying:

```yaml
# This will fail on Ubiquiti (no OSPF support)
routes:
  ospf:
    enabled: true
```

Error: `OSPF not supported on vendor 'ubiquiti'`

---

## Schema Version

Schema Version: 1.0.0
Last Updated: 2024-10-27
Supported Vendors: MikroTik RouterOS 7.x, FortiOS 7.x, UniFi Network 8.x, Fireware OS 12.x
