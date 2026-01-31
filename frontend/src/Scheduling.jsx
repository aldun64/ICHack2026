import { useState, useEffect } from 'react'
import './Scheduling.css'

function Scheduling() {
  const [socialId, setSocialId] = useState(null)
  const [username, setUsername] = useState('')
  const [discordId, setDiscordId] = useState(null)
  const [selectedDates, setSelectedDates] = useState({})
  const [loading, setLoading] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const [social, setSocial] = useState(null)
  const [error, setError] = useState(null)

  // Get social ID, username, and discord_id from URL query params
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const id = params.get('social_id')
    const user = params.get('username')
    const did = params.get('discord_id')

    if (!id || !user || !did) {
      setError('Invalid link. Please start from the beginning.')
      return
    }

    setSocialId(parseInt(id))
    setUsername(user)
    setDiscordId(parseInt(did))
    fetchSocial(parseInt(id))
  }, [])

  const fetchSocial = async (id) => {
    try {
      const response = await fetch(`http://localhost:5000/api/socials/${id}`)
      if (!response.ok) {
        setError('Event not found')
        return
      }
      const data = await response.json()
      setSocial(data)
    } catch (err) {
      setError('Failed to load event details')
    }
  }

  const handleDateToggle = (dateStr, time) => {
    const key = `${dateStr}_${time}`
    setSelectedDates(prev => ({
      ...prev,
      [key]: !prev[key]
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    setLoading(true)
    setError(null)

    try {
      // Process selected dates into the availability format
      const availabilitySlots = {}
      Object.entries(selectedDates).forEach(([key, isSelected]) => {
        if (isSelected) {
          const [dateStr, time] = key.split('_')
          if (!availabilitySlots[dateStr]) {
            availabilitySlots[dateStr] = []
          }
          availabilitySlots[dateStr].push(time)
        }
      })

      const slotsArray = Object.entries(availabilitySlots).map(([date, times]) => ({
        date,
        times
      }))

      // Submit availability
      const response = await fetch(`http://localhost:5000/api/socials/${socialId}/availability`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username,
          discord_id: discordId,
          availability_slots: slotsArray
        })
      })

      if (!response.ok) {
        throw new Error('Failed to submit availability')
      }

      setSubmitted(true)
      setSelectedDates({})
    } catch (err) {
      setError(err.message || 'Failed to submit availability')
    } finally {
      setLoading(false)
    }
  }

  if (error && !social) {
    return (
      <div className="scheduling-container">
        <div className="error-message">
          <p>⚠️ {error}</p>
        </div>
      </div>
    )
  }

  if (!social) {
    return (
      <div className="scheduling-container">
        <p>Loading event...</p>
      </div>
    )
  }

  return (
    <div className="scheduling-container">
      <div className="scheduling-card">
        <h1>📅 Schedule Your Availability</h1>
        <h2>{social.name}</h2>

        {social.description && (
          <p className="event-description">{social.description}</p>
        )}

        {submitted ? (
          <div className="success-message">
            <p>✓ Your availability has been submitted!</p>
            <p className="small-text">Thanks for letting us know when you're available!</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            <div className="user-info">
              <p>Scheduling as: <strong>{username}</strong></p>
            </div>

            <div className="form-group">
              <label>Select Your Available Times</label>
              <div className="calendar-grid">
                {/* Example: Generate some dates around the event */}
                {generateDateOptions().map(({ date, timeSlots }) => (
                  <div key={date} className="date-section">
                    <h4>{formatDate(date)}</h4>
                    <div className="time-slots">
                      {timeSlots.map(time => {
                        const key = `${date}_${time}`
                        const isSelected = selectedDates[key]
                        return (
                          <button
                            key={key}
                            type="button"
                            className={`time-slot ${isSelected ? 'selected' : ''}`}
                            onClick={() => handleDateToggle(date, time)}
                          >
                            {time}
                          </button>
                        )
                      })}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {error && (
              <div className="error-message">
                <p>{error}</p>
              </div>
            )}

            <button
              type="submit"
              className="submit-btn"
              disabled={loading || Object.values(selectedDates).every(v => !v)}
            >
              {loading ? 'Submitting...' : 'Submit Availability'}
            </button>
          </form>
        )}
      </div>
    </div>
  )
}

// Helper function to generate date options
function generateDateOptions() {
  const dates = []
  const today = new Date()

  // Generate next 7 days
  for (let i = 0; i < 7; i++) {
    const date = new Date(today)
    date.setDate(date.getDate() + i)
    const dateStr = date.toISOString().split('T')[0]

    const timeSlots = [
      '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00'
    ]

    dates.push({ date: dateStr, timeSlots })
  }

  return dates
}

function formatDate(dateStr) {
  const date = new Date(dateStr + 'T00:00:00')
  return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })
}

export default Scheduling
