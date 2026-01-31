# Hackathon Starter Template

A complete starter template with Python backend, React frontend, PostgreSQL database, and Docker Compose orchestration.

## Tech Stack

- **Backend**: Python Flask
- **Frontend**: React with Vite
- **Database**: PostgreSQL
- **Orchestration**: Docker Compose

## Quick Start

### Prerequisites
- Docker and Docker Compose installed

### Running the Application

1. Start all services:
```bash
docker-compose up
```

2. Access the application:
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:5000
   - **Database**: localhost:5432

### Architecture

```
┌─────────────┐         ┌──────────────┐         ┌────────────┐
│   Frontend  │ ◄──────►│   Backend    │ ◄──────►│ PostgreSQL │
│   (React)   │         │  (Flask)     │         │     DB     │
│  Port 3000  │         │  Port 5000   │         │ Port 5432  │
└─────────────┘         └──────────────┘         └────────────┘
```

## API Endpoints

- `GET /health` - Health check endpoint
- `GET /api/data` - Get all data from sample_data table
- `POST /api/data` - Create new entry (JSON body: `{"name": "...", "description": "..."}`)

## File Structure

```
.
├── backend/
│   ├── app.py              # Flask application
│   ├── Dockerfile          # Backend Docker image
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.jsx        # Main React component
│   │   ├── App.css        # App styles
│   │   ├── index.css      # Global styles
│   │   └── main.jsx       # React entry point
│   ├── Dockerfile         # Frontend Docker image
│   ├── package.json       # Node dependencies
│   ├── vite.config.js     # Vite configuration
│   └── index.html         # HTML entry point
├── database/
│   └── init.sql           # Database initialization script
├── docker-compose.yml     # Docker Compose configuration
└── README.md             # This file
```

## Environment Variables

The services are pre-configured with default credentials. To customize:

Edit `docker-compose.yml`:
```yaml
environment:
  POSTGRES_USER: your_user
  POSTGRES_PASSWORD: your_password
  POSTGRES_DB: your_db
```

## Development

### Backend
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Database
Connect with:
```bash
psql -h localhost -U hackathon_user -d hackathon_db
```

## Troubleshooting

**Frontend can't reach backend?**
- Ensure the backend service is healthy: `docker-compose ps`
- Check logs: `docker-compose logs backend`

**Database connection failed?**
- Wait for database to be ready (check healthcheck): `docker-compose ps`
- Verify credentials match in backend environment variables

**Port already in use?**
- Change ports in docker-compose.yml (e.g., `"8000:5000"`)

## Next Steps

1. Replace `sample_data` table with your schema
2. Add authentication/authorization
3. Deploy to production using docker-compose or Kubernetes
4. Add more API endpoints as needed
5. Implement additional React components

Good luck with your hackathon! 🚀
