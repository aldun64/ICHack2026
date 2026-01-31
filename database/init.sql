-- Discord Users table
CREATE TABLE IF NOT EXISTS discord_users (
  id SERIAL PRIMARY KEY,
  discord_id BIGINT UNIQUE NOT NULL,
  username VARCHAR(255) NOT NULL,
  display_name VARCHAR(255),
  avatar_url TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Socials/Events table
CREATE TABLE IF NOT EXISTS socials (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  location VARCHAR(255),
  event_date TIMESTAMP,
  created_by BIGINT REFERENCES discord_users(discord_id),
  status VARCHAR(50) DEFAULT 'planned', -- planned, ongoing, completed, cancelled
  group_points INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Social Attendance table (tracking who said they will come and actual attendance)
CREATE TABLE IF NOT EXISTS social_attendance (
  id SERIAL PRIMARY KEY,
  social_id INT REFERENCES socials(id) ON DELETE CASCADE,
  discord_id BIGINT REFERENCES discord_users(discord_id),
  rsvp_status VARCHAR(50) DEFAULT 'attending', -- attending, maybe, not_attending
  actual_attended BOOLEAN DEFAULT FALSE,
  availability_submitted BOOLEAN DEFAULT FALSE,
  -- availability_slots: JSON array of available time slots (format: [{date: "2025-01-31", times: ["10:00", "14:00"]}, ...])
  availability_slots JSONB,
  rsvp_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(social_id, discord_id)
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_socials_status ON socials(status);
CREATE INDEX IF NOT EXISTS idx_socials_event_date ON socials(event_date);
CREATE INDEX IF NOT EXISTS idx_attendance_social ON social_attendance(social_id);
CREATE INDEX IF NOT EXISTS idx_attendance_user ON social_attendance(discord_id);

-- Seed data: Users
INSERT INTO discord_users (discord_id, username, display_name)
VALUES
  (123456789, 'alice', 'Alice'),
  (987654321, 'bob', 'Bob'),
  (555444333, 'charlie', 'Charlie')
ON CONFLICT (discord_id) DO NOTHING;

-- Seed data: Socials/Events
INSERT INTO socials (name, description, location, event_date, created_by, status, group_points)
VALUES
  ('Coffee Meetup', 'Casual coffee hangout to catch up and chat', 'Downtown Cafe', '2025-02-07 10:00:00', 123456789, 'planned', 0),
  ('Brunch Party', 'Sunday brunch with the crew at the new brunch spot', 'Riverside Brunch Spot', '2025-02-09 11:00:00', 987654321, 'planned', 0),
  ('Game Night', 'Board games and video games night', 'Alice''s Place', '2025-02-15 19:00:00', 555444333, 'planned', 0)
ON CONFLICT DO NOTHING;
