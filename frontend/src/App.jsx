import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom'
import Dashboard from './components/Dashboard'
import Login from './components/Login'
import LoginCallback from './components/LoginCallback'
import History from './components/History'
import AdminSettings from './components/AdminSettings'
import Logo from './components/Logo'
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
        <nav className="nav-header">
          <Link to="/" style={{ textDecoration: 'none' }}>
            <Logo />
          </Link>

          <div className="nav-actions">
            {localStorage.getItem('token') && (
              <>
                <Link to="/history" className="nav-link">History</Link>
                <Link to="/admin" className="nav-link">Admin</Link>
                <button onClick={handleLogout} className="btn-logout">
                  Logout
                </button>
              </>
            )}
          </div>
        </nav>

        <Routes>
          <Route path="/" element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } />
          <Route path="/history" element={
            <ProtectedRoute>
              <History />
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
