import { useState, useEffect } from 'react'
import axios from 'axios'

function History() {
    const [history, setHistory] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        fetchHistory()
    }, [])

    const fetchHistory = async () => {
        try {
            setLoading(true)
            const res = await axios.get('/api/user/history')
            setHistory(res.data.history || [])
        } catch (err) {
            console.error(err)
            setError('Failed to load history')
        } finally {
            setLoading(false)
        }
    }

    const handleDelete = async (tmdbId) => {
        if (!confirm('Are you sure you want to remove this record?')) return
        try {
            await axios.delete(`/api/media/${tmdbId}/rate`)
            setHistory((prev) => prev.filter((item) => item.tmdb_id !== tmdbId))
        } catch (err) {
            console.error(err)
            alert('Failed to delete record')
        }
    }

    const handleRate = async (item, rating) => {
        try {
            // Optimistic update
            const newRating = rating === 'up' ? 1 : -1
            setHistory((prev) =>
                prev.map((i) => (i.tmdb_id === item.tmdb_id ? { ...i, rating: newRating } : i))
            )

            await axios.post(`/api/media/${item.tmdb_id}/rate`, {
                rating,
                media_type: item.media_type || 'movie'
            })
        } catch (err) {
            console.error(err)
            alert('Failed to update rating')
            fetchHistory() // Revert on error
        }
    }

    const getRatingLabel = (rating) => {
        if (rating === 2) return <span style={{ color: 'var(--sagarr-cyan)', fontWeight: 'bold' }}>Requested</span>
        if (rating === 1) return <span style={{ color: '#4ade80' }}>Liked</span>
        if (rating === -1) return <span style={{ color: '#f87171' }}>Disliked</span>
        return <span>Seen</span>
    }

    if (loading) return <div style={{ padding: '2rem' }}>Loading history...</div>
    if (error) return <div style={{ padding: '2rem', color: 'red' }}>{error}</div>

    return (
        <div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
            <h2 style={{ marginBottom: '2rem' }}>My History</h2>

            {history.length === 0 && <p>No history found.</p>}

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {history.map((item) => (
                    <div
                        key={`${item.tmdb_id}-${item.media_type}`}
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                            background: 'var(--bg-card)',
                            padding: '1rem',
                            borderRadius: '8px',
                            gap: '1rem'
                        }}
                    >
                        {item.poster_url ? (
                            <img
                                src={item.poster_url}
                                alt={item.title}
                                style={{ width: '50px', height: '75px', objectFit: 'cover', borderRadius: '4px' }}
                            />
                        ) : (
                            <div style={{ width: '50px', height: '75px', background: '#333', borderRadius: '4px' }} />
                        )}

                        <div style={{ flex: 1 }}>
                            <h4 style={{ margin: '0 0 0.5rem 0' }}>{item.title || `ID: ${item.tmdb_id}`}</h4>
                            <div style={{ fontSize: '0.9rem', color: 'var(--text-dim)' }}>
                                {new Date(item.created_at).toLocaleDateString()} • {item.media_type === 'tv' ? 'TV Series' : 'Movie'}
                            </div>
                        </div>

                        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                            <div style={{ minWidth: '80px', textAlign: 'center' }}>
                                {getRatingLabel(item.rating)}
                            </div>

                            <div style={{ display: 'flex', gap: '0.5rem' }}>
                                <button
                                    onClick={() => handleRate(item, 'up')}
                                    className={`btn ${item.rating === 1 ? 'btn-primary' : 'btn-ghost'}`}
                                    style={{ padding: '0.5rem' }}
                                    title="Like"
                                >
                                    👍
                                </button>
                                <button
                                    onClick={() => handleRate(item, 'down')}
                                    className={`btn ${item.rating === -1 ? 'btn-primary' : 'btn-ghost'}`}
                                    style={{ padding: '0.5rem' }}
                                    title="Dislike"
                                >
                                    👎
                                </button>
                                <button
                                    onClick={() => handleDelete(item.tmdb_id)}
                                    className="btn btn-ghost"
                                    style={{ padding: '0.5rem', color: '#f87171', borderColor: '#f87171' }}
                                    title="Delete"
                                >
                                    🗑️
                                </button>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}

export default History
