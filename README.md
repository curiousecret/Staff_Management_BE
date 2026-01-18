# Staff Management Backend

A RESTful API backend built with FastAPI for managing staff information with authentication and authorization.

## Features

- User authentication and authorization with JWT tokens
- Staff management (CRUD operations)
- PostgreSQL database with async support
- API documentation with Swagger UI
- Clean architecture with separation of concerns (routers, services, repositories)
- Environment-based configuration
- CORS middleware support

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLModel
- **Database Driver**: asyncpg
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt + passlib
- **Server**: Uvicorn
- **Validation**: Pydantic

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.8 or higher
- PostgreSQL database
- pip (Python package manager)
- Virtual environment tool (venv)

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd Staff_Management_BE
```

2. Create and activate a virtual environment:

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

1. Create a `.env` file in the root directory with the following variables:

```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/database_name

# Security
SECRET_KEY=your-secret-key-here

# Application Settings
APP_ENV=development
DEBUG=True
```

2. Update the environment variables:
   - `DATABASE_URL`: Your PostgreSQL connection string
   - `SECRET_KEY`: A secure random string for JWT token signing (generate with `openssl rand -hex 32`)
   - `APP_ENV`: Environment mode (development/production)
   - `DEBUG`: Enable/disable debug mode (True/False)

3. Ensure your PostgreSQL database is running and accessible with the credentials provided in `DATABASE_URL`.

## Database Setup

After configuring your PostgreSQL connection, you need to set up the database tables. Choose one of the following methods:

### Method 1: Using Database Schema (Recommended for New Setup)

This method creates all tables from scratch using SQL scripts.

1. **Create the database** in pgAdmin:
   - Open pgAdmin and connect to your PostgreSQL server
   - Right-click on "Databases" and select "Create" > "Database..."
   - Enter your database name (must match the database name in your `DATABASE_URL`)
   - Click "Save"

2. **Run the schema script**:
   - Right-click on your newly created database
   - Select "Query Tool"
   - Open the schema file: `database/schema.sql`
   - Click "Execute/Run" (F5) to create all tables and indexes

3. **Load sample data** (optional, for testing):
   - In the same Query Tool, open: `database/sample_data.sql`
   - Click "Execute/Run" (F5) to insert sample records

**Verification:**
After running the scripts, you should have:
- 4 tables: `users`, `staff`, `refresh_tokens`, `token_blacklist`
- Sample users with test credentials (see sample_data.sql for login details)
- 13 sample staff records (10 active, 3 inactive)

### Method 2: Using Database Backup File

This method restores a complete database from a backup file (if provided).

1. **Create an empty database** in pgAdmin:
   - Right-click on "Databases" and select "Create" > "Database..."
   - Enter your database name
   - Click "Save"

2. **Restore from backup**:
   - Right-click on your database
   - Select "Restore..."
   - In the "Filename" field, browse to your `.backup` file
   - Set "Format" to "Custom or tar"
   - Click "Restore"

3. **Wait for completion**:
   - Check the process status in the background processes
   - Verify tables were created by expanding the database tree

### Database Structure

The database includes the following tables:

```
users
├── id (Primary Key)
├── username (Unique)
├── hashed_password
├── created_at
└── updated_at

staff
├── id (Primary Key)
├── staff_id (Unique Business ID)
├── name
├── dob (Date of Birth)
├── salary
├── status (active/inactive)
├── created_at
└── updated_at

refresh_tokens
├── id (Primary Key)
├── token (Unique)
├── user_id (Foreign Key → users.id)
├── is_revoked
├── created_at
├── expires_at
└── last_used_at

token_blacklist
├── id (Primary Key)
├── token (Unique)
├── blacklisted_at
└── expires_at
```

### Test Credentials (Sample Data)

If you loaded the sample data, you can use these credentials for testing:

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Administrator |
| manager | manager123 | Manager |
| user1 | password123 | Regular User |
| testuser | test123 | Test User |

**WARNING:** Change these passwords before deploying to production!

## Running the Application

1. Make sure your virtual environment is activated and PostgreSQL is running.

2. Start the development server:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

3. Access the interactive API documentation:
   - Swagger UI: `http://localhost:8000/docs`

4. Health check endpoint:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "healthy"
}
```

## Project Structure

```
Staff_Management_BE/
├── src/
│   ├── core/           # Core configuration and database setup
│   ├── models/         # Database models
│   ├── schemas/        # Pydantic schemas for request/response
│   ├── repositories/   # Data access layer
│   ├── services/       # Business logic layer
│   └── routers/        # API route handlers
│       ├── auth_router.py    # Authentication endpoints
│       └── staff_router.py   # Staff management endpoints
├── database/
│   ├── schema.sql      # Database schema creation script
│   └── sample_data.sql # Sample data for testing
├── main.py             # Application entry point
├── security.py         # Security utilities
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (not in git)
└── README.md          # This file
```

## API Endpoints

### Authentication

- `POST /api/v1/auth/...` - Authentication endpoints (login, register, etc.)

### Staff Management

- `GET /api/v1/staff/...` - Staff-related endpoints

For detailed API documentation, visit `/docs` after starting the server.

## Development

To run in development mode with auto-reload:

```bash
uvicorn main:app --reload
```
