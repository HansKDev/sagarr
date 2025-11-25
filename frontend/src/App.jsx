import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom'
import Dashboard from './components/Dashboard'
import Login from './components/Login'
import LoginCallback from './components/LoginCallback'
import History from './components/History'
import AdminSettings from './components/AdminSettings'
import Logo from './components/Logo'
import { initAuthFromStorage } from './apiClient.js'

function getStoredUser() {
  const raw = localStorage.getItem('user')
  if (!raw) return null
  try {
    return JSON.parse(raw)
  } catch {
    return null
  }
}

function ProtectedRoute({ children }) {
  const token = localStorage.getItem('token')
  if (!token) {
    return <Navigate to="/login" replace />
  }
  return children
}

function AdminRoute({ children }) {
  const token = localStorage.getItem('token')
  const user = getStoredUser()
  const isAdmin = !!user?.is_admin

  if (!token) {
    return <Navigate to="/login" replace />
  }
  if (!isAdmin) {
    return <Navigate to="/" replace />
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
                {getStoredUser()?.is_admin && (
                  <Link to="/admin" className="nav-link">Admin</Link>
                )}
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
            <AdminRoute>
              <AdminSettings />
            </AdminRoute>
          } />
          <Route path="/login" element={<Login />} />
          <Route path="/login/callback" element={<LoginCallback />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
