# OrcheNet Configuration Schema - WatchGuard

This document defines the complete YAML configuration schema for managing WatchGuard devices through OrcheNet. This includes Firebox firewalls, WatchGuard AP access points, and WatchGuard switches.

## WatchGuard Configuration Overview

WatchGuard devices use Fireware OS for firewalls and cloud-managed configuration for access points. Configuration can be managed through Policy Manager, Web UI, or CLI. OrcheNet translates vendor-agnostic YAML into WatchGuard configuration format (XML-based for Firebox).

---

## Table of Contents

### Firebox Firewall
- [System Configuration](#firebox-system-configuration)
- [Network Interfaces](#firebox-network-interfaces)
- [VLANs](#firebox-vlans)
- [Aliases](#firebox-aliases)
- [DHCP Server](#firebox-dhcp-server)
- [DNS](#firebox-dns)
- [Static Routes](#firebox-static-routes)
- [Dynamic Routing](#firebox-dynamic-routing)
- [Firewall Policies](#firebox-firewall-policies)
- [NAT](#firebox-nat)
- [VPN](#firebox-vpn)
- [Security Services](#firebox-security-services)
- [High Availability](#firebox-high-availability)
- [Traffic Management](#firebox-traffic-management)
- [Authentication](#firebox-authentication)
- [Logging](#firebox-logging)

### WatchGuard AP
- [AP Configuration](#watchguard-ap-configuration)
- [Wireless Networks](#watchguard-wireless-networks)
- [Radio Settings](#watchguard-radio-settings)
- [Guest Access](#watchguard-guest-access)

### WatchGuard Switch
- [Switch Configuration](#watchguard-switch-configuration)
- [Port Configuration](#watchguard-port-configuration)
- [VLANs](#watchguard-switch-vlans)

---

# Firebox Firewall Configuration

## Firebox System Configuration

Global system settings for WatchGuard Firebox.

```yaml
watchguard:
  firebox:
    system:
      # Device identification
      device_name: "FBX-HQ-01"
      location: "Headquarters"
      contact: "admin@example.com"

      # Time settings
      timezone: "America/New_York"
      ntp:
        enabled: true
        servers:
          - "pool.ntp.org"
          - "time.google.com"
        sync_interval: 3600

      # Management
      management:
        # Web UI
        web_ui:
          enabled: true
          port: 8080
          https_port: 8443
          session_timeout: 30

        # SSH
        ssh:
          enabled: true
          port: 4118
          timeout: 300

        # Management tunnel
        management_tunnel:
          enabled: true

      # WatchGuard Cloud
      cloud:
        enabled: true
        activation_key: "xxxx-xxxx-xxxx-xxxx"

      # SNMP
      snmp:
        enabled: true
        version: "v2c"
        community: "public"
        location: "Datacenter A"
        contact: "admin@example.com"
        trap_destinations:
          - host: "192.168.1.100"
            community: "public"
            port: 162

      # Feature keys
      feature_keys:
        - key: "APT-xxxxx-xxxxx"
          description: "APT Blocker"
        - key: "IPS-xxxxx-xxxxx"
          description: "Intrusion Prevention"

      # Logging
      log_server:
        enabled: true
        server: "192.168.1.101"
        port: 514
        protocol: "tcp"  # tcp, udp

      # Notifications
      notifications:
        email:
          enabled: true
          smtp_server: "smtp.gmail.com"
          smtp_port: 587
          from: "firebox@example.com"
          username: "firebox@example.com"
          password: "email-password"
          use_tls: true
          recipients:
            - "admin@example.com"

        # Alert types
        alerts:
          - type: "critical"
            enabled: true
          - type: "warning"
            enabled: true
          - type: "information"
            enabled: false
```

---

## Firebox Network Interfaces

Interface configuration including external, trusted, optional, and custom.

```yaml
watchguard:
  firebox:
    interfaces:
      # External interface (WAN)
      - name: "External"
        type: "external"
        mode: "dhcp"  # dhcp, static, pppoe
        enabled: true

        # For static mode:
        # mode: "static"
        # ip: "203.0.113.10"
        # netmask: "255.255.255.252"
        # gateway: "203.0.113.9"

        # Link settings
        link:
          speed: "auto"  # auto, 10, 100, 1000
          duplex: "auto"  # auto, half, full
          mtu: 1500

        # Failover (for HA)
        monitor_ip: "8.8.8.8"

      # Trusted interface (LAN)
      - name: "Trusted"
        type: "trusted"
        mode: "static"
        ip: "192.168.1.1"
        netmask: "255.255.255.0"
        enabled: true

        link:
          speed: "auto"
          duplex: "auto"
          mtu: 1500

        # DHCP relay
        dhcp_relay:
          enabled: false
          server: ""

      # Optional interface
      - name: "Optional"
        type: "optional"
        mode: "static"
        ip: "192.168.2.1"
        netmask: "255.255.255.0"
        enabled: true

        link:
          speed: "auto"
          duplex: "auto"
          mtu: 1500

      # Custom interface
      - name: "DMZ"
        type: "custom"
        mode: "static"
        ip: "192.168.100.1"
        netmask: "255.255.255.0"
        enabled: true
        security_zone: "dmz"

        link:
          speed: "1000"
          duplex: "full"
          mtu: 1500

      # Bridge interface
      - name: "Bridge-LAN"
        type: "bridge"
        enabled: true
        members:
          - "Trusted"
          - "Optional"
        stp_enabled: true

      # VLAN interface
      - name: "VLAN-Management"
        type: "vlan"
        parent_interface: "Trusted"
        vlan_id: 10
        mode: "static"
        ip: "192.168.10.1"
        netmask: "255.255.255.0"
        enabled: true

      # PPPoE
      - name: "External-PPPoE"
        type: "external"
        mode: "pppoe"
        enabled: false
        pppoe:
          username: "user@isp.com"
          password: "pppoe-password"
          service_name: ""
          mtu: 1492
```

---

## Firebox VLANs

VLAN configuration for interface segmentation.

```yaml
watchguard:
  firebox:
    vlans:
      - vlan_id: 10
        name: "Management"
        description: "Management VLAN"
        parent_interface: "Trusted"
        ip: "192.168.10.1"
        netmask: "255.255.255.0"
        enabled: true

      - vlan_id: 20
        name: "Guest"
        description: "Guest network"
        parent_interface: "Trusted"
        ip: "192.168.20.1"
        netmask: "255.255.255.0"
        enabled: true

      - vlan_id: 30
        name: "IoT"
        description: "IoT devices"
        parent_interface: "Trusted"
        ip: "192.168.30.1"
        netmask: "255.255.255.0"
        enabled: true

      - vlan_id: 100
        name: "Servers"
        description: "Server network"
        parent_interface: "Optional"
        ip: "192.168.100.1"
        netmask: "255.255.255.0"
        enabled: true
```

---

## Firebox Aliases

Network aliases for use in policies and rules.

```yaml
watchguard:
  firebox:
    aliases:
      # Host aliases
      - name: "WebServer1"
        type: "host"
        ip: "192.168.1.100"
        description: "Primary web server"

      - name: "MailServer"
        type: "host"
        ip: "192.168.1.50"
        description: "Email server"

      # Network aliases
      - name: "TrustedNetwork"
        type: "network"
        ip: "192.168.1.0"
        netmask: "255.255.255.0"
        description: "Main LAN"

      - name: "GuestNetwork"
        type: "network"
        ip: "192.168.20.0"
        netmask: "255.255.255.0"
        description: "Guest WiFi"

      # Range aliases
      - name: "GuestRange"
        type: "range"
        start_ip: "192.168.20.50"
        end_ip: "192.168.20.100"
        description: "Guest DHCP range"

      # FQDN aliases
      - name: "SaaS-Service"
        type: "fqdn"
        fqdn: "app.example.com"
        description: "External SaaS application"

      # Group aliases
      - name: "InternalServers"
        type: "group"
        members:
          - "WebServer1"
          - "MailServer"
        description: "All internal servers"

      # Service aliases (ports)
      - name: "WebServices"
        type: "service"
        protocol: "tcp"
        ports: "80,443"
        description: "HTTP and HTTPS"

      - name: "CustomApp"
        type: "service"
        protocol: "tcp"
        ports: "8000-8100"
        description: "Custom application ports"
```

---

## Firebox DHCP Server

DHCP server configuration.

```yaml
watchguard:
  firebox:
    dhcp_servers:
      # Trusted network DHCP
      - interface: "Trusted"
        enabled: true
        start_ip: "192.168.1.100"
        end_ip: "192.168.1.200"
        netmask: "255.255.255.0"
        gateway: "192.168.1.1"
        lease_time: 86400

        dns_servers:
          - "192.168.1.1"
          - "1.1.1.1"

        domain_name: "local.lan"

        # DHCP options
        options:
          - code: 66
            type: "string"
            value: "192.168.1.10"
            description: "TFTP server"

        # Static mappings
        static_mappings:
          - mac: "00:11:22:33:44:55"
            ip: "192.168.1.50"
            hostname: "server1"
            description: "File server"

      # Guest VLAN DHCP
      - interface: "VLAN-Guest"
        enabled: true
        start_ip: "192.168.20.50"
        end_ip: "192.168.20.200"
        netmask: "255.255.255.0"
        gateway: "192.168.20.1"
        lease_time: 3600

        dns_servers:
          - "192.168.20.1"
          - "1.1.1.1"

        domain_name: "guest.local"
```

---

## Firebox DNS

DNS proxy and forwarding configuration.

```yaml
watchguard:
  firebox:
    dns:
      # DNS proxy
      proxy:
        enabled: true

        # Forwarders
        forwarders:
          - "1.1.1.1"
          - "8.8.8.8"

        # DNS security
        dns_watchguard:
          enabled: true
          category_filtering: true
          malware_filtering: true

      # Static DNS entries
      static_entries:
        - hostname: "server1.local.lan"
          ip: "192.168.1.100"
        - hostname: "server2.local.lan"
          ip: "192.168.1.101"

      # Domain blocking
      blocked_domains:
        - "malicious.example.com"
        - "*.badsite.com"
```

---

## Firebox Static Routes

Static routing configuration.

```yaml
watchguard:
  firebox:
    routes:
      static:
        - name: "DefaultRoute"
          enabled: true
          destination: "0.0.0.0"
          netmask: "0.0.0.0"
          gateway: "203.0.113.9"
          interface: "External"
          metric: 1
          description: "Default route to ISP"

        - name: "InternalNetwork"
          enabled: true
          destination: "10.0.0.0"
          netmask: "255.0.0.0"
          gateway: "192.168.1.254"
          interface: "Trusted"
          metric: 10
          description: "Route to internal network"

        - name: "RemoteSite"
          enabled: true
          destination: "172.16.0.0"
          netmask: "255.255.0.0"
          gateway: "vpn"
          interface: "BOVPN-RemoteSite"
          metric: 20
          description: "Route over VPN"

        - name: "Blackhole"
          enabled: true
          destination: "192.168.100.0"
          netmask: "255.255.255.0"
          gateway: "blackhole"
          metric: 254
          description: "Drop traffic to unused network"
```

---

## Firebox Dynamic Routing

OSPF and BGP configuration.

```yaml
watchguard:
  firebox:
    routes:
      # OSPF
      ospf:
        enabled: true
        router_id: "1.1.1.1"

        areas:
          - area_id: "0.0.0.0"
            type: "standard"
            authentication: "none"  # none, simple, md5

            networks:
              - network: "192.168.1.0"
                netmask: "255.255.255.0"

              - network: "192.168.10.0"
                netmask: "255.255.255.0"

        interfaces:
          - interface: "Trusted"
            area: "0.0.0.0"
            cost: 10
            priority: 1
            hello_interval: 10
            dead_interval: 40
            retransmit_interval: 5

        redistribution:
          - source: "static"
            enabled: true
            metric: 100
            metric_type: 2

          - source: "connected"
            enabled: true
            metric: 50

      # BGP
      bgp:
        enabled: false
        as_number: 65001
        router_id: "1.1.1.1"

        neighbors:
          - ip: "203.0.113.9"
            remote_as: 65000
            description: "ISP BGP peer"
            password: "bgp-password"
            timers:
              keepalive: 60
              holdtime: 180

        networks:
          - network: "192.168.0.0"
            netmask: "255.255.0.0"

        redistribution:
          - source: "static"
            enabled: true
          - source: "ospf"
            enabled: true
```

---

## Firebox Firewall Policies

Packet filter policies for traffic control.

```yaml
watchguard:
  firebox:
    policies:
      # Outbound policies
      - name: "Outgoing"
        enabled: true
        policy_type: "outgoing"
        from:
          - "Trusted"
          - "Optional"
        to:
          - "External"

        # Source
        source:
          - "TrustedNetwork"

        # Destination
        destination:
          - "Any-External"

        # Services
        services:
          - "HTTP"
          - "HTTPS"
          - "DNS"
          - "SMTP"
          - "POP3"
          - "IMAP"

        # Action
        action: "allow"

        # NAT
        nat: true
        nat_type: "dynamic"  # dynamic, static, 1-to-1

        # Logging
        log_enabled: true
        log_level: "send"  # none, send, send-recv

        # Security services
        security_services:
          gateway_antivirus: true
          intrusion_prevention: true
          apt_blocker: true
          reputation_enabled: true
          spamblocker: false
          webfilter: true

        # QoS
        qos:
          enabled: false

        # Schedule
        schedule: "Always"

      # Incoming policy (port forwarding)
      - name: "WebServer-Inbound"
        enabled: true
        policy_type: "incoming"
        from:
          - "External"
        to:
          - "Trusted"

        source:
          - "Any-External"

        destination:
          - "WebServer1"

        services:
          - "HTTPS"

        action: "allow"

        nat: true
        nat_type: "static"
        nat_destination: "WebServer1"

        log_enabled: true
        log_level: "send-recv"

        security_services:
          gateway_antivirus: true
          intrusion_prevention: true
          apt_blocker: true

      # Custom policy (inter-VLAN)
      - name: "Guest-to-Internet"
        enabled: true
        policy_type: "custom"
        from:
          - "VLAN-Guest"
        to:
          - "External"

        source:
          - "GuestNetwork"

        destination:
          - "Any-External"

        services:
          - "HTTP"
          - "HTTPS"
          - "DNS"

        action: "allow"

        nat: true
        nat_type: "dynamic"

        log_enabled: true

        security_services:
          webfilter: true
          reputation_enabled: true

      # Block policy
      - name: "Block-Guest-to-LAN"
        enabled: true
        policy_type: "custom"
        from:
          - "VLAN-Guest"
        to:
          - "Trusted"

        source:
          - "GuestNetwork"

        destination:
          - "TrustedNetwork"

        services:
          - "Any"

        action: "deny"

        log_enabled: true
        log_level: "send"

      # VoIP priority
      - name: "VoIP-Priority"
        enabled: true
        policy_type: "outgoing"
        from:
          - "Trusted"
        to:
          - "External"

        source:
          - "TrustedNetwork"

        destination:
          - "Any-External"

        services:
          - "SIP"
          - "RTP"

        action: "allow"

        nat: true

        qos:
          enabled: true
          priority: "high"
          bandwidth_limit: 0

      # Time-based policy
      - name: "Business-Hours-Only"
        enabled: true
        policy_type: "outgoing"
        from:
          - "Trusted"
        to:
          - "External"

        source:
          - "TrustedNetwork"

        destination:
          - "SaaS-Service"

        services:
          - "HTTPS"

        action: "allow"

        nat: true
        schedule: "BusinessHours"
```

---

## Firebox NAT

Network Address Translation configuration.

```yaml
watchguard:
  firebox:
    nat:
      # Dynamic NAT (built into policies usually)
      dynamic:
        - name: "LAN-to-Internet"
          enabled: true
          source_interface: "Trusted"
          destination_interface: "External"
          source_network: "192.168.1.0/24"
          nat_type: "dynamic"

      # Static NAT (1-to-1)
      static:
        - name: "WebServer-NAT"
          enabled: true
          external_ip: "203.0.113.10"
          internal_ip: "192.168.1.100"
          description: "Web server 1-to-1 NAT"

        - name: "MailServer-NAT"
          enabled: true
          external_ip: "203.0.113.11"
          internal_ip: "192.168.1.50"
          description: "Mail server 1-to-1 NAT"

      # Virtual IP (port forwarding)
      virtual_ip:
        - name: "HTTPS-Forward"
          enabled: true
          external_ip: "203.0.113.10"
          external_port: 443
          protocol: "tcp"
          internal_ip: "192.168.1.100"
          internal_port: 443
          description: "HTTPS to web server"

        - name: "SSH-Forward"
          enabled: true
          external_ip: "203.0.113.10"
          external_port: 2222
          protocol: "tcp"
          internal_ip: "192.168.1.50"
          internal_port: 22
          description: "SSH to management server"
```

---

## Firebox VPN

VPN configuration including Branch Office VPN, Mobile VPN, and SSL VPN.

```yaml
watchguard:
  firebox:
    vpn:
      # Branch Office VPN (BOVPN)
      bovpn:
        - name: "RemoteOffice-VPN"
          enabled: true
          type: "ike2"  # ike1, ike2

          # Local gateway
          local_gateway:
            external_interface: "External"
            local_id_type: "ip"  # ip, fqdn, email
            local_id: "203.0.113.10"

          # Remote gateway
          remote_gateway:
            ip: "198.51.100.10"
            remote_id_type: "ip"
            remote_id: "198.51.100.10"

          # Authentication
          authentication:
            method: "preshared_key"
            preshared_key: "your-pre-shared-key"

          # Phase 1
          phase1:
            encryption: "aes256"
            authentication: "sha256"
            dh_group: 14
            lifetime: 28800
            dpd_enabled: true
            dpd_interval: 30

          # Phase 2
          phase2:
            encryption: "aes256"
            authentication: "sha256"
            pfs_enabled: true
            pfs_group: 14
            lifetime: 3600

          # Routes
          local_networks:
            - "192.168.1.0/24"
            - "192.168.10.0/24"

          remote_networks:
            - "192.168.2.0/24"
            - "192.168.20.0/24"

          # Advanced
          tunnel_routing: true
          route_based: false
          persistent_tunnel: false

      # Mobile VPN (IPSec)
      mobile_vpn:
        ipsec:
          enabled: true

          # Server settings
          virtual_ip_pool:
            start: "10.10.10.10"
            end: "10.10.10.100"
            netmask: "255.255.255.0"

          # Authentication
          authentication:
            method: "xauth"  # xauth, certificate
            users:
              - username: "vpnuser1"
                password: "user-password"
              - username: "vpnuser2"
                password: "user-password"

          # Phase 1
          phase1:
            encryption: "aes256"
            authentication: "sha256"
            dh_group: 14

          # Phase 2
          phase2:
            encryption: "aes256"
            authentication: "sha256"
            pfs_enabled: true
            pfs_group: 14

          # Split tunneling
          split_tunneling:
            enabled: true
            networks:
              - "192.168.1.0/24"
              - "192.168.10.0/24"

          # DNS
          dns_servers:
            - "192.168.1.1"
            - "1.1.1.1"

      # SSL VPN
      ssl_vpn:
        enabled: true

        # Server settings
        port: 443
        virtual_ip_pool:
          start: "10.20.30.10"
          end: "10.20.30.100"

        # Authentication
        authentication:
          local_users: true
          radius: false
          ldap: false

        # Client settings
        allow_windows_client: true
        allow_mac_client: true
        allow_linux_client: true
        allow_mobile_client: true

        # Network access
        tunnel_mode: "split"  # full, split
        split_tunnel_networks:
          - "192.168.1.0/24"
          - "192.168.10.0/24"

        # Portal
        portal_title: "SSL VPN Access"
        portal_message: "Enter credentials to access network"

        # DNS
        dns_servers:
          - "192.168.1.1"

        # Users
        users:
          - username: "sslvpn1"
            password: "ssl-password"
            groups: ["VPN-Users"]
```

---

## Firebox Security Services

UTM and security service configuration.

```yaml
watchguard:
  firebox:
    security_services:
      # Gateway AntiVirus
      gateway_antivirus:
        enabled: true
        scan_http: true
        scan_https: true
        scan_ftp: true
        scan_smtp: true
        scan_pop3: true
        scan_imap: true

        # Actions
        block_virus: true
        block_infected_archive: true

        # Notifications
        notify_admin: true

      # Intrusion Prevention Service (IPS)
      intrusion_prevention:
        enabled: true
        mode: "prevention"  # detection, prevention

        # Signature categories
        categories:
          - "connectivity"
          - "dos"
          - "exploit"
          - "inappropriate"
          - "malware"
          - "policy"
          - "reconnaissance"
          - "sql"
          - "web"

        # Custom rules
        custom_signatures:
          - signature_id: 2100498
            action: "drop"
          - signature_id: 2103461
            action: "allow"

      # APT Blocker
      apt_blocker:
        enabled: true
        sensitivity: "medium"  # low, medium, high
        scan_https: true

      # Reputation Enabled Defense (RED)
      reputation:
        enabled: true
        threat_level: "moderate"  # low, moderate, high

        # Custom whitelist
        whitelist:
          - "trusted.example.com"
          - "192.168.1.100"

      # WebBlocker
      webfilter:
        enabled: true

        # Categories to block
        blocked_categories:
          - "Adult/Mature Content"
          - "Criminal Activity"
          - "Gambling"
          - "Illegal Drugs"
          - "Malware Sites"
          - "Phishing"
          - "Spam URLs"
          - "Spyware"

        # Categories to warn
        warn_categories:
          - "Entertainment"
          - "Social Networking"
          - "Streaming Media"

        # Safe search
        safe_search_enforcement: true

        # HTTPS scanning
        https_scanning: true

        # Custom exceptions
        whitelist:
          - "trusted-site.com"
        blacklist:
          - "blocked-site.com"

      # spamBlocker
      spamblocker:
        enabled: false
        threshold: 5  # 1-10
        tag_subject: true
        quarantine: false

      # Data Loss Prevention (DLP)
      dlp:
        enabled: false
        rules:
          - name: "Credit-Card-Detection"
            enabled: true
            pattern: "credit_card"
            action: "block"
            log: true
            notify: true

      # Application Control
      application_control:
        enabled: true
        blocked_applications:
          - "BitTorrent"
          - "Skype"
        limited_applications:
          - application: "YouTube"
            bandwidth_limit: 5000  # kbps
```

---

## Firebox High Availability

High availability cluster configuration.

```yaml
watchguard:
  firebox:
    high_availability:
      enabled: true
      mode: "active-passive"  # active-passive, active-active

      # Cluster settings
      cluster_id: 1
      shared_key: "ha-cluster-key"

      # Primary (this device)
      primary:
        priority: 100

      # Interfaces
      heartbeat:
        primary_interface: "0"  # Interface number
        secondary_interface: "1"
        interval: 500  # milliseconds

      # Virtual IP addresses
      virtual_ips:
        - interface: "External"
          ip: "203.0.113.12"
          netmask: "255.255.255.252"

        - interface: "Trusted"
          ip: "192.168.1.1"
          netmask: "255.255.255.0"

      # Failover
      failover:
        auto_failback: false
        failback_delay: 60

        # Monitoring
        monitor_interfaces:
          - "External"
          - "Trusted"

        # Link monitoring
        link_monitor:
          enabled: true
          interval: 5
          threshold: 3

      # State synchronization
      state_sync:
        enabled: true
        connection_sync: true
        dhcp_sync: true

      # Management
      management_sync: true
```

---

## Firebox Traffic Management

QoS and traffic shaping configuration.

```yaml
watchguard:
  firebox:
    traffic_management:
      # QoS enabled globally
      enabled: true

      # Interface bandwidth limits
      interfaces:
        - interface: "External"
          upload_bandwidth: 50000  # kbps
          download_bandwidth: 200000

      # Traffic classes
      classes:
        - name: "Critical"
          priority: 1
          guaranteed_bandwidth: 20  # percentage
          maximum_bandwidth: 100

        - name: "High"
          priority: 2
          guaranteed_bandwidth: 30
          maximum_bandwidth: 80

        - name: "Medium"
          priority: 3
          guaranteed_bandwidth: 20
          maximum_bandwidth: 60

        - name: "Low"
          priority: 4
          guaranteed_bandwidth: 10
          maximum_bandwidth: 40

        - name: "Bulk"
          priority: 5
          guaranteed_bandwidth: 5
          maximum_bandwidth: 20

      # Classification rules
      rules:
        - name: "VoIP-Critical"
          enabled: true
          match:
            protocol: "udp"
            port: "5060-5061"
          class: "Critical"

        - name: "Video-Conferencing"
          enabled: true
          match:
            applications:
              - "Zoom"
              - "Teams"
              - "Webex"
          class: "High"

        - name: "Business-Apps"
          enabled: true
          match:
            applications:
              - "Office365"
              - "Salesforce"
          class: "High"

        - name: "File-Transfer"
          enabled: true
          match:
            applications:
              - "Dropbox"
              - "Google Drive"
          class: "Medium"

        - name: "Streaming"
          enabled: true
          match:
            applications:
              - "Netflix"
              - "YouTube"
          class: "Low"

        - name: "P2P"
          enabled: true
          match:
            applications:
              - "BitTorrent"
          class: "Bulk"

      # Per-policy QoS (handled in policy config)
```

---

## Firebox Authentication

User authentication and directory services.

```yaml
watchguard:
  firebox:
    authentication:
      # Local users
      local_users:
        - username: "admin"
          password: "admin-password"
          role: "admin"
          description: "Administrator account"

        - username: "user1"
          password: "user-password"
          role: "user"
          description: "Standard user"

      # Authentication servers
      servers:
        # RADIUS
        - name: "RADIUS-Primary"
          type: "radius"
          enabled: true
          server: "192.168.1.100"
          port: 1812
          shared_secret: "radius-secret"
          timeout: 5
          retries: 3

        # LDAP
        - name: "ActiveDirectory"
          type: "ldap"
          enabled: true
          server: "192.168.1.50"
          port: 389
          use_ssl: false
          base_dn: "dc=example,dc=com"
          bind_dn: "cn=admin,dc=example,dc=com"
          bind_password: "ldap-password"
          user_search_filter: "(sAMAccountName=%s)"
          group_search_filter: "(member=%s)"

        # Active Directory (Firebox-DB)
        - name: "AD-Firebox-DB"
          type: "firebox_db"
          enabled: true
          domain: "EXAMPLE"
          domain_controller: "192.168.1.50"
          ssl_enabled: true
          query_interval: 300

        # TACACS+
        - name: "TACACS-Server"
          type: "tacacs"
          enabled: false
          server: "192.168.1.60"
          port: 49
          shared_secret: "tacacs-secret"

      # Authentication settings
      settings:
        # Single sign-on
        sso:
          enabled: true
          terminal_services_aware: true
          idle_timeout: 3600

        # Firebox authentication
        firebox_auth:
          idle_timeout: 1800
          absolute_timeout: 86400

        # Web authentication
        web_auth:
          enabled: true
          port: 4100
          ssl_port: 4443
```

---

## Firebox Logging

Logging and reporting configuration.

```yaml
watchguard:
  firebox:
    logging:
      # Local logging
      local:
        enabled: true
        max_size: 1024  # MB
        rotate: true

      # Log server
      log_server:
        enabled: true
        primary:
          host: "192.168.1.101"
          port: 514
          protocol: "tcp"  # tcp, udp
          format: "welf"  # welf, cef

        secondary:
          host: "192.168.1.102"
          port: 514
          protocol: "tcp"

      # WatchGuard Cloud
      cloud_logging:
        enabled: true

      # Log types
      log_types:
        - type: "traffic"
          enabled: true
          level: "send"  # none, send, send-recv

        - type: "security"
          enabled: true
          level: "all"

        - type: "event"
          enabled: true
          level: "all"

        - type: "alarm"
          enabled: true

        - type: "debug"
          enabled: false

      # Syslog integration
      syslog:
        enabled: true
        facility: "local0"
        include_hostname: true

      # Email alerts
      email_alerts:
        - alert_type: "critical"
          enabled: true
          recipients:
            - "admin@example.com"

        - alert_type: "high"
          enabled: true
          recipients:
            - "admin@example.com"
            - "security@example.com"

        - alert_type: "medium"
          enabled: false

      # SNMP traps
      snmp_traps:
        enabled: true
        destinations:
          - "192.168.1.100"
```

---

# WatchGuard AP Configuration

## WatchGuard AP Configuration

WatchGuard AP system configuration (managed through WatchGuard Cloud or controller).

```yaml
watchguard:
  access_points:
    - name: "AP-Office-1"
      mac: "00:00:00:00:00:01"
      model: "AP325"

      # Location
      location: "Office Floor 1"
      latitude: 40.7128
      longitude: -74.0060

      # Management
      cloud_managed: true

      # LED
      led_enabled: true

      # Channel management
      auto_channel: true
      auto_power: true
```

---

## WatchGuard Wireless Networks

SSID/wireless network configuration.

```yaml
watchguard:
  wireless_networks:
    # Corporate SSID
    - name: "Corporate-WiFi"
      ssid: "CompanyWiFi"
      enabled: true

      # Security
      security_mode: "wpa2-enterprise"  # open, wpa2-psk, wpa2-enterprise, wpa3
      encryption: "aes"

      # For PSK mode:
      # security_mode: "wpa2-psk"
      # passphrase: "SecurePassword123"

      # For Enterprise mode:
      radius_servers:
        - server: "192.168.1.100"
          port: 1812
          shared_secret: "radius-secret"
          accounting_port: 1813

      # VLAN
      vlan_id: 1
      vlan_tagging: false

      # Band
      band: "dual"  # 2.4ghz, 5ghz, dual

      # Broadcasting
      broadcast_ssid: true

      # Client limits
      max_clients: 100

      # Fast roaming
      fast_roaming: true

    # Guest SSID
    - name: "Guest-WiFi"
      ssid: "Guest"
      enabled: true

      security_mode: "wpa2-psk"
      passphrase: "GuestPassword456"
      encryption: "aes"

      # Guest settings
      is_guest: true
      guest_access: true
      captive_portal:
        enabled: true
        portal_type: "click-through"  # click-through, password, voucher
        redirect_url: ""
        session_timeout: 480  # minutes

      # Isolation
      client_isolation: true

      vlan_id: 20
      vlan_tagging: true

      band: "dual"
      broadcast_ssid: true
      max_clients: 50

    # WPA3 SSID
    - name: "Secure-WiFi"
      ssid: "SecureNet"
      enabled: true

      security_mode: "wpa3-psk"
      passphrase: "WPA3SecurePass!"
      encryption: "aes"

      # WPA3 specific
      sae_enabled: true
      pmf_required: true

      vlan_id: 1
      band: "5ghz"
      broadcast_ssid: true
```

---

## WatchGuard Radio Settings

Radio configuration for 2.4GHz and 5GHz.

```yaml
watchguard:
  access_points:
    - name: "AP-Office-1"
      mac: "00:00:00:00:00:01"

      # 2.4GHz radio
      radio_2ghz:
        enabled: true
        channel: "auto"  # auto, or 1-11
        channel_width: "20"  # 20, 40
        tx_power: "auto"  # auto, or specific dBm
        min_bitrate: "12"  # Mbps

      # 5GHz radio
      radio_5ghz:
        enabled: true
        channel: "auto"  # auto, or specific channel
        channel_width: "80"  # 20, 40, 80, 160
        tx_power: "auto"
        min_bitrate: "24"
        dfs_enabled: true

      # Advanced
      beamforming: true
      airtime_fairness: true
      band_steering: true
```

---

## WatchGuard Guest Access

Guest portal and access configuration.

```yaml
watchguard:
  guest_access:
    # Portal customization
    portal:
      title: "Welcome to Guest WiFi"
      logo_url: "https://example.com/logo.png"
      background_color: "#ffffff"
      text_color: "#000000"

      # Terms and conditions
      terms_enabled: true
      terms_text: "By accessing this network, you agree to..."

    # Authentication methods
    authentication:
      - type: "click-through"
        enabled: true

      - type: "password"
        enabled: true
        password: "GuestAccess2024"

      - type: "voucher"
        enabled: true

      - type: "social"
        enabled: false
        providers:
          - "facebook"
          - "google"

    # Session settings
    session:
      timeout: 480  # minutes
      idle_timeout: 30
      bandwidth_limit: 5000  # kbps

    # Vouchers
    vouchers:
      - code: "GUEST2024"
        duration: 480
        bandwidth_limit: 0
        uses: 100
        valid_from: "2024-01-01"
        valid_until: "2024-12-31"
```

---

# WatchGuard Switch Configuration

## WatchGuard Switch Configuration

Basic switch configuration (if applicable for WatchGuard managed switches).

```yaml
watchguard:
  switches:
    - name: "Switch-Main"
      mac: "00:00:00:00:00:02"
      model: "WGS-804-POE"

      # Global settings
      stp:
        enabled: true
        mode: "rstp"  # stp, rstp, mstp
        priority: 32768

      # IGMP snooping
      igmp_snooping: true

      # Jumbo frames
      jumbo_frames: false
```

---

## WatchGuard Port Configuration

Switch port configuration.

```yaml
watchguard:
  switches:
    - name: "Switch-Main"
      mac: "00:00:00:00:00:02"

      ports:
        # Uplink port
        - port: 1
          name: "Uplink-to-Firebox"
          enabled: true
          mode: "trunk"
          native_vlan: 1
          allowed_vlans: "1,10,20,30"
          speed: "auto"
          duplex: "auto"
          poe: false

        # Access port
        - port: 2
          name: "Workstation-1"
          enabled: true
          mode: "access"
          vlan: 1
          speed: "auto"
          duplex: "auto"
          poe: false

        # PoE port
        - port: 5
          name: "AP-1"
          enabled: true
          mode: "access"
          vlan: 1
          poe: true
          poe_priority: "high"
          poe_limit: 30  # watts

        # Guest port
        - port: 10
          name: "Guest-Port"
          enabled: true
          mode: "access"
          vlan: 20
          speed: "auto"
          duplex: "auto"
          poe: false

        # Disabled port
        - port: 24
          name: "Unused"
          enabled: false
```

---

## WatchGuard Switch VLANs

VLAN configuration for switches.

```yaml
watchguard:
  switches:
    - name: "Switch-Main"
      mac: "00:00:00:00:00:02"

      vlans:
        - vlan_id: 1
          name: "Default"
          description: "Default VLAN"

        - vlan_id: 10
          name: "Management"
          description: "Management network"

        - vlan_id: 20
          name: "Guest"
          description: "Guest WiFi"

        - vlan_id: 30
          name: "IoT"
          description: "IoT devices"
```

---

## Complete WatchGuard Example Configuration

Here's a complete example for a small office with Firebox, APs, and switch:

```yaml
# Complete WatchGuard Configuration Example
# Small office with Firebox M370, WatchGuard APs, and managed switch

watchguard:
  firebox:
    system:
      device_name: "FBX-Office"
      location: "Main Office"
      timezone: "America/New_York"

    interfaces:
      - name: "External"
        type: "external"
        mode: "dhcp"
        enabled: true

      - name: "Trusted"
        type: "trusted"
        mode: "static"
        ip: "192.168.1.1"
        netmask: "255.255.255.0"
        enabled: true

    vlans:
      - vlan_id: 20
        name: "Guest"
        parent_interface: "Trusted"
        ip: "192.168.20.1"
        netmask: "255.255.255.0"
        enabled: true

    dhcp_servers:
      - interface: "Trusted"
        enabled: true
        start_ip: "192.168.1.100"
        end_ip: "192.168.1.200"
        gateway: "192.168.1.1"
        dns_servers:
          - "192.168.1.1"
          - "1.1.1.1"

      - interface: "VLAN-Guest"
        enabled: true
        start_ip: "192.168.20.50"
        end_ip: "192.168.20.200"
        gateway: "192.168.20.1"
        dns_servers:
          - "192.168.20.1"

    policies:
      - name: "Outgoing"
        enabled: true
        policy_type: "outgoing"
        from: ["Trusted"]
        to: ["External"]
        source: ["TrustedNetwork"]
        destination: ["Any-External"]
        services: ["HTTP", "HTTPS", "DNS"]
        action: "allow"
        nat: true
        security_services:
          gateway_antivirus: true
          intrusion_prevention: true

      - name: "Block-Guest-to-LAN"
        enabled: true
        policy_type: "custom"
        from: ["VLAN-Guest"]
        to: ["Trusted"]
        source: ["GuestNetwork"]
        destination: ["TrustedNetwork"]
        services: ["Any"]
        action: "deny"

  wireless_networks:
    - name: "Office-WiFi"
      ssid: "OfficeWiFi"
      enabled: true
      security_mode: "wpa2-psk"
      passphrase: "SecurePassword123"
      vlan_id: 1
      band: "dual"

    - name: "Guest-WiFi"
      ssid: "Guest"
      enabled: true
      security_mode: "wpa2-psk"
      passphrase: "GuestPass456"
      is_guest: true
      captive_portal:
        enabled: true
        portal_type: "click-through"
      vlan_id: 20
      client_isolation: true

  access_points:
    - name: "AP-Office-1"
      mac: "00:00:00:00:00:01"
      location: "Reception"
      radio_2ghz:
        enabled: true
        channel: "auto"
        tx_power: "auto"
      radio_5ghz:
        enabled: true
        channel: "auto"
        tx_power: "auto"
```

---

## Notes and Best Practices

### WatchGuard Firebox Best Practices

1. **Security Services**: Always enable Gateway AV, IPS, and APT Blocker for internet traffic
2. **Policies**: Use specific policies instead of "Any" when possible
3. **Logging**: Configure log server for centralized logging and reporting
4. **Updates**: Keep Fireware OS and security signatures up to date
5. **VPN**: Use IKEv2 for BOVPN when possible for better performance
6. **HA**: Use dedicated interfaces for heartbeat in HA configurations
7. **Backup**: Regular configuration backups to WatchGuard Cloud

### WatchGuard AP Best Practices

1. **Cloud Management**: Use WatchGuard Cloud for centralized AP management
2. **Channel Planning**: Enable auto-channel for optimal performance
3. **Band Steering**: Enable to prefer 5GHz for dual-band clients
4. **Guest Networks**: Always isolate guest traffic from corporate
5. **Fast Roaming**: Enable for seamless transitions between APs

### Configuration Management

1. **Policy Manager**: Primary tool for Firebox configuration
2. **XML Export**: Configuration can be exported as XML for automation
3. **Templates**: Create policy templates for consistent deployments
4. **Change Control**: Document all configuration changes
5. **Testing**: Test policies in log-only mode before enforcing

### Security Considerations

1. **Default Deny**: Block all traffic by default, explicitly allow needed traffic
2. **Least Privilege**: Grant minimum required access
3. **Inter-VLAN**: Control traffic between VLANs with custom policies
4. **HTTPS Inspection**: Enable for deep content inspection
5. **Application Control**: Block unwanted applications
6. **Geo-Blocking**: Use Reputation Enabled Defense

### Performance Optimization

1. **Policy Order**: Place most-used policies at the top
2. **Security Services**: Balance security with performance needs
3. **QoS**: Configure traffic management for critical applications
4. **Connection Limits**: Set appropriate limits to prevent resource exhaustion
5. **Logging**: Log only what you need to review

---

## Schema Version

Schema Version: 1.0.0
Last Updated: 2024-10-27
Compatible with: Fireware OS 12.x, WatchGuard Cloud
