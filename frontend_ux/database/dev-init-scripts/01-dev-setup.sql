-- Development database initialization with sample data
-- Connect to the database
\c brant_roofing;

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Set timezone
SET timezone = 'UTC';

-- Insert development users (passwords are hashed 'password123')
INSERT INTO users (email, password_hash, first_name, last_name, company, role) VALUES
('admin@dtroofing.com', '$2b$10$rQZ8kHp.TB.It.NuiNvxaOFvmj8UQjd4NXz5i7TZeOt7S6fV4Lm8m', 'Admin', 'User', 'DT Commercial Roofing', 'admin'),
('estimator@dtroofing.com', '$2b$10$rQZ8kHp.TB.It.NuiNvxaOFvmj8UQjd4NXz5i7TZeOt7S6fV4Lm8m', 'John', 'Estimator', 'DT Commercial Roofing', 'estimator'),
('demo@example.com', '$2b$10$rQZ8kHp.TB.It.NuiNvxaOFvmj8UQjd4NXz5i7TZeOt7S6fV4Lm8m', 'Demo', 'User', 'Demo Company', 'estimator')
ON CONFLICT (email) DO NOTHING;

-- Insert sample projects for development
INSERT INTO projects (user_id, name, client_name, client_address, square_footage, roof_type, project_status) VALUES
(1, 'Development Test Project', 'Test Client', '123 Test Street, Test City', 10000, 'TPO Membrane', 'draft'),
(2, 'Sample Warehouse', 'Sample Corp', '456 Sample Ave, Sample Town', 15000, 'EPDM', 'in_review'),
(2, 'Demo Office Building', 'Demo LLC', '789 Demo Blvd, Demo City', 8000, 'Modified Bitumen', 'completed')
ON CONFLICT DO NOTHING;
