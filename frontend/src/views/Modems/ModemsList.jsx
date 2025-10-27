import React from 'react'
import { Link } from 'react-router-dom'
import { Plus, RefreshCw } from 'lucide-react'

function ModemsList() {
  const modems = [
    { id: 1, name: 'Modem-Primary', vendor: 'FortiExtender', model: 'FEX-201F', ip: '192.168.1.30', status: 'online', signal: '-75 dBm', carrier: 'Verizon' },
    { id: 2, name: 'Modem-Backup', vendor: 'Cradlepoint', model: 'IBR900', ip: '192.168.1.31', status: 'online', signal: '-82 dBm', carrier: 'AT&T' },
  ]

  return (
    <>
      <div className="content-header">
        <h1 className="content-title">5G Modems</h1>
        <div className="content-actions">
          <button className="btn btn-secondary">
            <RefreshCw size={16} />
            Refresh
          </button>
          <button className="btn btn-primary">
            <Plus size={16} />
            Add Modem
          </button>
        </div>
      </div>

      <div className="content-body">
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-label">Total Modems</div>
            <div className="stat-value">2</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Online</div>
            <div className="stat-value" style={{color: 'var(--accent-green)'}}>2</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Avg Signal</div>
            <div className="stat-value">-79 dBm</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Data Usage</div>
            <div className="stat-value">145 GB</div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Modems</h3>
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
                    <th>Signal</th>
                    <th>Carrier</th>
                  </tr>
                </thead>
                <tbody>
                  {modems.map(modem => (
                    <tr key={modem.id}>
                      <td>
                        <Link to={`/modems/${modem.id}`} style={{color: 'var(--accent-blue)', textDecoration: 'none'}}>
                          {modem.name}
                        </Link>
                      </td>
                      <td>{modem.vendor}</td>
                      <td>{modem.model}</td>
                      <td style={{fontFamily: 'monospace'}}>{modem.ip}</td>
                      <td><span className={`status-badge status-${modem.status}`}>{modem.status}</span></td>
                      <td>{modem.signal}</td>
                      <td>{modem.carrier}</td>
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

export default ModemsList
