# Staff Management Backend

A RESTful API backend built with FastAPI for managing staff information with authentication and authorization.

## Features

- User authentication and authorization with JWT tokens
- Staff management (CRUD operations)
- PostgreSQL database with async support
- API documentation with Swagger UI and ReDoc
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
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Production Deployment

1. Set environment variables:

   - Set `DEBUG=False`
   - Set `APP_ENV=production`
   - Update CORS settings in `main.py` to restrict origins
   - Use a production-grade database

2. Run with production server:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```
