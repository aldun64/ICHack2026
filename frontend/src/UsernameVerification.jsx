import { useState, useEffect } from 'react'
import './UsernameVerification.css'

function UsernameVerification() {
  const [username, setUsername] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [socialId, setSocialId] = useState(null)

  // Get social ID from URL query params
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const id = params.get('social_id')
    if (id) {
      setSocialId(parseInt(id))
    } else {
      setError('No event specified in the link')
    }
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!username.trim()) {
      setError('Please enter your username')
      return
    }

    setLoading(true)
    setError(null)

    try {
      // Try to find the user
      const response = await fetch(`http://localhost:5000/api/users/by-username/${username}`)

      if (!response.ok) {
        setError('Username not found. Please check and try again.')
        setLoading(false)
        return
      }

      const userData = await response.json()

      // Redirect to scheduling page with verified username and social_id
      window.location.href = `/schedule?social_id=${socialId}&username=${encodeURIComponent(username)}&discord_id=${userData.discord_id}`
    } catch (err) {
      setError('Failed to verify username. Please try again.')
      setLoading(false)
    }
  }

  if (error && !socialId) {
    return (
      <div className="verification-container">
        <div className="error-message">
          <p>⚠️ {error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="verification-container">
      <div className="verification-card">
        <h1>📋 Join Event</h1>

        <div className="verification-content">
          <p className="subtitle">Enter your username to continue scheduling your availability</p>

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="username">Discord Username</label>
              <input
                id="username"
                type="text"
                placeholder="e.g., alice, bob, charlie"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                disabled={loading}
                autoFocus
              />
            </div>

            {error && (
              <div className="error-message">
                <p>{error}</p>
              </div>
            )}

            <button
              type="submit"
              className="submit-btn"
              disabled={loading || !username.trim()}
            >
              {loading ? 'Verifying...' : 'Continue'}
            </button>
          </form>

          <p className="help-text">
            Don't see your username? Contact an admin to be added to the group.
          </p>
        </div>
      </div>
    </div>
  )
}

export default UsernameVerification
