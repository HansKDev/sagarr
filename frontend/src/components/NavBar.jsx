import { Link, useLocation, useNavigate } from 'react-router-dom'
import Logo from './Logo'

import ProfileDropdown from './ProfileDropdown'

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
                {token && user && (
                    <ProfileDropdown user={user} onLogout={handleLogout} />
                )}
            </div>
        </nav>
    )
}

export default NavBar
