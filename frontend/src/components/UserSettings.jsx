import { useState, useEffect } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'

function UserSettings() {
    const [settings, setSettings] = useState({ date_cutoff: '' })
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
            const res = await axios.get('/api/user/settings', {
                headers: { Authorization: `Bearer ${token}` }
            })
            setSettings(res.data)
            setLoading(false)
        } catch (err) {
            console.error(err)
            setMessage('Failed to load settings.')
            setLoading(false)
        }
    }

    const handleSave = async (e) => {
        e.preventDefault()
        setSaving(true)
        setMessage('')
        try {
            const token = localStorage.getItem('token')
            // Convert date_cutoff to int or null
            const payload = {
                date_cutoff: settings.date_cutoff ? parseInt(settings.date_cutoff) : null
            }

            await axios.post('/api/user/settings', payload, {
                headers: { Authorization: `Bearer ${token}` }
            })
            setMessage('Settings saved successfully!')
        } catch (err) {
            console.error(err)
            setMessage('Failed to save settings.')
        } finally {
            setSaving(false)
        }
    }

    if (loading) return <div style={{ padding: '2rem' }}>Loading...</div>

    return (
        <div style={{ padding: '2rem', maxWidth: '600px', margin: '0 auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <h2>User Settings</h2>
                <button onClick={() => navigate('/')} className="btn btn-ghost">Back to Dashboard</button>
            </div>

            {message && <div style={{ padding: '1rem', background: '#333', marginBottom: '1rem', borderRadius: '4px' }}>{message}</div>}

            <form onSubmit={handleSave} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                <section style={{ background: 'var(--bg-card)', padding: '1.5rem', borderRadius: '8px' }}>
                    <h3 style={{ marginTop: 0 }}>AI Search Preferences</h3>
                    <p style={{ color: 'var(--text-dim)', fontSize: '0.9rem' }}>
                        Customize how the AI generates recommendations for you.
                    </p>

                    <div style={{ marginTop: '1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                        <label htmlFor="date_cutoff">Date Cutoff (Year)</label>
                        <p style={{ margin: 0, fontSize: '0.8rem', color: 'var(--text-dim)' }}>
                            Only recommend content released after this year. Leave empty for no limit.
                        </p>
                        <input
                            type="number"
                            id="date_cutoff"
                            value={settings.date_cutoff || ''}
                            onChange={(e) => setSettings({ ...settings, date_cutoff: e.target.value })}
                            placeholder="e.g. 1990"
                            style={{ padding: '0.75rem', background: 'rgba(255,255,255,0.05)', border: '1px solid var(--border-color)', color: 'white', borderRadius: '4px' }}
                        />
                    </div>
                </section>

                <button
                    type="submit"
                    disabled={saving}
                    className="btn btn-primary"
                    style={{ padding: '1rem' }}
                >
                    {saving ? 'Saving...' : 'Save Preferences'}
                </button>
            </form>
        </div>
    )
}

export default UserSettings
