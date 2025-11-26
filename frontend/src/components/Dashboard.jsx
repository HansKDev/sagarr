import { useState, useEffect } from 'react'
import axios from 'axios'
import RecommendationRow from './RecommendationRow'

function Dashboard() {
  const [data, setData] = useState({ movies: [], tv: [], documentaries: [] })
  const [activeTab, setActiveTab] = useState('movies') // 'movies' | 'tv' | 'documentaries'
  const [loadingRecs, setLoadingRecs] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        setLoadingRecs(true)
        setError(null)
        const res = await axios.get('/api/recommendations')
        // Handle both legacy and new formats gracefully
        const movies = res.data.movies || res.data.categories || []
        const tv = res.data.tv || []
        const documentaries = res.data.documentaries || []
        setData({ movies, tv, documentaries })
      } catch (err) {
        console.error(err)
        if (err.response && err.response.status === 401) {
          // Token expired or invalid, force logout
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          window.location.href = '/login'
          return
        }
        setError('Failed to load recommendations')
      } finally {
        setLoadingRecs(false)
      }
    }

    fetchRecommendations()
  }, [])

  const handleRated = (tmdbId) => {
    // Remove item from the active list
    setData((prev) => ({
      ...prev,
      [activeTab]: prev[activeTab].map((cat) => ({
        ...cat,
        items: cat.items.filter((item) => item.tmdb_id !== tmdbId),
      })),
    }))
  }

  const activeCategories = data[activeTab] || []

  return (
    <div className="dashboard">
      <div style={{ textAlign: 'left' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <h2 style={{ margin: 0, color: 'var(--text-light)' }}>Your Recommendations</h2>

          <div style={{ display: 'flex', gap: '0.5rem', background: 'var(--bg-card)', padding: '0.25rem', borderRadius: '8px' }}>
            <button
              onClick={() => setActiveTab('movies')}
              className={activeTab === 'movies' ? 'btn btn-primary' : 'btn btn-ghost'}
              style={{ fontSize: '0.9rem', padding: '0.4rem 1rem' }}
            >
              Movies
            </button>
            <button
              onClick={() => setActiveTab('tv')}
              className={activeTab === 'tv' ? 'btn btn-primary' : 'btn btn-ghost'}
              style={{ fontSize: '0.9rem', padding: '0.4rem 1rem' }}
            >
              TV Series
            </button>
            <button
              onClick={() => setActiveTab('documentaries')}
              className={activeTab === 'documentaries' ? 'btn btn-primary' : 'btn btn-ghost'}
              style={{ fontSize: '0.9rem', padding: '0.4rem 1rem' }}
            >
              Docs
            </button>
          </div>
        </div>

        {loadingRecs && <p>Loading recommendations...</p>}
        {error && <p style={{ color: 'red' }}>{error}</p>}

        {!loadingRecs && !error && activeCategories.length === 0 && (
          <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-dim)' }}>
            <p>No {activeTab === 'movies' ? 'movie' : activeTab === 'tv' ? 'TV' : 'documentary'} recommendations found.</p>
            <p style={{ fontSize: '0.9rem' }}>Try watching more content or check back later!</p>
          </div>
        )}

        {activeCategories.map((category) => (
          <RecommendationRow
            key={category.title}
            category={category}
            onRated={handleRated}
          />
        ))}
      </div>
    </div>
  )
}

export default Dashboard
