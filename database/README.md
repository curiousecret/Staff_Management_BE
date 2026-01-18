# Database Setup Files

This directory contains SQL scripts for setting up the Staff Management Backend database.

## Files

### `schema.sql`
Creates all database tables, indexes, constraints, and triggers required for the application.

**What it creates:**
- `users` table - User authentication data
- `staff` table - Staff information records
- `refresh_tokens` table - JWT refresh token management
- `token_blacklist` table - Invalidated JWT tokens
- All necessary indexes for performance
- Triggers for automatic timestamp updates

**Usage:**
```sql
-- Run this in pgAdmin Query Tool or psql
\i schema.sql
```

### `sample_data.sql`
Inserts sample data for testing and development purposes.

**What it includes:**
- 4 test user accounts with bcrypt-hashed passwords
- 13 sample staff records (10 active, 3 inactive)
- Verification queries to check data insertion

**Usage:**
```sql
-- Run this AFTER schema.sql
\i sample_data.sql
```

**Test Credentials:**
- admin / admin123
- manager / manager123
- user1 / password123
- testuser / test123

## Setup Methods

### Method 1: Schema + Sample Data (Recommended for Development)

1. Create a new database in pgAdmin
2. Run `schema.sql` to create all tables
3. Run `sample_data.sql` to insert test data

### Method 2: Database Backup/Restore

To create a backup file:
1. Right-click on your database in pgAdmin
2. Select "Backup..."
3. Choose format: "Custom"
4. Save as `staff_management_backup.backup`
5. Include: Data, Schema, and Owner

To restore from backup:
1. Create an empty database
2. Right-click and select "Restore..."
3. Select your `.backup` file
4. Execute the restore

## Database Maintenance

### Cleanup Expired Tokens (Run Periodically)

```sql
-- Remove expired blacklisted tokens
DELETE FROM token_blacklist WHERE expires_at < CURRENT_TIMESTAMP;

-- Remove expired refresh tokens
DELETE FROM refresh_tokens WHERE expires_at < CURRENT_TIMESTAMP;
```

### Reset Database (Development Only)

```sql
-- WARNING: This will delete ALL data
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;

-- Then run schema.sql and sample_data.sql again
```

## Security Notes

- **NEVER** use sample_data.sql in production
- Change all default passwords before deploying
- Regularly backup your production database
- Keep DATABASE_URL secret and secure
- Use strong passwords for PostgreSQL users

## pgAdmin Tips

### View Query Results
After running sample_data.sql, the verification queries will show:
- Total counts for each table
- List of users (without passwords)
- List of staff members

### Create Backup Schedule
1. Tools → Server → Backup Schedule
2. Set frequency (daily/weekly)
3. Set retention period
4. Configure notification email
