import React, { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Save } from 'lucide-react'

function ModemDetails() {
  const { id } = useParams()
  const [activeTab, setActiveTab] = useState('overview')

  return (
    <>
      <div className="content-header">
        <div style={{display: 'flex', alignItems: 'center', gap: '15px'}}>
          <Link to="/modems" style={{color: 'var(--text-primary)'}}>
            <ArrowLeft size={20} />
          </Link>
          <h1 className="content-title">Modem-Primary</h1>
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
          <div className={`tab ${activeTab === 'cellular' ? 'active' : ''}`} onClick={() => setActiveTab('cellular')}>Cellular</div>
          <div className={`tab ${activeTab === 'data' ? 'active' : ''}`} onClick={() => setActiveTab('data')}>Data Usage</div>
          <div className={`tab ${activeTab === 'config' ? 'active' : ''}`} onClick={() => setActiveTab('config')}>Configuration</div>
        </div>

        {activeTab === 'overview' && (
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Modem Information</h3>
            </div>
            <div className="card-body">
              <p>5G modem overview and signal information</p>
            </div>
          </div>
        )}
      </div>
    </>
  )
}

export default ModemDetails
