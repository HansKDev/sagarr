import MediaCard from './MediaCard'

function RecommendationRow({ category, onRated }) {
  if (!category.items || category.items.length === 0) {
    return null
  }

  const hasSinceYouLikedReason =
    typeof category.reason === 'string' &&
    category.reason.toLowerCase().startsWith('since you liked')

  return (
    <section className={`recommendation-row${hasSinceYouLikedReason ? ' recommendation-row--tight' : ''}`}>
      <header className="recommendation-row-header">
        <h3>{category.title}</h3>
        {category.reason && <p className="recommendation-row-reason">{category.reason}</p>}
      </header>
      <div className="recommendation-row-scroll">
        {category.items
          .filter((item) => item.title && item.title !== 'Unknown title')
          .map((item) => (
            <MediaCard key={item.tmdb_id} item={item} onRated={onRated} />
          ))}
      </div>
    </section>
  )
}

export default RecommendationRow
