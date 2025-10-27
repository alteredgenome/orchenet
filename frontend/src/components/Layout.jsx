import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  Shield,
  Network,
  Wifi,
  Radio,
  Settings,
  Bell,
  Search,
  User,
  ChevronDown
} from 'lucide-react'

function Layout({ children }) {
  const location = useLocation()

  const isActive = (path) => {
    return location.pathname === path || location.pathname.startsWith(path + '/')
  }

  return (
    <>
      {/* Header */}
      <header className="app-header">
        <div className="header-left">
          <div className="logo">
            <Network size={28} />
            <span>OrcheNet</span>
          </div>
        </div>

        <div className="header-right">
          <div className="search-bar">
            <Search className="search-icon" size={16} />
            <input
              type="text"
              className="search-input"
              placeholder="Search devices..."
            />
          </div>

          <div className="header-icon">
            <Bell size={20} />
          </div>

          <div className="header-icon">
            <Settings size={20} />
          </div>

          <div className="user-menu">
            <User size={18} />
            <span>Admin</span>
            <ChevronDown size={16} />
          </div>
        </div>
      </header>

      {/* Main Container */}
      <div className="app-main">
        {/* Sidebar */}
        <aside className="sidebar">
          <div className="sidebar-section">
            <div className="sidebar-section-title">Overview</div>
            <Link
              to="/"
              className={`sidebar-item ${isActive('/') && !isActive('/firewalls') && !isActive('/switches') && !isActive('/access-points') && !isActive('/modems') ? 'active' : ''}`}
            >
              <LayoutDashboard className="sidebar-item-icon" size={20} />
              <span className="sidebar-item-text">Dashboard</span>
            </Link>
          </div>

          <div className="sidebar-section">
            <div className="sidebar-section-title">Device Management</div>
            <Link
              to="/firewalls"
              className={`sidebar-item ${isActive('/firewalls') ? 'active' : ''}`}
            >
              <Shield className="sidebar-item-icon" size={20} />
              <span className="sidebar-item-text">Firewalls / Routers</span>
              <span className="sidebar-item-badge">4</span>
            </Link>

            <Link
              to="/switches"
              className={`sidebar-item ${isActive('/switches') ? 'active' : ''}`}
            >
              <Network className="sidebar-item-icon" size={20} />
              <span className="sidebar-item-text">Switches</span>
              <span className="sidebar-item-badge">8</span>
            </Link>

            <Link
              to="/access-points"
              className={`sidebar-item ${isActive('/access-points') ? 'active' : ''}`}
            >
              <Wifi className="sidebar-item-icon" size={20} />
              <span className="sidebar-item-text">Access Points</span>
              <span className="sidebar-item-badge">12</span>
            </Link>

            <Link
              to="/modems"
              className={`sidebar-item ${isActive('/modems') ? 'active' : ''}`}
            >
              <Radio className="sidebar-item-icon" size={20} />
              <span className="sidebar-item-text">5G Modems</span>
              <span className="sidebar-item-badge">2</span>
            </Link>
          </div>
        </aside>

        {/* Main Content */}
        <main className="content">
          {children}
        </main>
      </div>
    </>
  )
}

export default Layout
