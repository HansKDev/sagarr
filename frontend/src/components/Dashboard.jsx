import { useState, useEffect } from 'react'
import axios from 'axios'
import RecommendationRow from './RecommendationRow'

function Dashboard() {
  const [health, setHealth] = useState(null)
  const [categories, setCategories] = useState([])
  const [loadingRecs, setLoadingRecs] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    axios.get('/api/health')
      .then((res) => setHealth(res.data))
      .catch((err) => console.error(err))
  }, [])

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        setLoadingRecs(true)
        setError(null)
        const res = await axios.get('/api/recommendations')
        setCategories(res.data.categories || [])
      } catch (err) {
        console.error(err)
        setError('Failed to load recommendations')
      } finally {
        setLoadingRecs(false)
      }
    }

    fetchRecommendations()
  }, [])

  const handleRated = (tmdbId) => {
    setCategories((prev) =>
      prev.map((cat) => ({
        ...cat,
        items: cat.items.filter((item) => item.tmdb_id !== tmdbId),
      })),
    )
  }

  return (
    <div className="dashboard">
      <h2>Dashboard</h2>

      <div className="card">
        <h3>Backend Status</h3>
        <pre>{JSON.stringify(health, null, 2)}</pre>
      </div>

      <div style={{ marginTop: '2rem', textAlign: 'left' }}>
        <h3>Recommendations</h3>
        {loadingRecs && <p>Loading recommendations...</p>}
        {error && <p style={{ color: 'red' }}>{error}</p>}
        {!loadingRecs && !error && categories.length === 0 && (
          <p>No recommendations yet. They will appear here once generated.</p>
        )}

        {categories.map((category) => (
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
