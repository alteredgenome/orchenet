import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Plus, RefreshCw, Download, Upload, Settings, MoreVertical } from 'lucide-react'
import AddDeviceWizard from '../../components/AddDeviceWizard'
import api from '../../services/api'

function FirewallsList() {
  const [view, setView] = useState('list') // list or grid
  const [showAddWizard, setShowAddWizard] = useState(false)
  const [devices, setDevices] = useState([])
  const [loading, setLoading] = useState(true)

  // Fetch devices from API
  const fetchDevices = async () => {
    try {
      setLoading(true)
      const response = await api.get('/api/devices')
      setDevices(response.data)
    } catch (error) {
      console.error('Error fetching devices:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDevices()
  }, [])

  const handleAddSuccess = () => {
    fetchDevices() // Refresh device list
  }

  // Mock data for display if no devices
  const firewalls = [
    {
      id: 1,
      name: 'FW-HQ-01',
      vendor: 'FortiGate',
      model: 'FortiGate 60F',
      ip: '192.168.1.1',
      status: 'online',
      cpu: 45,
      memory: 62,
      uptime: '45 days',
      version: '7.2.4',
      location: 'Headquarters'
    },
    {
      id: 2,
      name: 'FW-Branch-01',
      vendor: 'MikroTik',
      model: 'CCR1009',
      ip: '192.168.10.1',
      status: 'online',
      cpu: 28,
      memory: 41,
      uptime: '92 days',
      version: '7.11',
      location: 'Branch Office 1'
    },
    {
      id: 3,
      name: 'FW-Branch-02',
      vendor: 'WatchGuard',
      model: 'Firebox M370',
      ip: '192.168.20.1',
      status: 'offline',
      cpu: 0,
      memory: 0,
      uptime: 'N/A',
      version: '12.8.2',
      location: 'Branch Office 2'
    },
    {
      id: 4,
      name: 'FW-Remote-01',
      vendor: 'Ubiquiti',
      model: 'UDM Pro',
      ip: '192.168.30.1',
      status: 'online',
      cpu: 15,
      memory: 35,
      uptime: '12 days',
      version: '3.0.20',
      location: 'Remote Office'
    }
  ]

  // Use real devices if available, otherwise show mock data
  const displayDevices = devices.length > 0 ? devices : firewalls
  const stats = {
    total: displayDevices.length,
    online: displayDevices.filter(d => d.status === 'online').length,
    offline: displayDevices.filter(d => d.status === 'offline' || d.status === 'pending').length,
    avgCpu: Math.round(displayDevices.reduce((acc, d) => acc + (d.cpu || 0), 0) / (displayDevices.length || 1))
  }

  return (
    <>
      <AddDeviceWizard
        isOpen={showAddWizard}
        onClose={() => setShowAddWizard(false)}
        onSuccess={handleAddSuccess}
      />

      <div className="content-header">
        <h1 className="content-title">Firewalls / Routers</h1>
        <div className="content-actions">
          <button className="btn btn-secondary" onClick={fetchDevices}>
            <RefreshCw size={16} />
            Refresh
          </button>
          <button className="btn btn-secondary">
            <Download size={16} />
            Export
          </button>
          <button className="btn btn-primary" onClick={() => setShowAddWizard(true)}>
            <Plus size={16} />
            Add Device
          </button>
        </div>
      </div>

      <div className="content-body">
        {/* Stats */}
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-label">Total Firewalls</div>
            <div className="stat-value">{stats.total}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Online</div>
            <div className="stat-value" style={{color: 'var(--accent-green)'}}>{stats.online}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Offline</div>
            <div className="stat-value" style={{color: 'var(--accent-red)'}}>{stats.offline}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Avg CPU Usage</div>
            <div className="stat-value">{stats.avgCpu}%</div>
          </div>
        </div>

        {/* Device List */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Devices</h3>
            <div style={{display: 'flex', gap: '10px'}}>
              <button className="btn btn-secondary">
                <Settings size={16} />
                Filter
              </button>
            </div>
          </div>
          <div className="card-body" style={{padding: 0}}>
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Device Name</th>
                    <th>Vendor</th>
                    <th>Model</th>
                    <th>IP Address</th>
                    <th>Status</th>
                    <th>CPU</th>
                    <th>Memory</th>
                    <th>Uptime</th>
                    <th>Location</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {loading && (
                    <tr>
                      <td colSpan="10" style={{textAlign: 'center', padding: '40px'}}>
                        Loading devices...
                      </td>
                    </tr>
                  )}
                  {!loading && displayDevices.length === 0 && (
                    <tr>
                      <td colSpan="10" style={{textAlign: 'center', padding: '40px'}}>
                        No devices found. Click "Add Device" to get started.
                      </td>
                    </tr>
                  )}
                  {!loading && displayDevices.map(firewall => (
                    <tr key={firewall.id}>
                      <td>
                        <Link
                          to={`/firewalls/${firewall.id}`}
                          style={{color: 'var(--accent-blue)', textDecoration: 'none'}}
                        >
                          {firewall.name}
                        </Link>
                      </td>
                      <td>{firewall.vendor}</td>
                      <td>{firewall.model}</td>
                      <td style={{fontFamily: 'monospace'}}>{firewall.ip}</td>
                      <td>
                        <span className={`status-badge status-${firewall.status}`}>
                          {firewall.status}
                        </span>
                      </td>
                      <td>
                        <span style={{color: firewall.cpu > 70 ? 'var(--accent-red)' : 'var(--text-primary)'}}>
                          {firewall.cpu}%
                        </span>
                      </td>
                      <td>{firewall.memory}%</td>
                      <td>{firewall.uptime}</td>
                      <td className="text-muted">{firewall.location}</td>
                      <td>
                        <button className="btn btn-secondary" style={{padding: '4px 8px'}}>
                          <MoreVertical size={16} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

export default FirewallsList
