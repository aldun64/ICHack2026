import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [health, setHealth] = useState(null)
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')

  useEffect(() => {
    checkHealth()
    fetchData()
  }, [])

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

  const fetchData = async () => {
    try {
      setLoading(true)
      const response = await fetch('http://localhost:5000/api/data')
      const result = await response.json()
      setData(result)
    } catch (error) {
      console.error('Error fetching data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      const response = await fetch('http://localhost:5000/api/data', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, description })
      })
      if (response.ok) {
        setName('')
        setDescription('')
        fetchData()
      }
    } catch (error) {
      console.error('Error creating data:', error)
    }
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>🚀 Hackathon Starter</h1>
        
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

        <div className="form-section">
          <h2>Add Data</h2>
          <form onSubmit={handleSubmit}>
            <input
              type="text"
              placeholder="Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
            <input
              type="text"
              placeholder="Description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              required
            />
            <button type="submit">Submit</button>
          </form>
        </div>

        <div className="data-section">
          <h2>Sample Data</h2>
          {loading ? (
            <p>Loading...</p>
          ) : data.length === 0 ? (
            <p>No data yet. Add some above!</p>
          ) : (
            <ul>
              {data.map((item) => (
                <li key={item.id}>
                  <strong>{item.name}</strong>: {item.description}
                </li>
              ))}
            </ul>
          )}
        </div>
      </header>
    </div>
  )
}

export default App
