import { useState, useRef, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'

function ProfileDropdown({ user, onLogout }) {
    const [isOpen, setIsOpen] = useState(false)
    const dropdownRef = useRef(null)
    const navigate = useNavigate()

    useEffect(() => {
        function handleClickOutside(event) {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setIsOpen(false)
            }
        }
        document.addEventListener("mousedown", handleClickOutside)
        return () => {
            document.removeEventListener("mousedown", handleClickOutside)
        }
    }, [dropdownRef])

    return (
        <div className="profile-dropdown" ref={dropdownRef} style={{ position: 'relative' }}>
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="btn-profile"
                style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    background: 'transparent',
                    border: '1px solid var(--border-color)',
                    padding: '0.5rem 1rem',
                    borderRadius: '20px',
                    color: 'var(--text-light)',
                    cursor: 'pointer'
                }}
            >
                <div style={{
                    width: '24px',
                    height: '24px',
                    borderRadius: '50%',
                    background: 'var(--sagarr-cyan)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'black',
                    fontWeight: 'bold',
                    fontSize: '0.8rem'
                }}>
                    {user.username ? user.username[0].toUpperCase() : 'U'}
                </div>
                <span>{user.username || 'Profile'}</span>
                <span style={{ fontSize: '0.8rem' }}>{isOpen ? '▲' : '▼'}</span>
            </button>

            {isOpen && (
                <div style={{
                    position: 'absolute',
                    top: '120%',
                    right: 0,
                    width: '200px',
                    background: 'var(--bg-card)',
                    border: '1px solid var(--border-color)',
                    borderRadius: '8px',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.5)',
                    zIndex: 1000,
                    overflow: 'hidden'
                }}>
                    <div style={{ padding: '1rem', borderBottom: '1px solid var(--border-color)' }}>
                        <div style={{ fontWeight: 'bold', color: 'white' }}>{user.username}</div>
                        <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>{user.email}</div>
                    </div>

                    <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                        <li>
                            <Link
                                to="/history"
                                onClick={() => setIsOpen(false)}
                                style={{ display: 'block', padding: '0.75rem 1rem', color: 'var(--text-light)', textDecoration: 'none', transition: 'background 0.2s' }}
                                onMouseOver={(e) => e.target.style.background = 'rgba(255,255,255,0.05)'}
                                onMouseOut={(e) => e.target.style.background = 'transparent'}
                            >
                                History
                            </Link>
                        </li>
                        <li>
                            <Link
                                to="/settings"
                                onClick={() => setIsOpen(false)}
                                style={{ display: 'block', padding: '0.75rem 1rem', color: 'var(--text-light)', textDecoration: 'none', transition: 'background 0.2s' }}
                                onMouseOver={(e) => e.target.style.background = 'rgba(255,255,255,0.05)'}
                                onMouseOut={(e) => e.target.style.background = 'transparent'}
                            >
                                Settings
                            </Link>
                        </li>
                        {user.is_admin && (
                            <li>
                                <Link
                                    to="/admin"
                                    onClick={() => setIsOpen(false)}
                                    style={{ display: 'block', padding: '0.75rem 1rem', color: 'var(--text-light)', textDecoration: 'none', transition: 'background 0.2s' }}
                                    onMouseOver={(e) => e.target.style.background = 'rgba(255,255,255,0.05)'}
                                    onMouseOut={(e) => e.target.style.background = 'transparent'}
                                >
                                    Admin Dashboard
                                </Link>
                            </li>
                        )}
                        <li style={{ borderTop: '1px solid var(--border-color)' }}>
                            <button
                                onClick={() => {
                                    setIsOpen(false)
                                    onLogout()
                                }}
                                style={{
                                    width: '100%',
                                    textAlign: 'left',
                                    padding: '0.75rem 1rem',
                                    background: 'transparent',
                                    border: 'none',
                                    color: '#ef4444',
                                    cursor: 'pointer',
                                    fontSize: '1rem'
                                }}
                                onMouseOver={(e) => e.target.style.background = 'rgba(255,255,255,0.05)'}
                                onMouseOut={(e) => e.target.style.background = 'transparent'}
                            >
                                Logout
                            </button>
                        </li>
                    </ul>
                </div>
            )}
        </div>
    )
}

export default ProfileDropdown
