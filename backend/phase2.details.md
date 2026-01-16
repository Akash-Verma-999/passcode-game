# Phase 2: In-Memory Storage - Implementation Details

## Overview
Phase 2 implements the in-memory data storage layer for the Passcode Guessing Game. This includes storage dictionaries, CRUD operations, ID generation utilities, input validators, and custom exception handling.

---

## What Was Done

### 1. ID Generator Utility (`app/utils/id_generator.py`)

Created utility functions to generate unique identifiers with descriptive prefixes:

| Function | Prefix | Example Output |
|----------|--------|----------------|
| `generate_game_id()` | `game_` | `game_a1b2c3d4e5f6` |
| `generate_player_id()` | `player_` | `player_x9y8z7w6v5u4` |
| `generate_guess_id()` | `guess_` | `guess_m1n2o3p4q5r6` |

**Implementation:**
- Uses Python's `uuid.uuid4()` for randomness
- Takes first 12 hex characters for shorter, readable IDs
- Prefixes help identify entity type at a glance

---

### 2. Memory Store (`app/storage/memory_store.py`)

Created in-memory storage with three main dictionaries:

```python
games_db: dict[str, Game] = {}           # game_id -> Game
players_db: dict[str, Player] = {}       # player_id -> Player
game_guesses_db: dict[str, list[Guess]] = {}  # game_id -> List[Guess]
```

#### 2.1 Game CRUD Operations

| Function | Description |
|----------|-------------|
| `create_game(game)` | Store new game, initialize empty guesses list |
| `get_game(game_id)` | Retrieve game by ID (returns None if not found) |
| `update_game(game)` | Update existing game |
| `delete_game(game_id)` | Delete game and associated guesses |
| `get_all_games()` | Retrieve all games |
| `get_games_by_status(status)` | Filter games by status |

#### 2.2 Player CRUD Operations

| Function | Description |
|----------|-------------|
| `create_player(player)` | Store new player |
| `get_player(player_id)` | Retrieve player by ID |
| `update_player(player)` | Update existing player |
| `delete_player(player_id)` | Delete player |

#### 2.3 Guess CRUD Operations

| Function | Description |
|----------|-------------|
| `add_guess(guess)` | Add guess to game's history |
| `get_guesses_by_game(game_id)` | Get all guesses for a game |
| `get_guesses_by_player(game_id, player_id)` | Get guesses by specific player |
| `get_guess_count(game_id)` | Count total guesses in a game |

#### 2.4 Utility Functions

| Function | Description |
|----------|-------------|
| `clear_all_data()` | Clear all storage (for testing) |
| `get_player_by_game(game_id, player_id)` | Get player if they belong to game |
| `is_player_in_game(game_id, player_id)` | Check if player is in game |

---

### 3. Input Validators (`app/utils/validators.py`)

Created validation helper functions:

| Function | Purpose | Validation Rules |
|----------|---------|------------------|
| `is_valid_4_digit_number(number)` | Validate 4-digit string | Exactly 4 digits (0-9) |
| `is_valid_player_name(name)` | Validate player name | 1-50 characters, not empty |
| `validate_secret_number(number)` | Full validation with error message | Returns (bool, error_msg) |
| `validate_guess_number(number)` | Full validation with error message | Returns (bool, error_msg) |

---

### 4. Custom Exceptions (`app/utils/exceptions.py`)

Created 9 custom exception classes for specific error scenarios:

| Exception | HTTP Status | When Raised |
|-----------|-------------|-------------|
| `GameNotFoundError` | 404 | Game ID doesn't exist |
| `PlayerNotFoundError` | 404 | Player ID doesn't exist |
| `GameFullError` | 409 | Joining game with 2 players |
| `NotYourTurnError` | 409 | Player guesses out of turn |
| `GameNotStartedError` | 409 | Guessing before both players ready |
| `NumberAlreadyLockedError` | 409 | Changing already locked number |
| `InvalidNumberFormatError` | 400 | Number not 4 digits |
| `GameAlreadyCompletedError` | 409 | Playing finished game |
| `PlayerNotInGameError` | 403 | Player not in specified game |

---

### 5. Exception Handlers (`app/main.py`)

Added exception handlers to FastAPI app for all custom exceptions:

```python
@app.exception_handler(GameNotFoundError)
async def game_not_found_handler(request: Request, exc: GameNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc), "error_code": "GAME_NOT_FOUND"}
    )
```

**Response Format:**
```json
{
    "detail": "Human-readable error message",
    "error_code": "MACHINE_READABLE_CODE"
}
```

---

## Files Created/Modified in Phase 2

### New Files

| File | Lines | Description |
|------|-------|-------------|
| `app/utils/id_generator.py` | 16 | UUID generation utilities |
| `app/storage/memory_store.py` | 118 | In-memory storage with CRUD |
| `app/utils/validators.py` | 47 | Input validation helpers |
| `app/utils/exceptions.py` | 37 | Custom exception classes |

### Modified Files

| File | Changes |
|------|---------|
| `app/main.py` | Added exception imports and 9 exception handlers |

---

## Storage Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    In-Memory Storage                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  games_db                    players_db                     │
│  ┌─────────────────┐        ┌─────────────────┐            │
│  │ game_abc123     │        │ player_xyz789   │            │
│  │   → Game obj    │        │   → Player obj  │            │
│  │ game_def456     │        │ player_uvw456   │            │
│  │   → Game obj    │        │   → Player obj  │            │
│  └─────────────────┘        └─────────────────┘            │
│                                                             │
│  game_guesses_db                                            │
│  ┌─────────────────────────────────────────────┐           │
│  │ game_abc123 → [Guess1, Guess2, Guess3, ...] │           │
│  │ game_def456 → [Guess1, Guess2, ...]         │           │
│  └─────────────────────────────────────────────┘           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## How to Verify Phase 2

### 1. Start the Server
```bash
cd backend
uvicorn app.main:app --reload
```

### 2. Verify No Import Errors
Server should start without any import errors.

### 3. Test Health Endpoint
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

### 4. Unit Test Storage (Optional)
```python
# In Python REPL
from app.storage.memory_store import *
from app.models.game import Game, GameStatus
from app.models.player import Player
from app.utils.id_generator import generate_game_id, generate_player_id

# Create a player
player = Player(player_id=generate_player_id(), name="Test")
create_player(player)

# Verify
print(get_player(player.player_id))

# Clean up
clear_all_data()
```

---

## Next Steps (Phase 3)

Phase 3 will implement the **Core Game Logic**:
- `calculate_match()` function for comparing numbers
- Turn management logic
- Win condition checking
- Unit tests for game logic

---

## Summary

Phase 2 establishes the data layer foundation:
- **4 new files** created
- **1 file** modified (main.py)
- **~220 lines** of new code
- **9 custom exceptions** with handlers
- **15+ CRUD functions** for data management
- **4 validation functions** for input checking
