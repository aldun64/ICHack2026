# Backend Setup Guide

This is the Python Flask backend that provides API endpoints for the frontend.

## Prerequisites

You need Python 3.11 or higher. Check your version:
```bash
python3 --version
```

If you don't have Python installed, download it from https://www.python.org/downloads/

## Installation (Local Development)

### Step 1: Navigate to the backend directory
```bash
cd backend
```

### Step 2: Create a Python virtual environment
A virtual environment keeps your project dependencies isolated from other projects.

**On Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` in your terminal after activation.

### Step 3: Install dependencies
```bash
pip install -r requirements.txt
```

This installs:
- Flask (web framework)
- Flask-CORS (allows frontend to communicate with backend)
- psycopg2-binary (PostgreSQL database driver)
- python-dotenv (environment variable management)

### Step 4: Set up environment variables

Create a file named `.env` in the backend directory:
```bash
touch .env
```

Add these lines to `.env`:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=hackathon_db
DB_USER=hackathon_user
DB_PASSWORD=hackathon_password
FLASK_ENV=development
```

### Step 5: Make sure PostgreSQL is running

**Option A: Using Docker** (Recommended for local development)
```bash
docker run --name postgres_dev -e POSTGRES_USER=hackathon_user -e POSTGRES_PASSWORD=hackathon_password -e POSTGRES_DB=hackathon_db -p 5432:5432 -d postgres:15-alpine
```

**Option B: Install PostgreSQL locally**
- Mac: `brew install postgresql@15`
- Windows: Download from https://www.postgresql.org/download/windows/
- Linux: `sudo apt-get install postgresql`

Then create the database:
```bash
psql -U postgres -c "CREATE USER hackathon_user WITH PASSWORD 'hackathon_password';"
psql -U postgres -c "CREATE DATABASE hackathon_db OWNER hackathon_user;"
psql -U hackathon_user -d hackathon_db -f ../database/init.sql
```

### Step 6: Run the backend server
```bash
python app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
```

## Testing the Backend

### Health Check
```bash
curl http://localhost:5000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

### Get all data
```bash
curl http://localhost:5000/api/data
```

### Add new data
```bash
curl -X POST http://localhost:5000/api/data \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Item","description":"This is a test"}'
```

## Project Structure

```
backend/
├── app.py                 # Main Flask application with all routes
├── requirements.txt       # Python dependencies list
├── Dockerfile            # For running in Docker
├── .dockerignore         # Files to ignore when building Docker image
├── .env                  # Environment variables (create this yourself)
└── README.md            # This file
```

## Available Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/health` | Check if backend and database are working |
| GET | `/api/data` | Get all entries from the sample_data table |
| POST | `/api/data` | Create a new entry (send JSON with `name` and `description`) |

## Common Issues

### "ModuleNotFoundError: No module named 'flask'"
- Make sure you activated the virtual environment: `source venv/bin/activate` (Mac/Linux) or `venv\Scripts\activate` (Windows)
- Run `pip install -r requirements.txt` again

### "Connection refused" when accessing database
- Make sure PostgreSQL is running
- Check that DB_HOST, DB_PORT, DB_USER, DB_PASSWORD in `.env` are correct

### "Database does not exist"
- Run the init.sql script: `psql -U hackathon_user -d hackathon_db -f ../database/init.sql`

### "Address already in use"
- Port 5000 is being used by another application
- Change the port in `app.py` line: `app.run(host='0.0.0.0', port=5000, debug=True)` to a different port like 5001

## Deactivating the Virtual Environment

When you're done working, deactivate the virtual environment:
```bash
deactivate
```

## Running with Docker

Instead of local setup, you can run the entire stack with Docker:
```bash
cd .. # Go back to root directory
docker-compose up
```

## Next Steps

Once the backend is running:
1. Test all endpoints with curl or Postman
2. Modify `app.py` to add more routes for your hackathon project
3. Update `database/init.sql` to create tables matching your needs
