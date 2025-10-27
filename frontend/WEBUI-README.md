# OrcheNet Web UI - FortiManager-Inspired Interface

## Overview

The OrcheNet Web UI is a professional, FortiManager-inspired interface for managing network devices across multiple vendors. Built with React and Vite, it provides a unified management experience for Firewalls/Routers, Switches, Access Points, and 5G Modems.

## Features

### 🎨 FortiManager-Style Design
- Dark theme with professional color scheme
- Consistent navigation and layout
- Intuitive sidebar with device type organization
- Clean, modern interface components

### 📊 Dashboard
- Overview of all managed devices
- Real-time statistics and metrics
- Device status at a glance
- Recent alerts and notifications
- Quick access to device types

### 🛡️ Firewall / Router Management
- Device list with status indicators
- Detailed device view with multiple tabs:
  - Overview (system resources, statistics)
  - Configuration (YAML editor)
  - Interfaces management
  - Firewall policies
  - VPN configuration
  - System logs
  - Configuration history

### 🔌 Switch Management
- Port configuration
- VLAN management
- PoE monitoring
- Link aggregation

### 📡 Access Point Management
- Wireless network configuration
- Client monitoring
- Radio settings (2.4GHz/5GHz)
- SSID management

### 📱 5G Modem Management
- Cellular signal monitoring
- Data usage tracking
- Carrier information
- Connection status

## Technology Stack

- **React 18.3.1** - UI framework
- **React Router 6.26.2** - Routing
- **Vite 5.4.9** - Build tool and dev server
- **Lucide React 0.454.0** - Icon library
- **Axios 1.7.7** - API client
- **js-yaml 4.1.0** - YAML parsing
- **Recharts 2.12.7** - Charts and graphs

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   └── Layout.jsx          # Main layout with header and sidebar
│   ├── views/
│   │   ├── Dashboard.jsx       # Main dashboard
│   │   ├── Firewalls/
│   │   │   ├── FirewallsList.jsx
│   │   │   └── FirewallDetails.jsx
│   │   ├── Switches/
│   │   │   ├── SwitchesList.jsx
│   │   │   └── SwitchDetails.jsx
│   │   ├── AccessPoints/
│   │   │   ├── AccessPointsList.jsx
│   │   │   └── AccessPointDetails.jsx
│   │   └── Modems/
│   │       ├── ModemsList.jsx
│   │       └── ModemDetails.jsx
│   ├── services/
│   │   └── api.js              # API client
│   ├── App.jsx                 # Main app component
│   ├── App.css                 # Global styles
│   ├── main.jsx                # Entry point
│   └── index.css               # Base styles
├── index.html
├── vite.config.js
└── package.json
```

## Getting Started

### Prerequisites
- Node.js 18+ or npm/pnpm

### Installation

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
# or
pnpm install
```

3. Create environment file:
```bash
cp .env.example .env
```

4. Update `.env` with your API URL:
```
VITE_API_URL=http://localhost:8000
```

### Development

Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

### Build for Production

```bash
npm run build
```

Output will be in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## Color Scheme

The UI uses a FortiManager-inspired dark theme:

| Color Variable | Hex Code | Usage |
|----------------|----------|-------|
| `--primary-bg` | #1a1d24 | Main background |
| `--secondary-bg` | #23262e | Cards, header |
| `--tertiary-bg` | #2a2d35 | Input backgrounds |
| `--border-color` | #3a3d45 | Borders |
| `--text-primary` | #ffffff | Primary text |
| `--text-secondary` | #a0a0a0 | Secondary text |
| `--accent-blue` | #4a9eff | Links, primary actions |
| `--accent-green` | #40c057 | Success, online status |
| `--accent-red` | #ff6b6b | Errors, offline status |
| `--accent-orange` | #ff922b | Warnings |
| `--accent-yellow` | #fab005 | Alerts |
| `--hover-bg` | #2d3038 | Hover states |
| `--selected-bg` | #363942 | Selected items |

## Component Patterns

### Page Header
```jsx
<div className="content-header">
  <h1 className="content-title">Page Title</h1>
  <div className="content-actions">
    <button className="btn btn-primary">Action</button>
  </div>
</div>
```

### Card
```jsx
<div className="card">
  <div className="card-header">
    <h3 className="card-title">Card Title</h3>
  </div>
  <div className="card-body">
    Content here
  </div>
</div>
```

