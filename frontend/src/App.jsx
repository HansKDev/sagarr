import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom'
import Dashboard from './components/Dashboard'
import Login from './components/Login'
import LoginCallback from './components/LoginCallback'
import AdminSettings from './components/AdminSettings'
import { initAuthFromStorage } from './apiClient.js'

function ProtectedRoute({ children }) {
  const token = localStorage.getItem('token')
  if (!token) {
    return <Navigate to="/login" replace />
  }
  return children
}

function App() {
  useEffect(() => {
    // Ensure Axios has the auth header on initial load if a token exists.
    initAuthFromStorage()
  }, [])

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    window.location.href = '/login'
  }

  return (
    <Router>
      <div className="app-container">
        <nav style={{ padding: '1rem', borderBottom: '1px solid #333', marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <h1 style={{ margin: 0 }}>Sagarr</h1>
            {localStorage.getItem('token') && (
              <Link to="/admin" style={{ color: '#ccc', textDecoration: 'none', fontSize: '0.9rem' }}>Admin</Link>
            )}
          </div>
          {localStorage.getItem('token') && (
            <button onClick={handleLogout} style={{ background: 'transparent', border: '1px solid #666', color: 'white', padding: '0.5rem 1rem', cursor: 'pointer' }}>
              Logout
            </button>
          )}
        </nav>

        <Routes>
          <Route path="/" element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } />
          <Route path="/admin" element={
            <ProtectedRoute>
              <AdminSettings />
            </ProtectedRoute>
          } />
          <Route path="/login" element={<Login />} />
          <Route path="/login/callback" element={<LoginCallback />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
