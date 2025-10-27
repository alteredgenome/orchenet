import React from 'react'
import { Link } from 'react-router-dom'
import { Plus, RefreshCw } from 'lucide-react'

function AccessPointsList() {
  const aps = [
    { id: 1, name: 'AP-Office-1', vendor: 'UniFi', model: 'U6-LR', ip: '192.168.1.20', status: 'online', clients: 15 },
    { id: 2, name: 'AP-Office-2', vendor: 'FortiAP', model: 'FAP-231F', ip: '192.168.1.21', status: 'online', clients: 22 },
    { id: 3, name: 'AP-Warehouse', vendor: 'WatchGuard', model: 'AP325', ip: '192.168.1.22', status: 'offline', clients: 0 },
  ]

  return (
    <>
      <div className="content-header">
        <h1 className="content-title">Access Points</h1>
        <div className="content-actions">
          <button className="btn btn-secondary">
            <RefreshCw size={16} />
            Refresh
          </button>
          <button className="btn btn-primary">
            <Plus size={16} />
            Add AP
          </button>
        </div>
      </div>

      <div className="content-body">
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-label">Total APs</div>
            <div className="stat-value">12</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Online</div>
            <div className="stat-value" style={{color: 'var(--accent-green)'}}>11</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Total Clients</div>
            <div className="stat-value">147</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">SSIDs</div>
            <div className="stat-value">3</div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Access Points</h3>
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
                    <th>Clients</th>
                  </tr>
                </thead>
                <tbody>
                  {aps.map(ap => (
                    <tr key={ap.id}>
                      <td>
                        <Link to={`/access-points/${ap.id}`} style={{color: 'var(--accent-blue)', textDecoration: 'none'}}>
                          {ap.name}
                        </Link>
                      </td>
                      <td>{ap.vendor}</td>
                      <td>{ap.model}</td>
                      <td style={{fontFamily: 'monospace'}}>{ap.ip}</td>
                      <td><span className={`status-badge status-${ap.status}`}>{ap.status}</span></td>
                      <td>{ap.clients}</td>
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

export default AccessPointsList
