import React from 'react'
import { Link } from 'react-router-dom'
import { Plus, RefreshCw } from 'lucide-react'

function SwitchesList() {
  const switches = [
    { id: 1, name: 'SW-Main-01', vendor: 'UniFi', model: 'USW-24-POE', ip: '192.168.1.10', status: 'online', ports: 24, poePorts: 16 },
    { id: 2, name: 'SW-Floor1-01', vendor: 'FortiSwitch', model: 'FS-124E', ip: '192.168.1.11', status: 'online', ports: 24, poePorts: 0 },
    { id: 3, name: 'SW-Floor2-01', vendor: 'MikroTik', model: 'CRS328', ip: '192.168.1.12', status: 'online', ports: 28, poePorts: 4 },
  ]

  return (
    <>
      <div className="content-header">
        <h1 className="content-title">Switches</h1>
        <div className="content-actions">
          <button className="btn btn-secondary">
            <RefreshCw size={16} />
            Refresh
          </button>
          <button className="btn btn-primary">
            <Plus size={16} />
            Add Switch
          </button>
        </div>
      </div>

      <div className="content-body">
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-label">Total Switches</div>
            <div className="stat-value">8</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Online</div>
            <div className="stat-value" style={{color: 'var(--accent-green)'}}>8</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Total Ports</div>
            <div className="stat-value">192</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">PoE Ports</div>
            <div className="stat-value">96</div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Devices</h3>
          </div>
          <div className="card-body" style={{padding: 0}}>
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Vendor</th>
                    <th>Model</th>
                    <th>IP Address</th>
                    <th>Status</th>
                    <th>Ports</th>
                    <th>PoE Ports</th>
                  </tr>
                </thead>
                <tbody>
                  {switches.map(sw => (
                    <tr key={sw.id}>
                      <td>
                        <Link to={`/switches/${sw.id}`} style={{color: 'var(--accent-blue)', textDecoration: 'none'}}>
                          {sw.name}
                        </Link>
                      </td>
                      <td>{sw.vendor}</td>
                      <td>{sw.model}</td>
                      <td style={{fontFamily: 'monospace'}}>{sw.ip}</td>
                      <td><span className={`status-badge status-${sw.status}`}>{sw.status}</span></td>
                      <td>{sw.ports}</td>
                      <td>{sw.poePorts}</td>
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

export default SwitchesList
