import { useEffect, useState } from 'react'
import axios from 'axios'

function MediaCard({ item, onRated }) {
  const [status, setStatus] = useState('unknown')
  const [loadingStatus, setLoadingStatus] = useState(false)
  const [showRating, setShowRating] = useState(false)
  const [submittingRating, setSubmittingRating] = useState(false)

  useEffect(() => {
    let cancelled = false
    const fetchStatus = async () => {
      try {
        setLoadingStatus(true)
        const res = await axios.get(`/api/media/${item.tmdb_id}/status`)
        if (!cancelled) {
          setStatus(res.data.status || 'unknown')
        }
      } catch (err) {
        console.error(err)
      } finally {
        if (!cancelled) {
          setLoadingStatus(false)
        }
      }
    }

    fetchStatus()
    return () => {
      cancelled = true
    }
  }, [item.tmdb_id])

  const handleRequest = async () => {
    try {
      await axios.post(`/api/media/${item.tmdb_id}/request`, { media_type: 'movie' })
      setStatus('requested')
    } catch (err) {
      console.error(err)
    }
  }

  const handleRate = async (rating) => {
    try {
      setSubmittingRating(true)
      await axios.post(`/api/media/${item.tmdb_id}/rate`, { rating })
      if (onRated) {
        onRated(item.tmdb_id)
      }
    } catch (err) {
      console.error(err)
    } finally {
      setSubmittingRating(false)
    }
  }

  const renderPrimaryAction = () => {
    if (loadingStatus) {
      return <button className="media-button" disabled>Loading...</button>
    }

    if (status === 'missing') {
      return (
        <button className="media-button" type="button" onClick={handleRequest}>
          Request
        </button>
      )
    }

    if (status === 'requested') {
      return (
        <button className="media-button media-button-muted" type="button" disabled>
          Requested
        </button>
      )
    }

    if (status === 'available') {
      return (
        <button className="media-button" type="button" disabled>
          Available
        </button>
      )
    }

    return (
      <button className="media-button media-button-muted" type="button" disabled>
        Status unknown
      </button>
    )
  }

  return (
    <div className="media-card">
      {item.poster_url && (
        <img
          src={item.poster_url}
          alt={item.title || 'Poster'}
          className="media-poster"
        />
      )}
      <div className="media-body">
        <h4 className="media-title">{item.title || 'Unknown title'}</h4>
        {item.overview && (
          <p className="media-overview">
            {item.overview.length > 160 ? `${item.overview.slice(0, 157)}...` : item.overview}
          </p>
        )}
      </div>
      <div className="media-actions">
        {renderPrimaryAction()}
        <button
          type="button"
          className="media-button-secondary"
          onClick={() => setShowRating((prev) => !prev)}
        >
          Seen it
        </button>
      </div>
      {showRating && (
        <div className="media-rating">
          <span>Did you like it?</span>
          <div className="media-rating-buttons">
            <button
              type="button"
              className="media-button"
              disabled={submittingRating}
              onClick={() => handleRate('up')}
            >
              👍
            </button>
            <button
              type="button"
              className="media-button"
              disabled={submittingRating}
              onClick={() => handleRate('down')}
            >
              👎
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default MediaCard

