# OrcheNet Backend

FastAPI-based backend server for OrcheNet network device orchestration platform.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file with configuration:
```
DATABASE_URL=sqlite:///./orchenet.db
SECRET_KEY=your-secret-key-here
```

4. Run the development server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

## Project Structure

```
backend/
├── app/
│   ├── api/           # API endpoints
│   ├── models/        # Database models
│   ├── services/      # Business logic
│   ├── vendors/       # Vendor implementations
│   │   ├── base.py           # Vendor interface
│   │   └── mikrotik/         # MikroTik implementation
│   ├── config.py      # Application configuration
│   ├── database.py    # Database setup
│   └── main.py        # FastAPI application
├── tests/             # Test suite
└── requirements.txt   # Python dependencies
```

## Development

Run tests:
```bash
pytest
```

Run with auto-reload:
```bash
uvicorn app.main:app --reload
```

## Database Migrations

Using Alembic for database migrations:

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```
