import React from 'react'
import { Shield, Network, Wifi, Radio, Activity, AlertTriangle, CheckCircle, TrendingUp } from 'lucide-react'
import { Link } from 'react-router-dom'

function Dashboard() {
  return (
    <>
      <div className="content-header">
        <h1 className="content-title">Dashboard</h1>
        <div className="content-actions">
          <button className="btn btn-secondary">
            <Activity size={16} />
            Refresh
          </button>
        </div>
      </div>

      <div className="content-body">
        {/* Stats Grid */}
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-label">Total Devices</div>
            <div className="stat-value">26</div>
            <div className="stat-change positive">
              <TrendingUp size={14} />
              <span>+2 this week</span>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-label">Online Devices</div>
            <div className="stat-value" style={{color: 'var(--accent-green)'}}>24</div>
            <div className="stat-change">
              <span className="text-success">92% uptime</span>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-label">Offline Devices</div>
            <div className="stat-value" style={{color: 'var(--accent-red)'}}>2</div>
            <div className="stat-change">
              <AlertTriangle size={14} className="text-danger" />
              <span className="text-danger">Requires attention</span>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-label">Pending Updates</div>
            <div className="stat-value">5</div>
            <div className="stat-change">
              <span className="text-warning">3 critical</span>
            </div>
          </div>
        </div>

        {/* Device Type Summary */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Device Types</h3>
          </div>
          <div className="card-body">
            <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '15px'}}>
              <Link to="/firewalls" style={{textDecoration: 'none'}}>
                <div style={{
                  backgroundColor: 'var(--tertiary-bg)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '6px',
                  padding: '20px',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'var(--hover-bg)'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'var(--tertiary-bg)'}
                >
                  <div style={{display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '15px'}}>
                    <Shield size={24} style={{color: 'var(--accent-blue)'}} />
                    <h4 style={{color: 'var(--text-primary)', margin: 0}}>Firewalls / Routers</h4>
                  </div>
                  <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                    <div>
                      <div style={{fontSize: '24px', fontWeight: '600', color: 'var(--text-primary)'}}>4</div>
                      <div style={{fontSize: '12px', color: 'var(--text-secondary)'}}>devices</div>
                    </div>
                    <div>
                      <span className="status-badge status-online">3 online</span>
                    </div>
                  </div>
                </div>
              </Link>

              <Link to="/switches" style={{textDecoration: 'none'}}>
                <div style={{
                  backgroundColor: 'var(--tertiary-bg)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '6px',
                  padding: '20px',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'var(--hover-bg)'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'var(--tertiary-bg)'}
                >
                  <div style={{display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '15px'}}>
                    <Network size={24} style={{color: 'var(--accent-green)'}} />
                    <h4 style={{color: 'var(--text-primary)', margin: 0}}>Switches</h4>
                  </div>
                  <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                    <div>
                      <div style={{fontSize: '24px', fontWeight: '600', color: 'var(--text-primary)'}}>8</div>
                      <div style={{fontSize: '12px', color: 'var(--text-secondary)'}}>devices</div>
                    </div>
                    <div>
                      <span className="status-badge status-online">8 online</span>
                    </div>
                  </div>
                </div>
              </Link>

              <Link to="/access-points" style={{textDecoration: 'none'}}>
                <div style={{
                  backgroundColor: 'var(--tertiary-bg)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '6px',
                  padding: '20px',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'var(--hover-bg)'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'var(--tertiary-bg)'}
                >
                  <div style={{display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '15px'}}>
                    <Wifi size={24} style={{color: 'var(--accent-yellow)'}} />
                    <h4 style={{color: 'var(--text-primary)', margin: 0}}>Access Points</h4>
                  </div>
                  <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                    <div>
                      <div style={{fontSize: '24px', fontWeight: '600', color: 'var(--text-primary)'}}>12</div>
                      <div style={{fontSize: '12px', color: 'var(--text-secondary)'}}>devices</div>
                    </div>
                    <div>
                      <span className="status-badge status-online">11 online</span>
                    </div>
                  </div>
                </div>
              </Link>

              <Link to="/modems" style={{textDecoration: 'none'}}>
                <div style={{
                  backgroundColor: 'var(--tertiary-bg)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '6px',
                  padding: '20px',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'var(--hover-bg)'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'var(--tertiary-bg)'}
                >
                  <div style={{display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '15px'}}>
                    <Radio size={24} style={{color: 'var(--accent-orange)'}} />
                    <h4 style={{color: 'var(--text-primary)', margin: 0}}>5G Modems</h4>
                  </div>
                  <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                    <div>
                      <div style={{fontSize: '24px', fontWeight: '600', color: 'var(--text-primary)'}}>2</div>
                      <div style={{fontSize: '12px', color: 'var(--text-secondary)'}}>devices</div>
                    </div>
                    <div>
                      <span className="status-badge status-online">2 online</span>
                    </div>
                  </div>
                </div>
              </Link>
            </div>
          </div>
        </div>

        {/* Recent Alerts */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Recent Alerts</h3>
          </div>
          <div className="card-body">
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Time</th>
                    <th>Device</th>
                    <th>Type</th>
                    <th>Message</th>
                    <th>Severity</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>2 minutes ago</td>
                    <td>FW-HQ-01</td>
                    <td>Firewall</td>
                    <td>High CPU usage detected (85%)</td>
                    <td><span className="status-badge status-warning">Warning</span></td>
                  </tr>
                  <tr>
                    <td>15 minutes ago</td>
                    <td>AP-Office-3</td>
                    <td>Access Point</td>
                    <td>Device went offline</td>
                    <td><span className="status-badge status-offline">Critical</span></td>
                  </tr>
                  <tr>
                    <td>1 hour ago</td>
                    <td>SW-Main-01</td>
                    <td>Switch</td>
                    <td>Port 12 link down</td>
                    <td><span className="status-badge status-warning">Warning</span></td>
                  </tr>
                  <tr>
                    <td>2 hours ago</td>
                    <td>FW-Branch-02</td>
                    <td>Firewall</td>
                    <td>Firmware update available</td>
                    <td><span className="status-badge status-pending">Info</span></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

export default Dashboard
