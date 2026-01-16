# Passcode Guessing Game - Backend

A FastAPI backend for a two-player passcode guessing game.

## Setup

### 1. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Access API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI app initialization
│   ├── config.py         # Configuration settings
│   ├── models/           # Pydantic data models
│   ├── schemas/          # Request/Response schemas
│   ├── routers/          # API route handlers
│   ├── services/         # Business logic
│   ├── storage/          # In-memory data storage
│   └── utils/            # Utility functions
├── requirements.txt
└── README.md
```
