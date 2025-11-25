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
        AI_MODEL: '',
        TMDB_API_KEY: '',
        AI_FALLBACK_PROVIDER: '',
        AI_FALLBACK_API_KEY: '',
        AI_FALLBACK_MODEL: ''
    })
    const [loading, setLoading] = useState(true)
    const [saving, setSaving] = useState(false)
    const [message, setMessage] = useState('')
    const [testMessages, setTestMessages] = useState({
        tautulli: '',
        overseerr: '',
        ai: '',
        tmdb: ''
    })
    const [testing, setTesting] = useState({
        tautulli: false,
        overseerr: false,
        ai: false,
        tmdb: false
    })
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

    const saveSettings = async (scopeLabel) => {
        setSaving(true)
        setMessage('')

        try {
            const token = localStorage.getItem('token')
            await axios.post('/api/admin/settings', settings, {
                headers: { Authorization: `Bearer ${token}` }
            })
            const label = scopeLabel ? `${scopeLabel} settings` : 'Settings'
            setMessage(`${label} updated successfully!`)
            // Refresh to show masked keys again if needed, or just keep as is
            fetchSettings()
        } catch (err) {
            console.error(err)
            setMessage('Failed to update settings.')
        } finally {
            setSaving(false)
        }
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        await saveSettings()
    }

    const runTest = async (service) => {
        setTesting((prev) => ({ ...prev, [service]: true }))
        setTestMessages((prev) => ({ ...prev, [service]: '' }))
        try {
            const token = localStorage.getItem('token')
            const res = await axios.get(`/api/admin/test/${service}`, {
                headers: { Authorization: `Bearer ${token}` }
            })
            setTestMessages((prev) => ({ ...prev, [service]: res.data.message || 'OK' }))
        } catch (err) {
            console.error(err)
            let msg = 'Test failed.'
            if (err.response?.data?.detail) {
                msg = typeof err.response.data.detail === 'string'
                    ? err.response.data.detail
                    : JSON.stringify(err.response.data.detail)
            }
            setTestMessages((prev) => ({ ...prev, [service]: msg }))
        } finally {
            setTesting((prev) => ({ ...prev, [service]: false }))
        }
    }

    if (loading) return <div style={{ padding: '2rem' }}>Loading settings...</div>

    return (
        <div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <h2>Admin Settings</h2>
                <button onClick={() => navigate('/')} className="btn btn-ghost">
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
                    <div style={{ marginTop: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <button
                            type="button"
                            onClick={() => saveSettings('Tautulli')}
                            disabled={saving}
                            className="btn btn-primary"
                        >
                            {saving ? 'Saving...' : 'Save Tautulli'}
                        </button>
                        <button
                            type="button"
                            onClick={() => runTest('tautulli')}
                            disabled={testing.tautulli}
                            className="btn btn-secondary"
                        >
                            {testing.tautulli ? 'Testing...' : 'Test Tautulli'}
                        </button>
                        {testMessages.tautulli && (
                            <span style={{ fontSize: '0.85rem', color: '#e5e5e5' }}>{testMessages.tautulli}</span>
                        )}
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
                    <div style={{ marginTop: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <button
                            type="button"
                            onClick={() => saveSettings('Overseerr')}
                            disabled={saving}
                            className="btn btn-primary"
                        >
                            {saving ? 'Saving...' : 'Save Overseerr'}
                        </button>
                        <button
                            type="button"
                            onClick={() => runTest('overseerr')}
                            disabled={testing.overseerr}
                            className="btn btn-secondary"
                        >
                            {testing.overseerr ? 'Testing...' : 'Test Overseerr'}
                        </button>
                        {testMessages.overseerr && (
                            <span style={{ fontSize: '0.85rem', color: '#e5e5e5' }}>{testMessages.overseerr}</span>
                        )}
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
                    <div style={{ marginTop: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <button
                            type="button"
                            onClick={() => saveSettings('AI')}
                            disabled={saving}
                            className="btn btn-primary"
                        >
                            {saving ? 'Saving...' : 'Save AI'}
                        </button>
                        <button
                            type="button"
                            onClick={() => runTest('ai')}
                            disabled={testing.ai}
                            className="btn btn-secondary"
                        >
                            {testing.ai ? 'Testing...' : 'Test AI'}
                        </button>
                        {testMessages.ai && (
                            <span style={{ fontSize: '0.85rem', color: '#e5e5e5' }}>{testMessages.ai}</span>
                        )}
                    </div>
                </section>

                <section>
                    <h3>AI Fallback Configuration</h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                        <p style={{ fontSize: '0.85rem', color: '#cbd5f5' }}>
                            Optional secondary provider used when the primary AI fails (for example due to quota limits).
                            Configure this with a cheaper or free endpoint if available.
                        </p>

                        <label>Fallback Provider</label>
                        <select
                            name="AI_FALLBACK_PROVIDER"
                            value={settings.AI_FALLBACK_PROVIDER}
                            onChange={handleChange}
                            style={{ padding: '0.5rem', background: '#222', border: '1px solid #444', color: 'white' }}
                        >
                            <option value="">Disabled</option>
                            <option value="openai">OpenAI</option>
                            <option value="generic">Generic / Ollama</option>
                        </select>

                        <label>Fallback API Key</label>
                        <input
                            type="password"
                            name="AI_FALLBACK_API_KEY"
                            value={settings.AI_FALLBACK_API_KEY}
                            onChange={handleChange}
                            placeholder="Optional (defaults to primary AI key)"
                            style={{ padding: '0.5rem', background: '#222', border: '1px solid #444', color: 'white' }}
                        />

                        <label>Fallback Model Name</label>
                        <input
                            type="text"
                            name="AI_FALLBACK_MODEL"
                            value={settings.AI_FALLBACK_MODEL}
                            onChange={handleChange}
                            placeholder="Optional (defaults to primary model)"
                            style={{ padding: '0.5rem', background: '#222', border: '1px solid #444', color: 'white' }}
                        />
                    </div>
                    <div style={{ marginTop: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <button
                            type="button"
                            onClick={() => saveSettings('AI Fallback')}
                            disabled={saving}
                            style={{ padding: '0.4rem 0.8rem', fontSize: '0.9rem', borderRadius: '4px', border: 'none', background: '#e5a00d', color: 'black', cursor: 'pointer' }}
                        >
                            {saving ? 'Saving...' : 'Save AI Fallback'}
                        </button>
                    </div>
                </section>

                <section>
                    <h3>TMDb Configuration</h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                        <p style={{ fontSize: '0.85rem', color: '#cbd5f5' }}>
                            TMDb is used for fetching posters and titles for recommended items.
                        </p>
                        <label>API Key</label>
                        <input
                            type="password"
                            name="TMDB_API_KEY"
                            value={settings.TMDB_API_KEY}
                            onChange={handleChange}
                            placeholder="TMDb API Key"
                            style={{ padding: '0.5rem', background: '#222', border: '1px solid #444', color: 'white' }}
                        />
                    </div>
                    <div style={{ marginTop: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <button
                            type="button"
                            onClick={() => saveSettings('TMDb')}
                            disabled={saving}
                            className="btn btn-primary"
                        >
                            {saving ? 'Saving...' : 'Save TMDb'}
                        </button>
                        <button
                            type="button"
                            onClick={() => runTest('tmdb')}
                            disabled={testing.tmdb}
                            className="btn btn-secondary"
                        >
                            {testing.tmdb ? 'Testing...' : 'Test TMDb'}
                        </button>
                        {testMessages.tmdb && (
                            <span style={{ fontSize: '0.85rem', color: '#e5e5e5' }}>{testMessages.tmdb}</span>
                        )}
                    </div>
                </section>

                <button
                    type="submit"
                    disabled={saving}
                    className="btn btn-primary btn-block"
                    style={{ marginTop: '1rem', fontSize: '1.1rem', padding: '1rem' }}
                >
                    {saving ? 'Saving...' : 'Save Settings'}
                </button>
            </form>
        </div>
    )
}

export default AdminSettings