### Status Badge
```jsx
<span className="status-badge status-online">online</span>
<span className="status-badge status-offline">offline</span>
<span className="status-badge status-warning">warning</span>
<span className="status-badge status-pending">pending</span>
```

### Tabs
```jsx
<div className="tabs">
  <div className={`tab ${active ? 'active' : ''}`}>Tab 1</div>
  <div className="tab">Tab 2</div>
</div>
```

### Stats Grid
```jsx
<div className="stats-grid">
  <div className="stat-card">
    <div className="stat-label">Label</div>
    <div className="stat-value">Value</div>
  </div>
</div>
```

## API Integration

The UI expects API endpoints at `VITE_API_URL`:

### Device Endpoints
- `GET /api/devices` - List all devices
- `GET /api/devices/{id}` - Get device details
- `POST /api/devices` - Create device
- `PUT /api/devices/{id}` - Update device
- `PUT /api/devices/{id}/config` - Update configuration
- `DELETE /api/devices/{id}` - Delete device

### Task Endpoints
- `GET /api/tasks` - List tasks
- `GET /api/tasks/device/{deviceId}` - Get device tasks
- `GET /api/tasks/{id}` - Get task details

## Device Types

### Firewalls/Routers
- **Vendors**: MikroTik, Fortinet, Ubiquiti, WatchGuard
- **Features**: Firewall policies, VPN, routing, interfaces
- **Configuration**: YAML-based unified schema

### Switches
- **Vendors**: UniFi, FortiSwitch, MikroTik, WatchGuard
- **Features**: Port configuration, VLANs, PoE management
- **Monitoring**: Port status, PoE usage, link speeds

### Access Points
- **Vendors**: UniFi, FortiAP, WatchGuard
- **Features**: SSID management, radio configuration, client monitoring
- **Monitoring**: Signal strength, client count, channel usage

### 5G Modems
- **Vendors**: FortiExtender, Cradlepoint, others
- **Features**: Cellular configuration, failover settings
- **Monitoring**: Signal strength, data usage, carrier info

## Features by Tab

### Firewall Detail Tabs

#### Overview
- Device information
- System resources (CPU, Memory, Uptime)
- Quick statistics (Sessions, Throughput, Threats, VPN Tunnels)

#### Configuration
- YAML editor for device configuration
- Import/Export configuration
- Validate and preview commands
- Unified schema support

#### Interfaces
- Network interface list
- IP addressing
- Status and statistics
- Add/Edit/Delete interfaces

#### Firewall Policies
- Policy list with order
- Source/Destination zones
- Actions (Accept/Deny)
- NAT configuration
- Hit counters

#### VPN
- Site-to-site tunnels
- Remote access configuration
- Tunnel status

#### Logs
- System logs
- Security events
- Traffic logs
- Export functionality

#### History
- Configuration changes
- Rollback capability
- Audit trail

## Keyboard Shortcuts

(To be implemented)
- `Ctrl+K` - Global search
- `Ctrl+S` - Save changes
- `R` - Refresh current view
- `N` - New device/item
- `Esc` - Cancel/Close

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## Performance

- Code splitting for optimal loading
- Lazy loading of components
- Optimized re-renders with React hooks
- Virtual scrolling for large lists (future enhancement)

## Accessibility

- Semantic HTML
- ARIA labels (to be enhanced)
- Keyboard navigation (to be enhanced)
- Color contrast ratios meet WCAG AA

## Future Enhancements

### Short Term
- [ ] Real-time updates via WebSockets
- [ ] Advanced filtering and search
- [ ] Bulk operations
- [ ] Configuration templates
- [ ] Dark/Light theme toggle

### Medium Term
- [ ] Drag-and-drop interface
- [ ] Advanced charts and graphs
- [ ] Custom dashboards
- [ ] Notification system
- [ ] Multi-user support with RBAC

### Long Term
- [ ] Mobile responsive design
- [ ] Native mobile apps
- [ ] AI-powered recommendations
- [ ] Automated workflows
- [ ] Multi-site management

## Troubleshooting

### Development Server Won't Start
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### API Connection Issues
- Verify `VITE_API_URL` in `.env`
- Check backend is running on port 8000
- Check browser console for CORS errors

### Build Errors
```bash
# Clean build cache
npm run build -- --force
```

## Contributing

1. Follow the existing component structure
2. Use the established color scheme
3. Maintain FortiManager-style design patterns
4. Add PropTypes for all components
5. Write clear comments for complex logic

## License

Part of the OrcheNet project. See main repository LICENSE file.
