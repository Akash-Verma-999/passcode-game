# Phase 1: Project Setup - Implementation Details

## Overview
Phase 1 establishes the foundational structure for the Passcode Guessing Game FastAPI backend. This phase focuses on creating the project skeleton, installing dependencies, and defining the core data models.

---

## What Was Done

### 1. Created Backend Folder Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── player.py
│   │   ├── guess.py
│   │   └── game.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── requests.py
│   │   └── responses.py
│   ├── routers/
│   │   └── __init__.py
│   ├── services/
│   │   └── __init__.py
│   ├── storage/
│   │   └── __init__.py
│   └── utils/
│       └── __init__.py
├── requirements.txt
├── README.md
└── phase1.details.md
```

---

### 2. Dependencies (requirements.txt)

| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | >=0.109.0 | Web framework for building APIs |
| `uvicorn[standard]` | >=0.27.0 | ASGI server to run the application |
| `pydantic` | >=2.5.0 | Data validation and serialization |
| `pydantic-settings` | >=2.1.0 | Settings management with environment variables |
| `python-multipart` | >=0.0.6 | Form data parsing support |

---

### 3. Configuration (app/config.py)

Created a `Settings` class using Pydantic's `BaseSettings` for managing application configuration:

- **app_name**: Application title displayed in API docs
- **app_version**: Current version (1.0.0)
- **debug**: Debug mode flag
- **CORS settings**: Configured to allow all origins for development

The settings can be overridden via environment variables or a `.env` file.

---

### 4. FastAPI Application (app/main.py)

Initialized the FastAPI application with:

- **Title & Version**: From config settings
- **Description**: "A two-player passcode guessing game API"
- **Documentation URLs**: `/docs` (Swagger UI) and `/redoc` (ReDoc)
- **CORS Middleware**: Configured for cross-origin requests
- **Root Endpoint** (`GET /`): Returns welcome message and API info
- **Health Check** (`GET /health`): Returns server health status

---

### 5. Data Models (app/models/)

#### 5.1 Player Model (player.py)
```python
class Player:
    player_id: str       # Unique identifier
    name: str            # Display name (1-50 chars)
    secret_number: str   # 4-digit secret (nullable until locked)
    is_ready: bool       # True when number is locked
```

#### 5.2 Guess Model (guess.py)
```python
class Guess:
    guess_id: str           # Unique identifier
    game_id: str            # Reference to game
    guesser_player_id: str  # Who made the guess
    target_player_id: str   # Whose number is being guessed
    guessed_number: str     # The 4-digit guess
    correct_digits: int     # Digits present (0-4)
    correct_positions: int  # Exact matches (0-4)
    timestamp: datetime     # When guess was made
    turn_number: int        # Turn sequence number
```

#### 5.3 Game Model (game.py)
```python
class GameStatus(Enum):
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class Game:
    game_id: str            # Unique identifier
    player_1: Player        # Game creator
    player_2: Player | None # Second player (nullable)
    current_turn: str       # Current player's ID
    status: GameStatus      # Game state
    winner_id: str | None   # Winner's ID (nullable)
    guesses: list[Guess]    # All guesses history
    created_at: datetime    # Creation timestamp
    turn_count: int         # Total turns played
```

---

### 6. Request/Response Schemas (app/schemas/)

#### 6.1 Request Schemas (requests.py)

| Schema | Fields | Validation |
|--------|--------|------------|
| `CreateGameRequest` | `player_name` | 1-50 characters |
| `JoinGameRequest` | `player_name` | 1-50 characters |
| `LockNumberRequest` | `secret_number` | Regex: exactly 4 digits |
| `MakeGuessRequest` | `player_id`, `guessed_number` | 4-digit pattern |

#### 6.2 Response Schemas (responses.py)

| Schema | Purpose |
|--------|---------|
| `CreateGameResponse` | Response after creating a game |
| `JoinGameResponse` | Response after joining a game |
| `LockNumberResponse` | Response after locking secret number |
| `GuessResponse` | Response after making a guess |
| `PlayerInfo` | Player information (without secret) |
| `GameStatusResponse` | Current game state |
| `GuessDetail` | Single guess information |
| `GuessHistoryResponse` | List of all guesses |
| `ErrorResponse` | Standard error format |

---

### 7. README.md

Created documentation with:
- Setup instructions (virtual environment, dependencies)
- How to run the server
- API documentation URLs
- Project structure overview

---

## How to Verify Phase 1

### 1. Install Dependencies
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Run the Server
```bash
uvicorn app.main:app --reload
```

### 3. Test Endpoints
```bash
# Root endpoint
curl http://localhost:8000/

# Health check
curl http://localhost:8000/health
```

### 4. View API Documentation
Open http://localhost:8000/docs in your browser

---

## Next Steps (Phase 2)

Phase 2 will implement the **In-Memory Storage** layer:
- Create `memory_store.py` with storage dictionaries
- Implement CRUD helper functions
- Add ID generation utilities (UUID)

---

## Files Created in Phase 1

| File | Lines | Description |
|------|-------|-------------|
| `requirements.txt` | 5 | Python dependencies |
| `app/__init__.py` | 0 | Package marker |
| `app/main.py` | 33 | FastAPI application |
| `app/config.py` | 18 | Settings configuration |
| `app/models/__init__.py` | 0 | Package marker |
| `app/models/player.py` | 10 | Player data model |
| `app/models/guess.py` | 15 | Guess data model |
| `app/models/game.py` | 26 | Game data model |
| `app/schemas/__init__.py` | 0 | Package marker |
| `app/schemas/requests.py` | 18 | Request body schemas |
| `app/schemas/responses.py` | 68 | Response schemas |
| `app/routers/__init__.py` | 0 | Package marker |
| `app/services/__init__.py` | 0 | Package marker |
| `app/storage/__init__.py` | 0 | Package marker |
| `app/utils/__init__.py` | 0 | Package marker |
| `README.md` | 42 | Project documentation |

**Total: 16 files created**
