import React, { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  ArrowLeft,
  Save,
  RefreshCw,
  Power,
  Settings,
  Activity,
  Shield,
  Network,
  FileText,
  Clock,
  AlertTriangle
} from 'lucide-react'

function FirewallDetails() {
  const { id } = useParams()
  const [activeTab, setActiveTab] = useState('overview')

  // Mock device data
  const device = {
    id: id,
    name: 'FW-HQ-01',
    vendor: 'FortiGate',
    model: 'FortiGate 60F',
    ip: '192.168.1.1',
    status: 'online',
    cpu: 45,
    memory: 62,
    uptime: '45 days 12:34:56',
    version: '7.2.4',
    location: 'Headquarters',
    serialNumber: 'FG60F-XXXXXX',
    lastSeen: '2 minutes ago'
  }

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Activity },
    { id: 'configuration', label: 'Configuration', icon: Settings },
    { id: 'interfaces', label: 'Interfaces', icon: Network },
    { id: 'policies', label: 'Firewall Policies', icon: Shield },
    { id: 'vpn', label: 'VPN', icon: Network },
    { id: 'logs', label: 'Logs', icon: FileText },
    { id: 'history', label: 'History', icon: Clock }
  ]

  return (
    <>
      <div className="content-header">
        <div style={{display: 'flex', alignItems: 'center', gap: '15px'}}>
          <Link to="/firewalls" style={{color: 'var(--text-primary)'}}>
            <ArrowLeft size={20} />
          </Link>
          <div>
            <h1 className="content-title">{device.name}</h1>
            <div style={{fontSize: '13px', color: 'var(--text-secondary)', marginTop: '4px'}}>
              {device.vendor} {device.model}
            </div>
          </div>
          <span className={`status-badge status-${device.status}`}>
            {device.status}
          </span>
        </div>
        <div className="content-actions">
          <button className="btn btn-secondary">
            <RefreshCw size={16} />
            Refresh
          </button>
          <button className="btn btn-secondary">
            <Power size={16} />
            Reboot
          </button>
          <button className="btn btn-primary">
            <Save size={16} />
            Save Changes
          </button>
        </div>
      </div>

      <div className="content-body">
        {/* Tabs */}
        <div className="tabs">
          {tabs.map(tab => (
            <div
              key={tab.id}
              className={`tab ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <tab.icon size={16} style={{marginRight: '6px'}} />
              {tab.label}
            </div>
          ))}
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && <OverviewTab device={device} />}
        {activeTab === 'configuration' && <ConfigurationTab device={device} />}
        {activeTab === 'interfaces' && <InterfacesTab device={device} />}
        {activeTab === 'policies' && <PoliciesTab device={device} />}
        {activeTab === 'vpn' && <VPNTab device={device} />}
        {activeTab === 'logs' && <LogsTab device={device} />}
        {activeTab === 'history' && <HistoryTab device={device} />}
      </div>
    </>
  )
}

function OverviewTab({ device }) {
  return (
    <div>
      {/* Device Info */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Device Information</h3>
        </div>
        <div className="card-body">
          <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px'}}>
            <div>
              <div className="form-label">Device Name</div>
              <div style={{fontSize: '15px'}}>{device.name}</div>
            </div>
            <div>
              <div className="form-label">IP Address</div>
              <div style={{fontSize: '15px', fontFamily: 'monospace'}}>{device.ip}</div>
            </div>
            <div>
              <div className="form-label">Serial Number</div>
              <div style={{fontSize: '15px', fontFamily: 'monospace'}}>{device.serialNumber}</div>
            </div>
            <div>
              <div className="form-label">Firmware Version</div>
              <div style={{fontSize: '15px'}}>{device.version}</div>
            </div>
            <div>
              <div className="form-label">Location</div>
              <div style={{fontSize: '15px'}}>{device.location}</div>
            </div>
            <div>
              <div className="form-label">Last Seen</div>
              <div style={{fontSize: '15px'}}>{device.lastSeen}</div>
            </div>
          </div>
        </div>
      </div>

      {/* System Resources */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">System Resources</h3>
        </div>
        <div className="card-body">
          <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px'}}>
            <div>
              <div className="form-label">CPU Usage</div>
              <div style={{fontSize: '24px', fontWeight: '600', marginTop: '8px'}}>{device.cpu}%</div>
              <div style={{
                width: '100%',
                height: '8px',
                backgroundColor: 'var(--tertiary-bg)',
                borderRadius: '4px',
                marginTop: '12px',
                overflow: 'hidden'
              }}>
                <div style={{
                  width: `${device.cpu}%`,
                  height: '100%',
                  backgroundColor: device.cpu > 70 ? 'var(--accent-red)' : 'var(--accent-blue)',
                  transition: 'width 0.3s'
                }}></div>
              </div>
            </div>

            <div>
              <div className="form-label">Memory Usage</div>
              <div style={{fontSize: '24px', fontWeight: '600', marginTop: '8px'}}>{device.memory}%</div>
              <div style={{
                width: '100%',
                height: '8px',
                backgroundColor: 'var(--tertiary-bg)',
                borderRadius: '4px',
                marginTop: '12px',
                overflow: 'hidden'
              }}>
                <div style={{
                  width: `${device.memory}%`,
                  height: '100%',
                  backgroundColor: device.memory > 80 ? 'var(--accent-red)' : 'var(--accent-green)',
                  transition: 'width 0.3s'
                }}></div>
              </div>
            </div>

            <div>
              <div className="form-label">Uptime</div>
              <div style={{fontSize: '24px', fontWeight: '600', marginTop: '8px'}}>{device.uptime.split(' ')[0]}</div>
              <div style={{fontSize: '13px', color: 'var(--text-secondary)', marginTop: '8px'}}>
                {device.uptime}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px'}}>
        <div className="card">
          <div className="card-body">
            <div className="form-label">Active Sessions</div>
            <div style={{fontSize: '28px', fontWeight: '600', marginTop: '8px'}}>2,451</div>
            <div style={{fontSize: '13px', color: 'var(--text-secondary)', marginTop: '8px'}}>
              <span className="text-success">+12%</span> from yesterday
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-body">
            <div className="form-label">Throughput</div>
            <div style={{fontSize: '28px', fontWeight: '600', marginTop: '8px'}}>342 Mbps</div>
            <div style={{fontSize: '13px', color: 'var(--text-secondary)', marginTop: '8px'}}>
              ↑ 125 Mbps ↓ 217 Mbps
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-body">
            <div className="form-label">Threats Blocked</div>
            <div style={{fontSize: '28px', fontWeight: '600', marginTop: '8px'}}>1,234</div>
            <div style={{fontSize: '13px', color: 'var(--text-secondary)', marginTop: '8px'}}>
              Last 24 hours
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-body">
            <div className="form-label">VPN Tunnels</div>
            <div style={{fontSize: '28px', fontWeight: '600', marginTop: '8px'}}>3/5</div>
            <div style={{fontSize: '13px', color: 'var(--text-secondary)', marginTop: '8px'}}>
              Active tunnels
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function ConfigurationTab({ device }) {
  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">Device Configuration (YAML)</h3>
        <div style={{display: 'flex', gap: '10px'}}>
          <button className="btn btn-secondary">Import</button>
          <button className="btn btn-secondary">Export</button>
        </div>
      </div>
      <div className="card-body">
        <textarea
          className="form-textarea"
          style={{minHeight: '500px', fontSize: '13px'}}
          defaultValue={`device:
  name: "${device.name}"
  vendor: "${device.vendor.toLowerCase()}"
  location: "${device.location}"

system:
  hostname: "${device.name}"
  timezone: "America/New_York"

interfaces:
  - name: "wan1"
    type: "physical"
    addressing:
      mode: "dhcp"
    zone: "wan"

  - name: "lan1"
    type: "physical"
    addressing:
      mode: "static"
      ipv4: "${device.ip}/24"
    zone: "lan"

firewall:
  rules:
    - name: "allow-outbound"
      source:
        zones: ["lan"]
      destination:
        zones: ["wan"]
      action: "accept"
      nat:
        enabled: true
        type: "masquerade"`}
        />
        <div style={{marginTop: '15px', display: 'flex', gap: '10px'}}>
          <button className="btn btn-primary">
            <Save size={16} />
            Save Configuration
          </button>
          <button className="btn btn-secondary">Validate</button>
          <button className="btn btn-secondary">Preview Commands</button>
        </div>
      </div>
    </div>
  )
}

function InterfacesTab({ device }) {
  const interfaces = [
    { name: 'wan1', type: 'WAN', ip: '203.0.113.10/30', status: 'up', speed: '1000 Mbps' },
    { name: 'lan1', type: 'LAN', ip: '192.168.1.1/24', status: 'up', speed: '1000 Mbps' },
    { name: 'vlan10', type: 'VLAN', ip: '192.168.10.1/24', status: 'up', speed: '1000 Mbps' },
    { name: 'vlan20', type: 'VLAN', ip: '192.168.20.1/24', status: 'up', speed: '1000 Mbps' }
  ]

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">Network Interfaces</h3>
        <button className="btn btn-primary">Add Interface</button>
      </div>
      <div className="card-body" style={{padding: 0}}>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Interface</th>
                <th>Type</th>
                <th>IP Address</th>
                <th>Status</th>
                <th>Speed</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {interfaces.map((iface, idx) => (
                <tr key={idx}>
                  <td style={{fontFamily: 'monospace', fontWeight: '600'}}>{iface.name}</td>
                  <td>{iface.type}</td>
                  <td style={{fontFamily: 'monospace'}}>{iface.ip}</td>
                  <td><span className="status-badge status-online">{iface.status}</span></td>
                  <td>{iface.speed}</td>
                  <td>
                    <button className="btn btn-secondary" style={{padding: '4px 8px', marginRight: '5px'}}>
                      Edit
                    </button>
                    <button className="btn btn-danger" style={{padding: '4px 8px'}}>
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

function PoliciesTab({ device }) {
  const policies = [
    { id: 1, name: 'allow-outbound', from: 'LAN', to: 'WAN', action: 'Accept', nat: 'Yes', hits: '1.2M' },
    { id: 2, name: 'block-guest-to-lan', from: 'Guest', to: 'LAN', action: 'Deny', nat: 'No', hits: '453' },
    { id: 3, name: 'allow-vpn', from: 'VPN', to: 'LAN', action: 'Accept', nat: 'No', hits: '45K' }
  ]

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">Firewall Policies</h3>
        <button className="btn btn-primary">Add Policy</button>
      </div>
      <div className="card-body" style={{padding: 0}}>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Order</th>
                <th>Name</th>
                <th>From Zone</th>
                <th>To Zone</th>
                <th>Action</th>
                <th>NAT</th>
                <th>Hits</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {policies.map((policy, idx) => (
                <tr key={policy.id}>
                  <td>{idx + 1}</td>
                  <td style={{fontFamily: 'monospace'}}>{policy.name}</td>
                  <td>{policy.from}</td>
                  <td>{policy.to}</td>
                  <td>
                    <span className={`status-badge ${policy.action === 'Accept' ? 'status-online' : 'status-offline'}`}>
                      {policy.action}
                    </span>
                  </td>
                  <td>{policy.nat}</td>
                  <td>{policy.hits}</td>
                  <td>
                    <button className="btn btn-secondary" style={{padding: '4px 8px', marginRight: '5px'}}>
                      Edit
                    </button>
                    <button className="btn btn-danger" style={{padding: '4px 8px'}}>
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

function VPNTab({ device }) {
  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">VPN Tunnels</h3>
        <button className="btn btn-primary">Add Tunnel</button>
      </div>
      <div className="card-body">
        <p className="text-muted">VPN configuration panel coming soon...</p>
      </div>
    </div>
  )
}

function LogsTab({ device }) {
  const logs = [
    { time: '10:23:45', type: 'Info', message: 'Interface wan1: Link up' },
    { time: '10:22:10', type: 'Warning', message: 'High CPU usage: 85%' },
    { time: '10:20:33', type: 'Info', message: 'VPN tunnel established to 198.51.100.10' },
    { time: '10:18:22', type: 'Security', message: 'Blocked access attempt from 203.0.113.50' }
  ]

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">System Logs</h3>
        <button className="btn btn-secondary">Export Logs</button>
      </div>
      <div className="card-body" style={{padding: 0}}>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Time</th>
                <th>Type</th>
                <th>Message</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log, idx) => (
                <tr key={idx}>
                  <td style={{fontFamily: 'monospace'}}>{log.time}</td>
                  <td>
                    <span className={`status-badge ${
                      log.type === 'Warning' ? 'status-warning' :
                      log.type === 'Security' ? 'status-offline' :
                      'status-pending'
                    }`}>
                      {log.type}
                    </span>
                  </td>
                  <td>{log.message}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

function HistoryTab({ device }) {
  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">Configuration History</h3>
      </div>
      <div className="card-body">
        <p className="text-muted">Configuration history panel coming soon...</p>
      </div>
    </div>
  )
}

export default FirewallDetails
