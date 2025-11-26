import { Link, useLocation, useNavigate } from 'react-router-dom'
import Logo from './Logo'

function NavBar() {
    const location = useLocation() // Triggers re-render on route change
    const navigate = useNavigate()

    const token = localStorage.getItem('token')
    const userStr = localStorage.getItem('user')
    let user = null
    try {
        user = JSON.parse(userStr)
    } catch (e) {
        // ignore
    }

    const handleLogout = () => {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        navigate('/login')
    }

    return (
        <nav className="nav-header">
            <Link to="/" style={{ textDecoration: 'none' }}>
                <Logo />
            </Link>

            <div className="nav-actions">
                {token && (
                    <>
                        <Link to="/history" className="nav-link">History</Link>
                        {user?.is_admin && (
                            <Link to="/admin" className="nav-link">Admin</Link>
                        )}
                        <button onClick={handleLogout} className="btn-logout">
                            Logout
                        </button>
                    </>
                )}
            </div>
        </nav>
    )
}

export default NavBar
