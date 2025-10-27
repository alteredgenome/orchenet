import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import './App.css'

function App() {
  return (
    <Router>
      <div className="App">
        <header>
          <h1>OrcheNet</h1>
          <p>Network Device Orchestration Platform</p>
        </header>
        <main>
          <Routes>
            <Route path="/" element={<Home />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

function Home() {
  return (
    <div>
      <h2>Welcome to OrcheNet</h2>
      <p>Device management interface coming soon...</p>
    </div>
  )
}

export default App
