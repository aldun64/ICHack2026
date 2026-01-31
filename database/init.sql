-- Create the sample_data table
CREATE TABLE IF NOT EXISTS sample_data (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO sample_data (name, description) VALUES 
  ('Example 1', 'This is the first example entry'),
  ('Example 2', 'This is the second example entry');
