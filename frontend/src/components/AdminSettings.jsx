import { useState, useEffect } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'

function AdminSettings() {
    const [settings, setSettings] = useState({
        TAUTULLI_URL: '',
        TAUTULLI_API_KEY: '',
        OVERSEERR_URL: '',
        OVERSEERR_API_KEY: '',
        AI_PROVIDER: 'openai',
        AI_API_KEY: '',
        AI_MODEL: ''
    })
    const [loading, setLoading] = useState(true)
    const [saving, setSaving] = useState(false)
    const [message, setMessage] = useState('')
    const navigate = useNavigate()

    useEffect(() => {
        fetchSettings()
    }, [])

    const fetchSettings = async () => {
        try {
            const token = localStorage.getItem('token')
            const res = await axios.get('/api/admin/settings', {
                headers: { Authorization: `Bearer ${token}` }
            })
            setSettings(res.data)
            setLoading(false)
        } catch (err) {
            console.error(err)
            setMessage('Error fetching settings. Are you logged in?')
            setLoading(false)
        }
    }

    const handleChange = (e) => {
        setSettings({ ...settings, [e.target.name]: e.target.value })
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        setSaving(true)
        setMessage('')
        try {
            const token = localStorage.getItem('token')
            await axios.post('/api/admin/settings', settings, {
                headers: { Authorization: `Bearer ${token}` }
            })
            setMessage('Settings updated successfully!')
            // Refresh to show masked keys again if needed, or just keep as is
            fetchSettings()
        } catch (err) {
            console.error(err)
            setMessage('Failed to update settings.')
        } finally {
            setSaving(false)
        }
    }

    if (loading) return <div style={{ padding: '2rem' }}>Loading settings...</div>

    return (
        <div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <h2>Admin Settings</h2>
                <button onClick={() => navigate('/')} style={{ background: 'transparent', border: '1px solid #666', color: 'white', padding: '0.5rem 1rem', cursor: 'pointer' }}>
                    Back to Dashboard
                </button>
            </div>

            {message && <div style={{ padding: '1rem', background: '#333', marginBottom: '1rem', borderRadius: '4px' }}>{message}</div>}

            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>

                <section>
                    <h3>Tautulli Configuration</h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                        <label>URL</label>
                        <input
                            type="text"
                            name="TAUTULLI_URL"
                            value={settings.TAUTULLI_URL}
                            onChange={handleChange}
                            placeholder="http://localhost:8181"
                            style={{ padding: '0.5rem', background: '#222', border: '1px solid #444', color: 'white' }}
                        />
                        <label>API Key</label>
                        <input
                            type="password"
                            name="TAUTULLI_API_KEY"
                            value={settings.TAUTULLI_API_KEY}
                            onChange={handleChange}
                            placeholder="Your API Key"
                            style={{ padding: '0.5rem', background: '#222', border: '1px solid #444', color: 'white' }}
                        />
                    </div>
                </section>

                <section>
                    <h3>Overseerr Configuration</h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                        <label>URL</label>
                        <input
                            type="text"
                            name="OVERSEERR_URL"
                            value={settings.OVERSEERR_URL}
                            onChange={handleChange}
                            placeholder="http://localhost:5055"
                            style={{ padding: '0.5rem', background: '#222', border: '1px solid #444', color: 'white' }}
                        />
                        <label>API Key</label>
                        <input
                            type="password"
                            name="OVERSEERR_API_KEY"
                            value={settings.OVERSEERR_API_KEY}
                            onChange={handleChange}
                            placeholder="Your API Key"
                            style={{ padding: '0.5rem', background: '#222', border: '1px solid #444', color: 'white' }}
                        />
                    </div>
                </section>

                <section>
                    <h3>AI Configuration</h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                        <label>Provider</label>
                        <select
                            name="AI_PROVIDER"
                            value={settings.AI_PROVIDER}
                            onChange={handleChange}
                            style={{ padding: '0.5rem', background: '#222', border: '1px solid #444', color: 'white' }}
                        >
                            <option value="openai">OpenAI</option>
                            <option value="generic">Generic / Ollama</option>
                        </select>

                        <label>API Key</label>
                        <input
                            type="password"
                            name="AI_API_KEY"
                            value={settings.AI_API_KEY}
                            onChange={handleChange}
                            placeholder="sk-..."
                            style={{ padding: '0.5rem', background: '#222', border: '1px solid #444', color: 'white' }}
                        />

                        <label>Model Name</label>
                        <input
                            type="text"
                            name="AI_MODEL"
                            value={settings.AI_MODEL}
                            onChange={handleChange}
                            placeholder="gpt-4o or llama3"
                            style={{ padding: '0.5rem', background: '#222', border: '1px solid #444', color: 'white' }}
                        />
                    </div>
                </section>

                <button
                    type="submit"
                    disabled={saving}
                    style={{
                        padding: '1rem',
                        fontSize: '1.1rem',
                        backgroundColor: '#e5a00d',
                        color: 'black',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        marginTop: '1rem'
                    }}
                >
                    {saving ? 'Saving...' : 'Save Settings'}
                </button>
            </form>
        </div>
    )
}

export default AdminSettings
