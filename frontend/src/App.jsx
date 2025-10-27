import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import './App.css'
import Layout from './components/Layout'
import Dashboard from './views/Dashboard'
import FirewallsList from './views/Firewalls/FirewallsList'
import FirewallDetails from './views/Firewalls/FirewallDetails'
import SwitchesList from './views/Switches/SwitchesList'
import SwitchDetails from './views/Switches/SwitchDetails'
import AccessPointsList from './views/AccessPoints/AccessPointsList'
import AccessPointDetails from './views/AccessPoints/AccessPointDetails'
import ModemsList from './views/Modems/ModemsList'
import ModemDetails from './views/Modems/ModemDetails'

function App() {
  return (
    <Router>
      <div className="App">
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />

            {/* Firewalls/Routers */}
            <Route path="/firewalls" element={<FirewallsList />} />
            <Route path="/firewalls/:id" element={<FirewallDetails />} />

            {/* Switches */}
            <Route path="/switches" element={<SwitchesList />} />
            <Route path="/switches/:id" element={<SwitchDetails />} />

            {/* Access Points */}
            <Route path="/access-points" element={<AccessPointsList />} />
            <Route path="/access-points/:id" element={<AccessPointDetails />} />

            {/* 5G Modems */}
            <Route path="/modems" element={<ModemsList />} />
            <Route path="/modems/:id" element={<ModemDetails />} />
          </Routes>
        </Layout>
      </div>
    </Router>
  )
}

export default App
