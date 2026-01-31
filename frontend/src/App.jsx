import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [health, setHealth] = useState(null)
  const [groupStats, setGroupStats] = useState(null)
  const [userStats, setUserStats] = useState(null)
  const [socials, setSocials] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedUserId, setSelectedUserId] = useState(123456789) // Alice by default

  useEffect(() => {
    checkHealth()
    fetchGroupStats()
    fetchUserStats(selectedUserId)
    fetchSocials()
  }, [])

  useEffect(() => {
    fetchUserStats(selectedUserId)
  }, [selectedUserId])

  const checkHealth = async () => {
    try {
      const response = await fetch('http://localhost:5000/health')
      const result = await response.json()
      setHealth(result)
    } catch (error) {
      console.error('Error checking health:', error)
      setHealth({ status: 'error', message: error.message })
    }
  }

  const fetchGroupStats = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/stats/group')
      const result = await response.json()
      setGroupStats(result)
    } catch (error) {
      console.error('Error fetching group stats:', error)
    }
  }

  const fetchUserStats = async (userId) => {
    try {
      const response = await fetch(`http://localhost:5000/api/stats/user/${userId}`)
      const result = await response.json()
      setUserStats(result)
    } catch (error) {
      console.error('Error fetching user stats:', error)
    }
  }

  const fetchSocials = async () => {
    try {
      setLoading(true)
      const response = await fetch('http://localhost:5000/api/socials')
      const result = await response.json()
      setSocials(result)
    } catch (error) {
      console.error('Error fetching socials:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>🎉 Group Chat Socials Tracker</h1>

        <div className="health-section">
          <h2>Backend Status</h2>
          {health ? (
            <div className={`health-badge ${health.status}`}>
              Status: {health.status}
              {health.database && ` | DB: ${health.database}`}
            </div>
          ) : (
            <p>Checking backend...</p>
          )}
        </div>

        <div className="metrics-section">
          <h2>📊 Group Metrics</h2>
          {groupStats ? (
            <div className="metrics-grid">
              <div className="metric-card">
                <h3>Total Group Points</h3>
                <p className="metric-value">{groupStats.total_group_points}</p>
              </div>
              <div className="metric-card">
                <h3>Completed Socials</h3>
                <p className="metric-value">{groupStats.completed_socials}</p>
              </div>
              <div className="metric-card">
                <h3>Upcoming Socials</h3>
                <p className="metric-value">{groupStats.upcoming_socials}</p>
              </div>
              <div className="metric-card">
                <h3>Total Attendances</h3>
                <p className="metric-value">{groupStats.total_attendances}</p>
              </div>
            </div>
          ) : (
            <p>Loading group metrics...</p>
          )}
        </div>

        <div className="user-metrics-section">
          <h2>👤 User Metrics</h2>
          <div className="user-selector">
            <label htmlFor="user-select">Select User: </label>
            <select
              id="user-select"
              value={selectedUserId}
              onChange={(e) => setSelectedUserId(Number(e.target.value))}
            >
              <option value={123456789}>Alice</option>
              <option value={987654321}>Bob</option>
              <option value={555444333}>Charlie</option>
            </select>
          </div>
          {userStats ? (
            <div className="metrics-grid">
              <div className="metric-card">
                <h3>Username</h3>
                <p className="metric-value">{userStats.username}</p>
              </div>
              <div className="metric-card">
                <h3>Total RSVPs</h3>
                <p className="metric-value">{userStats.total_rsvps}</p>
              </div>
              <div className="metric-card">
                <h3>Actually Attended</h3>
                <p className="metric-value">{userStats.attended}</p>
              </div>
              <div className="metric-card">
                <h3>Upcoming Events</h3>
                <p className="metric-value">{userStats.upcoming}</p>
              </div>
            </div>
          ) : (
            <p>Loading user metrics...</p>
          )}
        </div>

        <div className="socials-section">
          <h2>🎊 Events</h2>
          {loading ? (
            <p>Loading events...</p>
          ) : socials.length === 0 ? (
            <p>No events yet.</p>
          ) : (
            <div className="socials-list">
              {socials.map((social) => (
                <div key={social.id} className="social-card">
                  <div className="social-header">
                    <h3>{social.name}</h3>
                    <span className={`status-badge status-${social.status}`}>{social.status}</span>
                  </div>
                  <p className="social-description">{social.description}</p>
                  <div className="social-details">
                    <span>📍 {social.location || 'TBD'}</span>
                    <span>📅 {social.event_date ? new Date(social.event_date).toLocaleDateString() : 'TBD'}</span>
                    <span>⭐ {social.group_points} points</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </header>
    </div>
  )
}

export default App
