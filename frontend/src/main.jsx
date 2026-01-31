import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import UsernameVerification from './UsernameVerification'
import Scheduling from './Scheduling'
import './index.css'

// Simple routing based on URL path
const path = window.location.pathname
const isScheduling = path.includes('/schedule')
const isVerification = path.includes('/verify')

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    {isVerification ? <UsernameVerification /> : isScheduling ? <Scheduling /> : <App />}
  </React.StrictMode>,
)
