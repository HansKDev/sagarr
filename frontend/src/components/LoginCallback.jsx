import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

function LoginCallback() {
    const navigate = useNavigate()
    const [status, setStatus] = useState('Verifying with Plex...')

    useEffect(() => {
        const verifyPin = async () => {
            const pinId = localStorage.getItem('plex_pin_id')
            if (!pinId) {
                setStatus('Error: No login session found.')
                return
            }

            try {
                const res = await axios.post('/api/auth/callback', { pin_id: parseInt(pinId) })
                const { access_token, user } = res.data

                // Store session
                localStorage.setItem('token', access_token)
                localStorage.setItem('user', JSON.stringify(user))
                localStorage.removeItem('plex_pin_id')

                setStatus('Success! Redirecting...')
                setTimeout(() => navigate('/'), 1000)
            } catch (err) {
                console.error(err)
                setStatus('Authentication failed. Please try again.')
                setTimeout(() => navigate('/login'), 2000)
            }
        }

        verifyPin()
    }, [navigate])

    return (
        <div style={{ marginTop: '4rem' }}>
            <h3>{status}</h3>
        </div>
    )
}

export default LoginCallback
