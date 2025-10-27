import React, { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Save } from 'lucide-react'

function AccessPointDetails() {
  const { id } = useParams()
  const [activeTab, setActiveTab] = useState('overview')

  return (
    <>
      <div className="content-header">
        <div style={{display: 'flex', alignItems: 'center', gap: '15px'}}>
          <Link to="/access-points" style={{color: 'var(--text-primary)'}}>
            <ArrowLeft size={20} />
          </Link>
          <h1 className="content-title">AP-Office-1</h1>
          <span className="status-badge status-online">online</span>
        </div>
        <div className="content-actions">
          <button className="btn btn-primary">
            <Save size={16} />
            Save Changes
          </button>
        </div>
      </div>

      <div className="content-body">
        <div className="tabs">
          <div className={`tab ${activeTab === 'overview' ? 'active' : ''}`} onClick={() => setActiveTab('overview')}>Overview</div>
          <div className={`tab ${activeTab === 'wireless' ? 'active' : ''}`} onClick={() => setActiveTab('wireless')}>Wireless</div>
          <div className={`tab ${activeTab === 'clients' ? 'active' : ''}`} onClick={() => setActiveTab('clients')}>Clients</div>
          <div className={`tab ${activeTab === 'config' ? 'active' : ''}`} onClick={() => setActiveTab('config')}>Configuration</div>
        </div>

        {activeTab === 'overview' && (
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">AP Information</h3>
            </div>
            <div className="card-body">
              <p>Access point overview and radio statistics</p>
            </div>
          </div>
        )}
      </div>
    </>
  )
}

export default AccessPointDetails
