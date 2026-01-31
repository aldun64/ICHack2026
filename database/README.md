# Database Setup Guide

This is the PostgreSQL database that stores all your application data.

## Quick Start (Using Docker - Easiest)

If you're running everything with Docker Compose, the database is set up automatically:

```bash
cd ..
docker-compose up
```

Skip to "Connecting to the Database" section below.

## Local Installation

### Prerequisites

You need PostgreSQL installed. Check if you have it:
```bash
psql --version
```

### Install PostgreSQL

**Mac (using Homebrew):**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Windows:**
1. Download from https://www.postgresql.org/download/windows/
2. Run the installer
3. Remember the password you set for the `postgres` user

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

## Creating the Database

### Step 1: Connect to PostgreSQL as admin
```bash
psql -U postgres
```

On Windows, you might need:
```bash
"C:\Program Files\PostgreSQL\15\bin\psql" -U postgres
```

### Step 2: Create the database user
```sql
CREATE USER hackathon_user WITH PASSWORD 'hackathon_password';
```

### Step 3: Create the database
```sql
CREATE DATABASE hackathon_db OWNER hackathon_user;
```

### Step 4: Exit psql
```sql
\q
```

### Step 5: Initialize tables
```bash
psql -U hackathon_user -d hackathon_db -f database/init.sql
```

## Connecting to the Database

### Using psql (command line)
```bash
psql -U hackathon_user -d hackathon_db
```

Common commands:
```sql
\dt              -- List all tables
\d sample_data   -- Describe the sample_data table
SELECT * FROM sample_data;  -- View all data
\q              -- Quit
```

### Using a GUI (DBeaver - Recommended for beginners)
1. Download DBeaver Community: https://dbeaver.io/
2. Create new connection → PostgreSQL
3. Enter credentials:
   - Host: localhost
   - Port: 5432
   - Database: hackathon_db
   - Username: hackathon_user
   - Password: hackathon_password
4. Click "Test Connection" → "Finish"

## Database Structure

Currently, there's one table: `sample_data`

```sql
CREATE TABLE sample_data (
  id SERIAL PRIMARY KEY,              -- Auto-incrementing ID
  name VARCHAR(255) NOT NULL,         -- Text field, required
  description TEXT,                   -- Longer text field, optional
  created_at TIMESTAMP DEFAULT NOW()  -- Creation time (automatic)
);
```

## Modifying the Database

### Adding a new table

Edit `database/init.sql`:

```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  username VARCHAR(100) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Then run:
```bash
psql -U hackathon_user -d hackathon_db -f database/init.sql
```

### Adding a column to existing table

```bash
psql -U hackathon_user -d hackathon_db
```

Then:
```sql
ALTER TABLE sample_data ADD COLUMN status VARCHAR(50) DEFAULT 'active';
\q
```

### Deleting everything and starting fresh

⚠️ This will delete all data!

```bash
psql -U postgres -c "DROP DATABASE hackathon_db;"
psql -U postgres -c "CREATE DATABASE hackathon_db OWNER hackathon_user;"
psql -U hackathon_user -d hackathon_db -f database/init.sql
```

## Sample Data

The `init.sql` file automatically inserts sample data:

```sql
INSERT INTO sample_data (name, description) VALUES 
  ('Example 1', 'This is the first example entry'),
  ('Example 2', 'This is the second example entry');
```

You can query it:
```bash
psql -U hackathon_user -d hackathon_db -c "SELECT * FROM sample_data;"
```

## Backing Up Your Data

### Create a backup
```bash
pg_dump -U hackathon_user -d hackathon_db > backup.sql
```

### Restore from backup
```bash
psql -U hackathon_user -d hackathon_db < backup.sql
```

## Common Issues

### "FATAL: role 'hackathon_user' does not exist"
- You haven't created the user yet
- Run: `psql -U postgres -c "CREATE USER hackathon_user WITH PASSWORD 'hackathon_password';"`

### "FATAL: database 'hackathon_db' does not exist"
- You haven't created the database yet
- Run: `psql -U postgres -c "CREATE DATABASE hackathon_db OWNER hackathon_user;"`

### "Connection refused"
- PostgreSQL is not running
- Mac: `brew services start postgresql@15`
- Linux: `sudo systemctl start postgresql`
- Windows: Start PostgreSQL service in Services app

### "Password authentication failed"
- Check your password in the connection string
- Default: `hackathon_password`
- If you forgot, you can reset it:
```bash
psql -U postgres -c "ALTER USER hackathon_user WITH PASSWORD 'hackathon_password';"
```

## File Structure

```
database/
├── init.sql         # SQL script that creates tables and sample data
└── README.md       # This file
```

## Backend Connection

The backend (Flask) connects using these environment variables:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=hackathon_db
DB_USER=hackathon_user
DB_PASSWORD=hackathon_password
```

If you change the database name, user, or password, update:
1. `database/init.sql` (if changing user/db name)
2. `backend/.env` (environment variables)
3. `docker-compose.yml` (if using Docker)

## SQL Basics for Your Team

### Create a new table
```sql
CREATE TABLE your_table_name (
  id SERIAL PRIMARY KEY,
  column_name VARCHAR(255),
  another_column INTEGER
);
```

### Insert data
```sql
INSERT INTO your_table_name (column_name, another_column) 
VALUES ('value1', 42);
```

### Select/view data
```sql
SELECT * FROM your_table_name;
SELECT column_name FROM your_table_name WHERE id = 1;
```

### Update data
```sql
UPDATE your_table_name SET column_name = 'new_value' WHERE id = 1;
```

### Delete data
```sql
DELETE FROM your_table_name WHERE id = 1;
```

## Useful Resources

- PostgreSQL Official Docs: https://www.postgresql.org/docs/
- SQL Tutorial: https://www.w3schools.com/sql/
- PostgreSQL Cheat Sheet: https://postgrescheatsheet.com/

## Next Steps

1. **Plan your schema**: What tables and columns do you need?
2. **Update init.sql**: Add your table definitions
3. **Test connections**: Make sure backend can read/write data
4. **Add indexes**: For frequently queried columns (advanced)
