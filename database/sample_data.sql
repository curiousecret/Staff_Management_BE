-- Sample Data for Staff Management Backend
-- PostgreSQL Database
-- Run this script AFTER creating the schema with schema.sql

-- ============================================
-- WARNING: This is sample data for testing only
-- DO NOT use in production environments
-- ============================================

-- Clear existing data (if any)
TRUNCATE TABLE token_blacklist CASCADE;
TRUNCATE TABLE refresh_tokens CASCADE;
TRUNCATE TABLE staff CASCADE;
TRUNCATE TABLE users CASCADE;

-- Reset sequences
ALTER SEQUENCE users_id_seq RESTART WITH 1;
ALTER SEQUENCE staff_id_seq RESTART WITH 1;
ALTER SEQUENCE token_blacklist_id_seq RESTART WITH 1;
ALTER SEQUENCE refresh_tokens_id_seq RESTART WITH 1;

-- ============================================
-- Sample Users
-- ============================================
-- NOTE: All passwords are hashed using bcrypt
-- Plain text passwords are documented in comments for testing purposes

INSERT INTO users (username, hashed_password, created_at, updated_at) VALUES
-- Username: admin, Password: admin0000
('admin', '$2b$12$3X6rju3PCjZSTywnWK5aeOZcAZCq.ORiy1KM351nLwzoy.jYEwk0y', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

-- ============================================
-- Sample Staff Records
-- ============================================

INSERT INTO staff (staff_id, name, dob, salary, status, created_at, updated_at) VALUES
-- Active Staff Members
('STF001', 'John Smith', '1990-05-15', 75000.00, 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('STF002', 'Sarah Johnson', '1988-08-22', 82000.00, 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('STF003', 'Michael Chen', '1992-03-10', 68000.00, 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('STF004', 'Emily Davis', '1995-11-30', 71000.00, 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('STF005', 'Robert Wilson', '1987-07-18', 95000.00, 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('STF006', 'Jessica Martinez', '1993-02-25', 73000.00, 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('STF007', 'David Brown', '1991-09-12', 79000.00, 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('STF008', 'Amanda Taylor', '1994-06-08', 70000.00, 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('STF009', 'Christopher Lee', '1989-12-20', 88000.00, 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('STF010', 'Jennifer White', '1996-04-15', 65000.00, 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

-- Inactive Staff Members
('STF011', 'Thomas Anderson', '1985-01-05', 92000.00, 'inactive', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('STF012', 'Lisa Moore', '1990-10-30', 67000.00, 'inactive', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('STF013', 'James Garcia', '1988-08-14', 74000.00, 'inactive', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);



-- Verify users inserted
SELECT 'Users:' as table_name, COUNT(*) as record_count FROM users
UNION ALL
SELECT 'Staff:', COUNT(*) FROM staff
UNION ALL
SELECT 'Active Staff:', COUNT(*) FROM staff WHERE status = 'active'
UNION ALL
SELECT 'Inactive Staff:', COUNT(*) FROM staff WHERE status = 'inactive';

-- Display sample users (excluding passwords)
SELECT id, username, created_at FROM users ORDER BY id;

-- Display sample staff
SELECT staff_id, name, dob, salary, status FROM staff ORDER BY staff_id;

-- ============================================
-- Test Credentials Summary
-- ============================================
/*
For testing the application, use these credentials:

1. Admin User:
   Username: admin
   Password: admin0000
*/
