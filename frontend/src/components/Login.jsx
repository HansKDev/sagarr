import { useState } from 'react'
import axios from 'axios'

function Login() {
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)

    const handleLogin = async () => {
        setLoading(true)
        setError(null)
        try {
            const res = await axios.get('/api/auth/login')
            const { auth_url, pin_id } = res.data

            // Store pin_id for verification step
            localStorage.setItem('plex_pin_id', pin_id)

            // Redirect to Plex Auth
            window.location.href = auth_url
        } catch (err) {
            console.error(err)
            setError('Failed to initiate login')
            setLoading(false)
        }
    }

    return (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginTop: '4rem' }}>
            <h2>Welcome to Sagarr</h2>
            <p>Please sign in with your Plex account to continue.</p>

            {error && <p style={{ color: 'red' }}>{error}</p>}

            <button
                onClick={handleLogin}
                disabled={loading}
                style={{
                    padding: '1rem 2rem',
                    fontSize: '1.2rem',
                    backgroundColor: '#e5a00d',
                    color: 'black',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                }}
            >
                {loading ? 'Connecting...' : 'Sign in with Plex'}
            </button>
        </div>
    )
}

export default Login
