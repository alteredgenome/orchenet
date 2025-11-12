# OrcheNet Configuration Schema - Fortinet

This document defines the complete YAML configuration schema for managing Fortinet devices through OrcheNet. This includes FortiGate firewalls, FortiSwitch switches, FortiAP access points, and FortiExtender cellular extenders.

## Fortinet Configuration Overview

Fortinet devices use FortiOS/FortiSwitchOS configuration system. OrcheNet translates vendor-agnostic YAML into FortiOS CLI commands.

---

## Table of Contents

### FortiGate
- [System Configuration](#fortigate-system-configuration)
- [Interfaces](#fortigate-interfaces)
- [Zones](#fortigate-zones)
- [DHCP Server](#fortigate-dhcp-server)
- [DNS](#fortigate-dns)
- [Routing](#fortigate-routing)
- [Firewall Policies](#fortigate-firewall-policies)
- [Firewall Objects](#fortigate-firewall-objects)
- [VPN](#fortigate-vpn)
- [SD-WAN](#fortigate-sd-wan)
- [User Authentication](#fortigate-user-authentication)
- [Security Profiles](#fortigate-security-profiles)
- [High Availability](#fortigate-high-availability)
- [Logging](#fortigate-logging)

### FortiSwitch
- [Switch System](#fortiswitch-system)
- [Switch Ports](#fortiswitch-ports)
- [VLANs](#fortiswitch-vlans)
- [Link Aggregation](#fortiswitch-link-aggregation)
- [Storm Control](#fortiswitch-storm-control)
- [Port Security](#fortiswitch-port-security)
- [QoS](#fortiswitch-qos)

### FortiAP
- [AP System](#fortiap-system)
- [Wireless Profiles](#fortiap-wireless-profiles)
- [SSIDs](#fortiap-ssids)
- [Radio Settings](#fortiap-radio-settings)

### FortiExtender
- [Extender Configuration](#fortiextender-configuration)
- [Modem Settings](#fortiextender-modem-settings)

---

# FortiGate Configuration

## FortiGate System Configuration

Global system settings for FortiGate firewalls.

```yaml
fortigate:
  system:
    global:
      hostname: "FGT-HQ-01"
      alias: "Headquarters Firewall"
      timezone: "04"  # GMT-4
      admin_sport: 443
      admin_ssh_port: 22
      admin_scp: enable
      admintimeout: 30

      # GUI settings
      gui_theme: "mariner"
      gui_date_format: "yyyy/MM/dd"

      # System behavior
      revision_backup_on_logout: enable
      revision_backup_on_upgrade: enable

    # Admin accounts
    admin:
      - name: "admin"
        password: "your-secure-password"
        trusthost1: "192.168.1.0/24"
        trusthost2: "10.0.0.0/8"
        accprofile: "super_admin"
        vdom: "root"

      - name: "readonly"
        password: "readonly-password"
        trusthost1: "192.168.1.0/24"
        accprofile: "prof_admin"
        vdom: "root"

    # Access profiles
    accprofile:
      - name: "custom_admin"
        secfabgrp: read-write
        ftviewgrp: read-write
        authgrp: read-write
        sysgrp: read-write
        netgrp: read-write
        loggrp: read-write
        fwgrp: read-write
        vpngrp: read-write

    # SNMP
    snmp:
      community:
        - id: 1
          name: "public"
          events:
            - cpu-high
            - mem-low
            - log-full
          hosts:
            - ip: "192.168.1.100/32"
              interface: "port1"

      sysinfo:
        status: enable
        contact_info: "admin@example.com"
        location: "Datacenter A"

    # NTP
    ntp:
      ntpserver:
        - server: "pool.ntp.org"
          ntpv3: enable
          authentication: disable
        - server: "time.google.com"
          ntpv3: enable
      ntpsync: enable
      type: fortiguard
      syncinterval: 60
```

---

## FortiGate Interfaces

Interface configuration including physical, VLAN, and aggregate interfaces.

```yaml
fortigate:
  system:
    interface:
      # Physical interface
      - name: "port1"
        vdom: "root"
        mode: static
        ip: "203.0.113.10/30"
        allowaccess: "ping https ssh"
        type: physical
        alias: "WAN"
        role: wan
        snmp_index: 1
        description: "Primary WAN"

      - name: "port2"
        vdom: "root"
        mode: static
        ip: "192.168.1.1/24"
        allowaccess: "ping https ssh snmp"
        type: physical
        alias: "LAN"
        role: lan
        device_identification: enable
        dhcp_relay_service: disable

      # VLAN interface
      - name: "vlan10"
        vdom: "root"
        type: vlan
        vlanid: 10
        interface: "port2"
        mode: static
        ip: "192.168.10.1/24"
        allowaccess: "ping https"
        alias: "Management VLAN"
        role: lan

      # Aggregate interface (LAG)
      - name: "aggregate1"
        vdom: "root"
        type: aggregate
        member:
          - interface_name: "port3"
          - interface_name: "port4"
        mode: static
        ip: "192.168.100.1/24"
        allowaccess: "ping"
        alias: "Server Network"
        lacp_mode: active
        lacp_speed: slow

      # Loopback
      - name: "loopback0"
        vdom: "root"
        type: loopback
        mode: static
        ip: "1.1.1.1/32"
        allowaccess: ""

      # Tunnel interface
      - name: "tunnel1"
        vdom: "root"
        type: tunnel
        mode: static
        ip: "10.10.10.1/30"
        allowaccess: "ping"
        remote_ip: "10.10.10.2"
        interface: "port1"

      # Software switch (deprecated but still used)
      - name: "lan"
        vdom: "root"
        type: switch
        member:
          - interface_name: "port5"
          - interface_name: "port6"
          - interface_name: "port7"
        mode: static
        ip: "192.168.2.1/24"
        allowaccess: "ping https"
```

---

## FortiGate Zones

Security zones for grouping interfaces.

```yaml
fortigate:
  system:
    zone:
      - name: "wan_zone"
        interface:
          - interface_name: "port1"
          - interface_name: "port8"
        description: "WAN interfaces"

      - name: "lan_zone"
        interface:
          - interface_name: "port2"
          - interface_name: "aggregate1"
        description: "LAN interfaces"

      - name: "dmz_zone"
        interface:
          - interface_name: "port9"
        description: "DMZ"
```

---

## FortiGate DHCP Server

DHCP server configuration.

```yaml
fortigate:
  system:
    dhcp:
      server:
        - id: 1
          interface: "port2"
          status: enable
          dns_service: local
          dns_server1: "192.168.1.1"
          dns_server2: "1.1.1.1"
          default_gateway: "192.168.1.1"
          netmask: "255.255.255.0"
          lease_time: 86400

          # IP range
          ip_range:
            - id: 1
              start_ip: "192.168.1.100"
              end_ip: "192.168.1.200"

          # DHCP options
          options:
            - id: 1
              code: 66  # TFTP server
              type: string
              value: "192.168.1.10"
            - id: 2
              code: 150  # TFTP server list
              type: ip
              value: "192.168.1.10 192.168.1.11"

          # Reserved addresses
          reserved_address:
            - id: 1
              ip: "192.168.1.50"
              mac: "00:11:22:33:44:55"
              description: "Server 1"

        - id: 2
          interface: "vlan10"
          status: enable
          dns_service: local
          dns_server1: "192.168.10.1"
          default_gateway: "192.168.10.1"
          netmask: "255.255.255.0"
          lease_time: 43200
          ip_range:
            - id: 1
              start_ip: "192.168.10.50"
              end_ip: "192.168.10.100"
```

---

## FortiGate DNS

DNS configuration including database and server settings.

```yaml
fortigate:
  system:
    dns:
      primary: "1.1.1.1"
      secondary: "8.8.8.8"
      protocol: "cleartext"  # cleartext, dot, doh
      ssl_certificate: ""
      server_hostname: []

    # DNS database for local resolution
    dns_database:
      - name: "local-dns"
        domain: "local.lan"
        type: master
        view: shadow
        ip_master: "0.0.0.0"
        primary_name: "ns1.local.lan"
        contact: "admin.local.lan"
        ttl: 86400
        authoritative: enable

        # DNS entries
        dns_entry:
          - id: 1
            hostname: "server1"
            ip: "192.168.1.100"
            canonical_name: ""
            type: A
            ttl: 300

          - id: 2
            hostname: "mail"
            preference: 10
            canonical_name: "server1.local.lan"
            type: MX
            ttl: 300
```

---

## FortiGate Routing

Static and dynamic routing configuration.

```yaml
fortigate:
  router:
    static:
      - seq_num: 1
        dst: "0.0.0.0/0"
        gateway: "203.0.113.9"
        device: "port1"
        distance: 10
        weight: 0
        priority: 0
        comment: "Default route to ISP"

      - seq_num: 2
        dst: "10.0.0.0/8"
        gateway: "192.168.1.254"
        device: "port2"
        distance: 10
        comment: "Internal network route"

      - seq_num: 3
        dst: "192.168.100.0/24"
        blackhole: enable
        distance: 254
        comment: "Blackhole unused subnet"

    # Policy-based routing
    policy:
      - seq_num: 1
        input_device:
          - name: "port2"
        src: "192.168.1.0/24"
        dst: "0.0.0.0/0"
        protocol: 0
        gateway: "203.0.113.9"
        output_device: "port1"
        comments: "Route LAN to primary WAN"

    # OSPF
    ospf:
      router_id: "1.1.1.1"
      distance_external: 110
      distance_inter_area: 110
      distance_intra_area: 110

      area:
        - id: "0.0.0.0"
          type: regular
          default_cost: 10
          authentication: none

      network:
        - id: 1
          prefix: "192.168.1.0/24"
          area: "0.0.0.0"
        - id: 2
          prefix: "192.168.10.0/24"
          area: "0.0.0.0"

      interface:
        - name: "port2"
          cost: 10
          priority: 1
          dead_interval: 40
          hello_interval: 10
          authentication: none

    # BGP
    bgp:
      as: 65001
      router_id: "1.1.1.1"
      keepalive_timer: 60
      holdtime_timer: 180

      neighbor:
        - ip: "203.0.113.9"
          remote_as: 65000
          ebgp_enforce_multihop: disable
          soft_reconfiguration: enable
          route_map_in: "bgp-in"
          route_map_out: "bgp-out"

      network:
        - id: 1
          prefix: "192.168.0.0/16"

      redistribute:
        - name: "connected"
          status: enable
        - name: "static"
          status: enable
          route_map: "static-to-bgp"
```

---

## FortiGate Firewall Policies

Security policies for traffic control.

```yaml
fortigate:
  firewall:
    policy:
      # Outbound internet access
      - policyid: 1
        name: "LAN_to_Internet"
        srcintf:
          - name: "port2"
        dstintf:
          - name: "port1"
        srcaddr:
          - name: "LAN_subnet"
        dstaddr:
          - name: "all"
        action: accept
        schedule: "always"
        service:
          - name: "HTTP"
          - name: "HTTPS"
          - name: "DNS"
        nat: enable
        ippool: disable
        logtraffic: all
        comments: "Allow LAN to Internet"

        # Security profiles
        av_profile: "default"
        webfilter_profile: "default"
        ips_sensor: "default"
        application_list: "default"
        ssl_ssh_profile: "certificate-inspection"

      # Inbound port forwarding
      - policyid: 2
        name: "WAN_to_WebServer"
        srcintf:
          - name: "port1"
        dstintf:
          - name: "port2"
        srcaddr:
          - name: "all"
        dstaddr:
          - name: "VIP_WebServer"
        action: accept
        schedule: "always"
        service:
          - name: "HTTP"
          - name: "HTTPS"
        nat: disable
        logtraffic: all
        comments: "Inbound to web server"

        # Security profiles for inbound
        av_profile: "default"
        webfilter_profile: "strict"
        ips_sensor: "protect_http_server"

      # Block specific traffic
      - policyid: 3
        name: "Block_P2P"
        srcintf:
          - name: "port2"
        dstintf:
          - name: "port1"
        srcaddr:
          - name: "all"
        dstaddr:
          - name: "all"
        action: deny
        schedule: "always"
        service:
          - name: "ALL"
        application_list: "block-p2p"
        logtraffic: all
        comments: "Block P2P applications"

      # VPN access
      - policyid: 4
        name: "VPN_to_LAN"
        srcintf:
          - name: "tunnel1"
        dstintf:
          - name: "port2"
        srcaddr:
          - name: "VPN_subnet"
        dstaddr:
          - name: "LAN_subnet"
        action: accept
        schedule: "always"
        service:
          - name: "ALL"
        logtraffic: all
        comments: "VPN users to LAN"

      # SD-WAN policy
      - policyid: 5
        name: "SDWAN_Policy"
        srcintf:
          - name: "port2"
        dstintf:
          - name: "virtual-wan-link"
        srcaddr:
          - name: "all"
        dstaddr:
          - name: "all"
        action: accept
        schedule: "always"
        service:
          - name: "ALL"
        nat: enable
        logtraffic: utm
        comments: "SD-WAN outbound"
```

---

## FortiGate Firewall Objects

Reusable objects for policies.

```yaml
fortigate:
  firewall:
    # Address objects
    address:
      - name: "LAN_subnet"
        type: subnet
        subnet: "192.168.1.0/24"
        comment: "Main LAN network"

      - name: "Server1"
        type: ipmask
        subnet: "192.168.1.100/32"
        comment: "Application server"

      - name: "FQDN_Example"
        type: fqdn
        fqdn: "www.example.com"
        comment: "External service"

      - name: "IP_Range"
        type: iprange
        start_ip: "192.168.1.150"
        end_ip: "192.168.1.160"
        comment: "Guest IP range"

      - name: "Geo_US"
        type: geography
        country: "US"
        comment: "United States"

    # Address groups
    addrgrp:
      - name: "Internal_Networks"
        member:
          - name: "LAN_subnet"
          - name: "Server1"
        comment: "All internal networks"

      - name: "Servers"
        member:
          - name: "Server1"
        comment: "Server group"

    # Virtual IPs (NAT/port forwarding)
    vip:
      - name: "VIP_WebServer"
        type: static-nat
        extip: "203.0.113.10"
        extintf: "port1"
        mappedip:
          - range: "192.168.1.100-192.168.1.100"
        comment: "Web server NAT"

      - name: "VIP_PortForward"
        type: static-nat
        extip: "203.0.113.10"
        extintf: "port1"
        mappedip:
          - range: "192.168.1.50"
        portforward: enable
        protocol: tcp
        extport: "8080"
        mappedport: "80"
        comment: "Port forwarding 8080 to 80"

    # Service objects
    service:
      custom:
        - name: "Custom_App"
          protocol: TCP/UDP/SCTP
          tcp_portrange: "8000-8100"
          udp_portrange: "8000-8100"
          comment: "Custom application ports"

        - name: "HTTPS_Alt"
          protocol: TCP/UDP/SCTP
          tcp_portrange: "8443"
          comment: "Alternative HTTPS"

    # Service groups
    service:
      group:
        - name: "Web_Services"
          member:
            - name: "HTTP"
            - name: "HTTPS"
          comment: "Standard web services"

    # Schedules
    schedule:
      recurring:
        - name: "Business_Hours"
          day: monday tuesday wednesday thursday friday
          start: "08:00"
          end: "18:00"

        - name: "Weekend"
          day: saturday sunday
          start: "00:00"
          end: "23:59"

      onetime:
        - name: "Maintenance_Window"
          start: "2024-12-01 02:00"
          end: "2024-12-01 06:00"

    # Internet Service
    internet_service_custom:
      - name: "Office365"
        entry:
          - id: 1
            protocol: 6  # TCP
            dst:
              - name: "O365_subnet1"
            port_range:
              - id: 1
                start_port: 443
                end_port: 443
```

---

## FortiGate VPN

VPN configuration for IPsec, SSL-VPN, and L2TP.

### IPsec VPN

```yaml
fortigate:
  vpn:
    ipsec:
      # Phase 1 (IKE)
      phase1_interface:
        - name: "site_to_site_vpn"
          type: static
          interface: "port1"
          ike_version: 2
          peertype: any
          net_device: disable
          mode_cfg: disable
          proposal: "aes256-sha256 aes256-sha1"
          dhgrp: "14 5"

          # Authentication
          authmethod: psk
          psksecret: "your-pre-shared-key"

          # Remote gateway
          remote_gw: "198.51.100.10"

          # DPD
          dpd: on-demand
          dpd_retrycount: 3
          dpd_retryinterval: 5

          # Additional settings
          nattraversal: enable
          fragmentation: enable
          keepalive: 10
          auto_negotiate: enable

        - name: "dialup_vpn"
          type: dynamic
          interface: "port1"
          ike_version: 2
          peertype: any
          mode_cfg: enable
          proposal: "aes256-sha256"
          dhgrp: "14"
          authmethod: psk
          psksecret: "dialup-psk"
          ipv4_start_ip: "10.10.10.10"
          ipv4_end_ip: "10.10.10.100"
          ipv4_netmask: "255.255.255.0"
          dns_mode: auto

      # Phase 2 (IPsec)
      phase2_interface:
        - name: "site_to_site_vpn_p2"
          phase1name: "site_to_site_vpn"
          proposal: "aes256-sha256 aes256-sha1"
          pfs: enable
          dhgrp: "14 5"

          # Traffic selectors
          src_subnet: "192.168.1.0/24"
          dst_subnet: "192.168.2.0/24"

          # Lifetime
          keylifeseconds: 28800
          auto_negotiate: enable

        - name: "dialup_vpn_p2"
          phase1name: "dialup_vpn"
          proposal: "aes256-sha256"
          pfs: enable
          dhgrp: "14"
          src_subnet: "0.0.0.0/0"
          dst_subnet: "0.0.0.0/0"

    # SSL-VPN
    ssl_vpn:
      settings:
        port: 10443
        source_interface:
          - name: "port1"
        source_address:
          - name: "all"
        default_portal: "full-access"

        # Authentication
        auth_timeout: 28800
        login_attempt_limit: 3
        login_block_time: 60

        # Tunnel settings
        tunnel_ip_pools:
          - name: "SSLVPN_TUNNEL_ADDR1"
        dns_server1: "192.168.1.1"
        dns_server2: "1.1.1.1"

      # Portal configuration
      settings:
        portal:
          - name: "full-access"
            tunnel_mode: enable
            web_mode: enable
            ip_pools:
              - name: "SSLVPN_TUNNEL_ADDR1"
            split_tunneling: enable
            split_tunneling_routing_address:
              - name: "Internal_Networks"
```

---

## FortiGate SD-WAN

SD-WAN configuration for intelligent path selection.

```yaml
fortigate:
  system:
    sdwan:
      status: enable

      # WAN members
      members:
        - seq_num: 1
          interface: "port1"
          gateway: "203.0.113.9"
          priority: 1
          weight: 100
          source: "203.0.113.10"
          cost: 0

        - seq_num: 2
          interface: "port8"
          gateway: "198.51.100.1"
          priority: 2
          weight: 50
          source: "198.51.100.10"
          cost: 0

      # Health check
      health_check:
        - name: "ISP1_Check"
          server: "8.8.8.8"
          protocol: ping
          interval: 5
          probe_timeout: 1
          failtime: 3
          recoverytime: 5
          members:
            - seq_num: 1

        - name: "ISP2_Check"
          server: "1.1.1.1"
          protocol: ping
          interval: 5
          probe_timeout: 1
          failtime: 3
          recoverytime: 5
          members:
            - seq_num: 2

      # SD-WAN zones
      zone:
        - name: "virtual-wan-link"

      # Service rules
      service:
        - id: 1
          name: "VoIP_Priority"
          mode: priority
          dst:
            - name: "all"
          protocol: 17  # UDP
          start_port: 5060
          end_port: 5061
          priority_members:
            - seq_num: 1
            - seq_num: 2
          health_check: "ISP1_Check"

        - id: 2
          name: "Web_LoadBalance"
          mode: load-balance
          dst:
            - name: "all"
          protocol: 6  # TCP
          start_port: 443
          end_port: 443
          priority_members:
            - seq_num: 1
            - seq_num: 2
          health_check: "ISP1_Check"
```

---

## FortiGate User Authentication

User and authentication configuration.

```yaml
fortigate:
  user:
    # Local users
    local:
      - name: "vpnuser1"
        status: enable
        type: password
        passwd: "user-password"
        two_factor: disable
        email_to: "user1@example.com"

      - name: "vpnuser2"
        status: enable
        type: password
        passwd: "user-password"
        two_factor: fortitoken

    # User groups
    group:
      - name: "VPN_Users"
        member:
          - name: "vpnuser1"
          - name: "vpnuser2"
        group_type: firewall

      - name: "Remote_Access"
        member:
          - name: "vpnuser1"

    # RADIUS server
    radius:
      - name: "RADIUS1"
        server: "192.168.1.100"
        secret: "radius-secret"
        auth_type: auto
        radius_port: 1812
        timeout: 5
        all_usergroup: disable

    # LDAP server
    ldap:
      - name: "ActiveDirectory"
        server: "192.168.1.50"
        cnid: "cn"
        dn: "dc=example,dc=com"
        type: simple
        username: "cn=admin,dc=example,dc=com"
        password: "ldap-password"
        secure: ldaps
        port: 636

    # TACACS+ server
    tacacs:
      - name: "TACACS1"
        server: "192.168.1.60"
        key: "tacacs-key"
        port: 49
        authen_type: auto
        authorization: enable

    # SAML
    saml:
      - name: "Azure_SAML"
        cert: "REMOTE_Cert_1"
        entity_id: "https://fortigate.example.com/remote/saml/metadata"
        single_sign_on_url: "https://fortigate.example.com/remote/saml/login"
        single_logout_url: "https://fortigate.example.com/remote/saml/logout"
        idp_entity_id: "https://sts.windows.net/tenant-id/"
        idp_single_sign_on_url: "https://login.microsoftonline.com/tenant-id/saml2"
        idp_single_logout_url: "https://login.microsoftonline.com/tenant-id/saml2"
        idp_cert: "REMOTE_Cert_2"
```

---

## FortiGate Security Profiles

UTM and security feature profiles.

```yaml
fortigate:
  # Antivirus profile
  antivirus:
    profile:
      - name: "av-strict"
        comment: "Strict AV scanning"

        http:
          options: "scan avmonitor quarantine"
          archive_block: "encrypted multipart nested"
          archive_log: "encrypted multipart nested"
          emulator: enable

        ftp:
          options: "scan avmonitor quarantine"
          archive_block: "encrypted corrupted"

        imap:
          options: "scan avmonitor quarantine"

        pop3:
          options: "scan avmonitor quarantine"

        smtp:
          options: "scan avmonitor quarantine"

  # Web filter profile
  webfilter:
    profile:
      - name: "web-filter-strict"
        comment: "Strict web filtering"

        web:
          blacklist: enable
          bword_table: 1
          bword_threshold: 10
          urlfilter_table: 1
          content_header_list: 1

        ftgd_wf:
          options: "error allow"
          filters:
            - id: 1
              category: 1  # Adult/Mature Content
              action: block
            - id: 2
              category: 26  # Malware
              action: block

        override:
          ovrd_cookie: enable
          ovrd_dur: "15m"
          profile_type: list
          profile:
            - name: "auth-portal-profile"

  # IPS sensor
  ips:
    sensor:
      - name: "protect-http-server"
        comment: "Protect HTTP servers"

        entries:
          - id: 1
            rule:
              - name: "Web.Server.Attack"
            severity:
              - critical
              - high
            status: enable
            action: block
            log: enable
            log_packet: enable

  # Application control
  application:
    list:
      - name: "block-p2p"
        comment: "Block P2P applications"

        entries:
          - id: 1
            category:
              - id: 2  # File Sharing
            action: block
            log: enable

          - id: 2
            application:
              - id: 16354  # BitTorrent
            action: block
            log: enable

  # SSL/SSH inspection
  firewall:
    ssl_ssh_profile:
      - name: "certificate-inspection"
        comment: "Deep SSL inspection"

        https:
          status: certificate-inspection
          ports: 443

        ftps:
          status: certificate-inspection
          ports: 990

        imaps:
          status: certificate-inspection
          ports: 993

        pop3s:
          status: certificate-inspection
          ports: 995

        smtps:
          status: certificate-inspection
          ports: 465

        ssh:
          status: inspect
          ports: 22

  # DLP sensor
  dlp:
    sensor:
      - name: "dlp-ccn"
        comment: "Detect credit card numbers"

        filter:
          - id: 1
            name: "Credit-Cards"
            type: file
            proto: "http-post ftp smtp"
            filter_by: credit-card
            action: block
            log: enable
```

---

## FortiGate High Availability

HA cluster configuration.

```yaml
fortigate:
  system:
    ha:
      mode: a-p  # a-p (active-passive) or a-a (active-active)
      group_id: 1
      group_name: "FGT-HA-Cluster"
      password: "ha-password"

      # Priority (higher is preferred)
      priority: 200

      # Heartbeat interfaces
      hbdev: "port10 50 port11 50"

      # Session pickup
      session_pickup: enable
      session_pickup_connectionless: enable
      session_pickup_nat: enable
      session_pickup_expectation: enable

      # HA direct
      ha_direct: enable

      # Management interface reservation
      ha_mgmt_status: enable
      ha_mgmt_interfaces:
        - id: 1
          interface: "port9"
          gateway: "192.168.99.1"

      # Monitor interfaces
      monitor:
        - port1
        - port2

      # Pingserver monitor
      pingserver_monitor_interface: "port1"
      pingserver_failover_threshold: 0
      pingserver_flip_timeout: 60

      # Unicast heartbeat
      unicast_hb: enable
      unicast_hb_peerip: "192.168.100.2"
      unicast_hb_netmask: "255.255.255.0"
```

---

## FortiGate Logging

Log configuration and forwarding.

```yaml
fortigate:
  log:
    # Syslog settings
    syslogd:
      setting:
        status: enable
        server: "192.168.1.100"
        port: 514
        mode: udp
        facility: local7
        source_ip: ""
        format: default
        priority: default
        max_log_rate: 0

      override_setting:
        status: enable
        override: enable

      filter:
        severity: information
        forward_traffic: enable
        local_traffic: enable
        multicast_traffic: enable
        sniffer_traffic: enable
        anomaly: enable
        voip: enable

    # FortiAnalyzer
    fortianalyzer:
      setting:
        status: enable
        server: "192.168.1.101"
        source_ip: ""
        upload_option: realtime
        reliable: enable
        hmac_algorithm: sha256
        enc_algorithm: high

      override_setting:
        status: enable
        override: enable

    # Memory logging
    memory:
      global_setting:
        max_size: 163840

      filter:
        severity: information
        forward_traffic: enable
        local_traffic: enable
        sniffer_traffic: enable
        anomaly: enable

    # Disk logging
    disk:
      setting:
        status: enable
        ips_archive: enable

      filter:
        severity: information
        forward_traffic: enable
        local_traffic: enable
```

---

# FortiSwitch Configuration

## FortiSwitch System

FortiSwitch basic system configuration.

```yaml
fortiswitch:
  system:
    global:
      hostname: "FSW-01"
      timezone: 04
      admin_sport: 443
      admin_scp: enable

    # Admin users
    admin:
      - name: "admin"
        password: "admin-password"
        accprofile: "super_admin"

    # SNMP
    snmp:
      community:
        - id: 1
          name: "public"
          hosts:
            - ip: "192.168.1.100/32"

      sysinfo:
        status: enable
        location: "Network Closet A"
        contact_info: "admin@example.com"

    # NTP
    ntp:
      server:
        - name: "pool.ntp.org"
      ntpsync: enable
```

---

## FortiSwitch Ports

Physical port configuration.

```yaml
fortiswitch:
  switch:
    interface:
      - name: "port1"
        description: "Uplink to FortiGate"
        mode: static
        type: physical
        allowed_vlans: "1,10,20,30"
        native_vlan: 1
        stp_state: enable
        stp_bpdu_guard: disable
        stp_root_guard: disable

      - name: "port2"
        description: "Server connection"
        mode: static
        type: physical
        allowed_vlans: "100"
        native_vlan: 100
        stp_state: enable

      - name: "port3"
        description: "Workstation - VLAN 10"
        mode: static
        type: physical
        allowed_vlans: "10"
        native_vlan: 10
        stp_state: enable

      - name: "port4"
        description: "Guest network"
        mode: static
        type: physical
        allowed_vlans: "20"
        native_vlan: 20
        stp_state: enable
        stp_bpdu_guard: enable

      # PoE settings
      - name: "port5"
        description: "IP Phone with PoE"
        mode: static
        type: physical
        allowed_vlans: "30"
        native_vlan: 30
        poe_status: enable
        poe_mode: "IEEE802.3AF"
        poe_max_power: 15.4  # watts
```

---

## FortiSwitch VLANs

VLAN configuration for FortiSwitch.

```yaml
fortiswitch:
  switch:
    vlan:
      - id: 1
        name: "default"
        description: "Default VLAN"

      - id: 10
        name: "management"
        description: "Management VLAN"

      - id: 20
        name: "guest"
        description: "Guest network"

      - id: 30
        name: "voip"
        description: "VoIP phones"

      - id: 100
        name: "servers"
        description: "Server network"
```

---

## FortiSwitch Link Aggregation

LAG/trunk configuration.

```yaml
fortiswitch:
  switch:
    trunk:
      - name: "lag1"
        mode: lacp-active
        members:
          - member_name: "port10"
          - member_name: "port11"
        description: "Uplink LAG to core switch"
        min_bundle: 1
        lacp_speed: slow
```

---

## FortiSwitch Storm Control

Broadcast/multicast/unicast storm control.

```yaml
fortiswitch:
  switch:
    storm_control:
      broadcast: enable
      unknown_unicast: enable
      unknown_multicast: enable
      rate: 500  # packets per second
      burst_size_level: 0
```

---

## FortiSwitch Port Security

MAC-based port security.

```yaml
fortiswitch:
  switch:
    security:
      port_security:
        - name: "port3"
          status: enable
          max_violations: 1
          violation_action: shutdown
          mac_addr:
            - mac: "00:11:22:33:44:55"
              description: "Authorized device"
```

---

## FortiSwitch QoS

Quality of Service configuration.

```yaml
fortiswitch:
  switch:
    qos:
      dot1p_map:
        - name: "default"
          priority_0: queue-0
          priority_1: queue-0
          priority_2: queue-1
          priority_3: queue-1
          priority_4: queue-2
          priority_5: queue-2
          priority_6: queue-3
          priority_7: queue-3

      queue_policy:
        - name: "default"
          schedule: weighted
          rate_by: kbps

      ip_dscp_map:
        - name: "default"
          description: "Default DSCP to queue mapping"
```

---

# FortiAP Configuration

## FortiAP System

FortiAP management through FortiGate.

```yaml
fortigate:
  wireless_controller:
    # AP global settings
    setting:
      account_id: ""
      country: "US"
      darrp_optimize: 86400
      device_weight: 1
      duplicate_ssid: disable

    # Timers
    timers:
      ble_scan_report_intv: 30
      client_idle_timeout: 120
      darrp_day: "sunday monday tuesday wednesday thursday friday saturday"
      darrp_optimize: 86400
      darrp_time:
        - "00:00:00"
      discovery_interval: 5
      echo_interval: 30
      fake_ap_log: 1
      ipsec_intf_cleanup: 120
      radio_stats_interval: 15
      rogue_ap_log: 0
      sta_stats_interval: 1
```

---

## FortiAP Wireless Profiles

Wireless profile configuration for FortiAPs.

```yaml
fortigate:
  wireless_controller:
    # WTP (Wireless Termination Point) profile
    wtp_profile:
      - name: "FAP-default"
        comment: "Default FortiAP profile"
        platform:
          type: "AP-default"

        # Radio settings - 2.4GHz
        radio_1:
          mode: "ap"
          band: "802.11n,g-only"
          channel:
            - "1"
            - "6"
            - "11"
          auto_power_level: enable
          auto_power_high: 17
          auto_power_low: 10
          power_level: 100

          # 80211n settings
          n80211d: enable
          spectrum_analysis: disable
          vaps:
            - name: "Corporate-WiFi"
            - name: "Guest-WiFi"

        # Radio settings - 5GHz
        radio_2:
          mode: "ap"
          band: "802.11ac"
          channel:
            - "36"
            - "40"
            - "44"
            - "48"
          auto_power_level: enable
          auto_power_high: 17
          auto_power_low: 10
          power_level: 100

          # 80211ac settings
          n80211d: enable
          channel_bonding: "80MHz"
          vaps:
            - name: "Corporate-WiFi"
            - name: "Guest-WiFi"

        # LED schedules
        led_state: enable
        led_schedules:
          - name: "always"
```

---

## FortiAP SSIDs

SSID/VAP configuration.

```yaml
fortigate:
  wireless_controller:
    vap:
      # Corporate SSID
      - name: "Corporate-WiFi"
        ssid: "CompanyWiFi"
        security: "wpa2-only-enterprise"
        auth: "radius"
        encrypt: "AES"

        # RADIUS settings
        radius_server: "RADIUS1"
        acct_interim_interval: 600

        # Additional settings
        broadcast_ssid: enable
        max_clients: 100
        max_clients_ap: 50
        local_bridging: disable
        pmf: optional

        # Fast roaming
        fast_roaming: enable
        ft_mobility_domain: 1000
        ft_over_ds: enable
        ft_r0_key_lifetime: 480

        # Rate limiting
        rate_limit: 0  # 0 = unlimited

      # Guest SSID
      - name: "Guest-WiFi"
        ssid: "Guest"
        security: "wpa2-only-personal"
        passphrase: "GuestPassword123"
        encrypt: "AES"

        # Captive portal
        portal_message_override_group: "guest-portal"
        portal_type: "auth+auth-disclaimer"

        # Guest settings
        broadcast_ssid: enable
        max_clients: 50
        max_clients_ap: 25
        local_bridging: disable
        intra_vap_privacy: enable

        # VLAN
        vlanid: 20

        # Rate limiting
        rate_limit: 5000  # kbps per client

      # IoT SSID
      - name: "IoT-WiFi"
        ssid: "IoT-Devices"
        security: "wpa2-only-personal"
        passphrase: "IoTSecurePass456"
        encrypt: "AES"

        broadcast_ssid: disable
        max_clients: 100
        local_bridging: disable
        pmf: required
        vlanid: 30
```

---

## FortiAP Radio Settings

Advanced radio configuration.

```yaml
fortigate:
  wireless_controller:
    # Radio Resource Provisioning (RRP)
    rrp_profile:
      - name: "default"
        comment: "Default RRP profile"

        # 2.4GHz
        darrp_optimize: 86400
        mode: "ap"

        # Channel utilization
        channel_utilization: enable
        rogue_ap_detection: enable

    # DARRP (Distributed Automatic Radio Resource Provisioning)
    setting:
      darrp_optimize: 86400
      darrp_optimize_schedules:
        - name: "always"

    # Spectrum analysis
    spectrum_analysis:
      - name: "spectrum-profile"
        schedule: "always"
```

---

# FortiExtender Configuration

## FortiExtender Configuration

FortiExtender cellular WAN extender configuration.

```yaml
fortigate:
  extender_controller:
    extender:
      - name: "FEX-01"
        id: "FEX-01-SERIAL"
        authorized: enable
        admin: enable

        # Connection settings
        device_id: 12345
        extension_type: "wan-extension"

        # Profile
        profile: "default"

        # Allowaccess
        allowaccess: "ping https ssh"

        # Login password
        login_password: "extender-password"

        # Override settings
        override_allowaccess: enable
        override_login_password_change: enable
        override_enforce_bandwidth: enable

        # Bandwidth enforcement
        enforce_bandwidth: enable
        bandwidth_limit: 100000  # kbps

        # Modem settings
        modem1:
          ifname: "modem1"
          redundant_mode: disable
          redundant_intf: ""
          conn_status: 0
          default_sim: "sim1"
          gps: enable

          auto_switch:
            disconnect: enable
            disconnect_threshold: 30
            disconnect_period: 600
            switch_back: "timer"
            switch_back_time: "00:00:00"
            switch_back_timer: 86400

          sim1:
            status: enable
            pin_status: disable
            pin: ""

          sim2:
            status: disable

        modem2:
          ifname: "modem2"
          redundant_mode: disable
          conn_status: 0
          default_sim: "sim1"
          gps: disable
```

---

## FortiExtender Modem Settings

Detailed modem/SIM configuration.

```yaml
fortigate:
  system:
    modem:
      - id: 1
        status: enable
        pin_code: ""
        network_mode: "auto"  # auto, lte, 3g, 2g

        # Connection settings
        auto_dial: enable
        dial_mode: "auto"
        idle_timer: 0
        redial: "none"

        # Data plan
        extra_init: ""
        auth_type: "auto"
        username: ""
        password: ""

      # LTE settings
      lte_settings:
        - modem_id: 1
          mode: "lte"
          apn: "internet"
          auth_type: "none"
          username: ""
          password: ""
```

---

## Complete Fortinet Example Configuration

Here's a complete example for a FortiGate with FortiSwitch and FortiAP:

```yaml
# Complete Fortinet Configuration Example
# Small office with FortiGate, FortiSwitch, and FortiAP

fortigate:
  system:
    global:
      hostname: "FGT-Office-Main"
      timezone: "04"
      admin_sport: 443

    interface:
      - name: "wan1"
        vdom: "root"
        mode: dhcp
        type: physical
        alias: "Primary WAN"
        role: wan
        allowaccess: "ping"

      - name: "lan"
        vdom: "root"
        mode: static
        ip: "192.168.1.1/24"
        type: physical
        alias: "LAN"
        role: lan
        allowaccess: "ping https ssh"
        device_identification: enable

      - name: "guest"
        vdom: "root"
        type: vlan
        vlanid: 20
        interface: "lan"
        mode: static
        ip: "192.168.20.1/24"
        alias: "Guest Network"

    dhcp:
      server:
        - id: 1
          interface: "lan"
          status: enable
          dns_server1: "192.168.1.1"
          default_gateway: "192.168.1.1"
          netmask: "255.255.255.0"
          ip_range:
            - id: 1
              start_ip: "192.168.1.100"
              end_ip: "192.168.1.200"

        - id: 2
          interface: "guest"
          status: enable
          dns_server1: "192.168.20.1"
          default_gateway: "192.168.20.1"
          netmask: "255.255.255.0"
          ip_range:
            - id: 1
              start_ip: "192.168.20.50"
              end_ip: "192.168.20.100"

  firewall:
    address:
      - name: "LAN_subnet"
        type: subnet
        subnet: "192.168.1.0/24"

      - name: "Guest_subnet"
        type: subnet
        subnet: "192.168.20.0/24"

    policy:
      - policyid: 1
        name: "LAN_to_WAN"
        srcintf:
          - name: "lan"
        dstintf:
          - name: "wan1"
        srcaddr:
          - name: "LAN_subnet"
        dstaddr:
          - name: "all"
        action: accept
        schedule: "always"
        service:
          - name: "ALL"
        nat: enable

      - policyid: 2
        name: "Guest_to_WAN"
        srcintf:
          - name: "guest"
        dstintf:
          - name: "wan1"
        srcaddr:
          - name: "Guest_subnet"
        dstaddr:
          - name: "all"
        action: accept
        schedule: "always"
        service:
          - name: "ALL"
        nat: enable
        webfilter_profile: "default"

  wireless_controller:
    vap:
      - name: "Corporate"
        ssid: "OfficeWiFi"
        security: "wpa2-only-personal"
        passphrase: "SecurePassword123"
        vlanid: 1

      - name: "Guest"
        ssid: "GuestWiFi"
        security: "wpa2-only-personal"
        passphrase: "GuestPass456"
        vlanid: 20
        intra_vap_privacy: enable

fortiswitch:
  system:
    global:
      hostname: "FSW-Office-01"

  switch:
    interface:
      - name: "port1"
        description: "Uplink to FortiGate"
        allowed_vlans: "1,20"
        native_vlan: 1

      - name: "port2"
        description: "Workstation"
        allowed_vlans: "1"
        native_vlan: 1
```

---

## Notes and Best Practices

### FortiGate Best Practices

1. **Security Profiles**: Always enable UTM features for internet-bound traffic
2. **Logging**: Configure FortiAnalyzer or syslog for centralized logging
3. **HA Configuration**: Use dedicated heartbeat interfaces
4. **Firmware Updates**: Keep FortiOS up to date with latest patches
5. **VPN Security**: Use IKEv2 with strong encryption (AES-256, SHA-256)
6. **SD-WAN**: Implement health checks for all WAN links
7. **Admin Access**: Restrict admin access to management networks only

### FortiSwitch Best Practices

1. **Port Security**: Enable on user-facing ports
2. **BPDU Guard**: Enable on access ports to prevent loops
3. **Storm Control**: Configure to prevent broadcast storms
4. **VLANs**: Segment network traffic appropriately
5. **PoE**: Monitor power budget for PoE devices

### FortiAP Best Practices

1. **Channel Planning**: Use non-overlapping channels (1, 6, 11 for 2.4GHz)
2. **Power Levels**: Enable auto-power for optimal coverage
3. **Guest Networks**: Isolate guest traffic with separate VLAN
4. **Fast Roaming**: Enable 802.11r for VoIP devices
5. **PMF**: Enable Protected Management Frames for security

### Configuration Validation

Before applying:
- Verify VLAN IDs match across FortiGate/FortiSwitch
- Confirm IP addressing doesn't conflict
- Test firewall policies in log-only mode first
- Validate VPN configuration with small pilot
- Check certificate validity for SSL inspection

---

## Schema Version

Schema Version: 1.0.0
Last Updated: 2024-10-27
Compatible with: FortiOS 7.x, FortiSwitchOS 7.x
