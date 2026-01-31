# Frontend Setup Guide

This is the React frontend application that connects to the backend API.

## Prerequisites

You need Node.js and npm installed. Check your versions:
```bash
node --version
npm --version
```

**If you don't have Node.js:**
- Download from https://nodejs.org/ (download the LTS version)
- This automatically installs npm as well

## Installation (Local Development)

### Step 1: Navigate to the frontend directory
```bash
cd frontend
```

### Step 2: Install dependencies
```bash
npm install
```

This installs React, Vite, and other dependencies listed in `package.json`. It creates a `node_modules` folder (~400MB).

**This might take 2-5 minutes.** Get some water!

### Step 3: Make sure the backend is running

Before starting the frontend, you need the backend running. In a **separate terminal**:

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python app.py
```

You should see: `Running on http://127.0.0.1:5000`

### Step 4: Start the frontend development server

In the frontend directory:
```bash
npm run dev
```

You should see something like:
```
VITE v5.0.0  ready in 123 ms

➜  Local:   http://localhost:3000/
```

Open http://localhost:3000 in your browser.

## What You'll See

The frontend shows:
- **Backend Status**: Green box if backend is connected, red if not
- **Add Data Form**: Input fields to add new entries
- **Sample Data**: List of all data from the database

Try adding data in the form—it should appear in the list below!

## File Structure

```
frontend/
├── src/
│   ├── App.jsx          # Main React component (the main page)
│   ├── App.css          # Styles for the app
│   ├── index.css        # Global styles
│   ├── main.jsx         # Entry point (don't touch this usually)
├── public/              # Static files (doesn't exist yet, create if needed)
├── package.json         # Node dependencies
├── vite.config.js       # Vite configuration
├── index.html           # HTML page template
├── .dockerignore        # Files to ignore when building Docker image
└── README.md           # This file
```

## Understanding the Code

### App.jsx Structure

```javascript
function App() {
  // State: variables that React watches
  const [health, setHealth] = useState(null)    // Backend health status
  const [data, setData] = useState([])          // List of data from DB
  
  // Functions that call the backend API
  const checkHealth = async () => { ... }       // Tests if backend is up
  const fetchData = async () => { ... }         // Gets data from backend
  const handleSubmit = async (e) => { ... }     // Sends new data to backend
  
  // JSX: the HTML-like code that renders
  return (
    <div className="App">
      {/* Displays health status */}
      {/* Form to add data */}
      {/* List of data */}
    </div>
  )
}
```

## Making Changes

### Changing the text/layout
Edit `frontend/src/App.jsx`:
- Change heading: Find `<h1>🚀 Hackathon Starter</h1>` and modify
- Change form labels: Edit the `<input>` elements

### Changing colors/styles
Edit `frontend/src/App.css`:
- Modify colors like `#282c34` or `#61dafb`
- Adjust padding, margin, font sizes, etc.

### Adding new API calls
Edit `frontend/src/App.jsx`:
1. Add a new `useState` for your data
2. Create a function that calls `fetch('http://backend:5000/your-endpoint')`
3. Call it in `useEffect` or a button click handler
4. Display the results in the JSX

Example:
```javascript
const [users, setUsers] = useState([])

const fetchUsers = async () => {
  const response = await fetch('http://backend:5000/api/users')
  const result = await response.json()
  setUsers(result)
}

// In the JSX:
<div>
  <button onClick={fetchUsers}>Load Users</button>
  {users.map(user => <p key={user.id}>{user.name}</p>)}
</div>
```

## Available Commands

```bash
npm run dev      # Start development server (what you'll use most)
npm run build    # Build for production (creates optimized files)
npm run preview  # Preview the production build
```

## Hot Reload

The best part about `npm run dev`: **changes appear instantly in your browser!**

1. Edit `App.jsx` or `App.css`
2. Save the file (Ctrl+S or Cmd+S)
3. Browser updates automatically

No need to restart anything!

## Connecting to Different Backend

By default, the app tries to reach `http://backend:5000` (used in Docker).

For local development, you might need to change this. In `App.jsx`, find all lines with:
```javascript
fetch('http://backend:5000/...')
```

And change to:
```javascript
fetch('http://localhost:5000/...')
```

Actually, localhost should work! But if you changed the backend port to 5001, change it here too.

## Common Issues

### "npm: command not found"
- Node.js is not installed
- Download from https://nodejs.org/

### "Cannot find module 'react'"
- Run `npm install` again
- Make sure you're in the `frontend` directory

### "Failed to fetch" or "Connection refused"
- Backend is not running
- In another terminal: `cd backend && python app.py`
- Or check it's running: `curl http://localhost:5000/health`

### "Port 3000 already in use"
- Another app is using port 3000
- In `vite.config.js`, change `port: 3000` to `port: 3001`

### Changes not showing up
- Hard refresh in browser: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
- Check the terminal for error messages (red text)

## Debugging

### Check what the backend is returning
Open DevTools in your browser:
- Right-click → Inspect
- Go to "Network" tab
- Make API calls and see responses

### Check React state
Install "React Developer Tools" browser extension (Chrome/Firefox)
- Right-click → Inspect
- Go to "Components" tab
- See all state variables and their values

## Next Steps

1. **Understand the API**: What endpoints does the backend have?
2. **Design your UI**: Sketch what your app should look like
3. **Create components**: Break the UI into React components
4. **Add API calls**: Connect components to backend
5. **Style it**: Make it look good with CSS

## Useful React Resources

- React Basics: https://react.dev/learn
- Hooks (useState, useEffect): https://react.dev/reference/react
- CSS-in-JS: Just use App.css for now, that's fine!

## Running with Docker

If you want to run everything with Docker instead:
```bash
cd ..  # Go back to root
docker-compose up
```

This starts frontend on http://localhost:3000 automatically.
