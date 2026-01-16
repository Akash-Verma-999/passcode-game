# Phase 4: API Endpoints (Routers) - Implementation Details

## Overview
Phase 4 implements all the REST API endpoints for the Passcode Guessing Game. Three routers handle game management, player operations, and gameplay actions.

---

## What Was Done

### 1. Games Router (`app/routers/games.py`)

Handles game lifecycle operations.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/games` | Create a new game |
| `GET` | `/games` | List all games |
| `GET` | `/games/{game_id}` | Get game details |
| `DELETE` | `/games/{game_id}` | Delete a game |

#### 1.1 Create Game
```
POST /games
Content-Type: application/json

{
    "player_name": "Alice"
}
```

**Response (201 Created):**
```json
{
    "game_id": "game_a1b2c3d4e5f6",
    "player_id": "player_x9y8z7w6v5u4",
    "status": "waiting",
    "message": "Game created successfully. Share game_id with opponent to join."
}
```

#### 1.2 List Games
```
GET /games
```

**Response (200 OK):**
```json
[
    {
        "game_id": "game_a1b2c3d4e5f6",
        "status": "waiting",
        "player_1": {"player_id": "...", "name": "Alice", "is_ready": false},
        "player_2": null,
        "current_turn": null,
        "turn_count": 0,
        "winner_id": null
    }
]
```

#### 1.3 Get Game
```
GET /games/{game_id}
```

**Response (200 OK):**
```json
{
    "game_id": "game_a1b2c3d4e5f6",
    "status": "in_progress",
    "player_1": {"player_id": "...", "name": "Alice", "is_ready": true},
    "player_2": {"player_id": "...", "name": "Bob", "is_ready": true},
    "current_turn": "player_x9y8z7w6v5u4",
    "turn_count": 5,
    "winner_id": null
}
```

#### 1.4 Delete Game
```
DELETE /games/{game_id}
```

**Response (204 No Content)**

---

### 2. Players Router (`app/routers/players.py`)

Handles player joining and number locking.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/games/{game_id}/join` | Join an existing game |
| `POST` | `/games/{game_id}/players/{player_id}/lock-number` | Lock secret number |
| `GET` | `/games/{game_id}/players/{player_id}` | Get player info |

#### 2.1 Join Game
```
POST /games/{game_id}/join
Content-Type: application/json

{
    "player_name": "Bob"
}
```

**Response (200 OK):**
```json
{
    "game_id": "game_a1b2c3d4e5f6",
    "player_id": "player_m1n2o3p4q5r6",
    "status": "waiting",
    "message": "Joined game successfully. Both players need to lock their numbers to start."
}
```

#### 2.2 Lock Secret Number
```
POST /games/{game_id}/players/{player_id}/lock-number
Content-Type: application/json

{
    "secret_number": "1234"
}
```

**Response (200 OK):**
```json
{
    "player_id": "player_x9y8z7w6v5u4",
    "is_ready": true,
    "message": "Number locked. Game started! Player 1 goes first.",
    "game_status": "in_progress"
}
```

#### 2.3 Get Player Info
```
GET /games/{game_id}/players/{player_id}
```

**Response (200 OK):**
```json
{
    "player_id": "player_x9y8z7w6v5u4",
    "name": "Alice",
    "is_ready": true
}
```

---

### 3. Gameplay Router (`app/routers/gameplay.py`)

Handles guessing and game progress.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/games/{game_id}/guess` | Make a guess |
| `GET` | `/games/{game_id}/guesses` | Get guess history |
| `GET` | `/games/{game_id}/turn` | Get current turn info |

#### 3.1 Make Guess
```
POST /games/{game_id}/guess
Content-Type: application/json

{
    "player_id": "player_x9y8z7w6v5u4",
    "guessed_number": "5678"
}
```

**Response (200 OK) - Not Winner:**
```json
{
    "guess_id": "guess_abc123def456",
    "guessed_number": "5678",
    "correct_digits": 2,
    "correct_positions": 1,
    "is_winner": false,
    "next_turn": "player_m1n2o3p4q5r6",
    "winner_id": null,
    "message": null,
    "turn_number": 1
}
```

**Response (200 OK) - Winner:**
```json
{
    "guess_id": "guess_xyz789uvw012",
    "guessed_number": "9876",
    "correct_digits": 4,
    "correct_positions": 4,
    "is_winner": true,
    "next_turn": null,
    "winner_id": "player_x9y8z7w6v5u4",
    "message": "Congratulations! You guessed the correct number and won the game!",
    "turn_number": 8
}
```

#### 3.2 Get Guess History
```
GET /games/{game_id}/guesses
GET /games/{game_id}/guesses?player_id=player_x9y8z7w6v5u4
```

**Response (200 OK):**
```json
{
    "game_id": "game_a1b2c3d4e5f6",
    "total_guesses": 6,
    "guesses": [
        {
            "guess_id": "guess_001",
            "guesser": "Alice",
            "guessed_number": "1234",
            "correct_digits": 2,
            "correct_positions": 0,
            "turn_number": 1
        },
        {
            "guess_id": "guess_002",
            "guesser": "Bob",
            "guessed_number": "5678",
            "correct_digits": 1,
            "correct_positions": 1,
            "turn_number": 2
        }
    ]
}
```

#### 3.3 Get Turn Info
```
GET /games/{game_id}/turn
```

**Response (200 OK):**
```json
{
    "game_id": "game_a1b2c3d4e5f6",
    "current_turn": "player_x9y8z7w6v5u4",
    "current_player_name": "Alice",
    "turn_count": 5,
    "game_status": "in_progress"
}
```

---

## Files Created/Modified in Phase 4

### New Files

| File | Lines | Description |
|------|-------|-------------|
| `app/routers/games.py` | 102 | Game management endpoints |
| `app/routers/players.py` | 77 | Player operations endpoints |
| `app/routers/gameplay.py` | 108 | Gameplay endpoints |

### Modified Files

| File | Changes |
|------|---------|
| `app/main.py` | Added router imports and registration |

---

## Complete API Summary

| Method | Endpoint | Tag | Description |
|--------|----------|-----|-------------|
| `GET` | `/` | Root | Welcome message |
| `GET` | `/health` | Root | Health check |
| `POST` | `/games` | Games | Create game |
| `GET` | `/games` | Games | List all games |
| `GET` | `/games/{game_id}` | Games | Get game details |
| `DELETE` | `/games/{game_id}` | Games | Delete game |
| `POST` | `/games/{game_id}/join` | Players | Join game |
| `POST` | `/games/{game_id}/players/{player_id}/lock-number` | Players | Lock number |
| `GET` | `/games/{game_id}/players/{player_id}` | Players | Get player info |
| `POST` | `/games/{game_id}/guess` | Gameplay | Make guess |
| `GET` | `/games/{game_id}/guesses` | Gameplay | Get guess history |
| `GET` | `/games/{game_id}/turn` | Gameplay | Get turn info |

**Total: 12 endpoints**

---

## How to Test Phase 4

### 1. Start the Server
```bash
cd backend
uvicorn app.main:app --reload
```

### 2. Open Swagger UI
Navigate to http://localhost:8000/docs

### 3. Complete Game Flow Test
```bash
# 1. Create game (Alice)
curl -X POST http://localhost:8000/games \
  -H "Content-Type: application/json" \
  -d '{"player_name": "Alice"}'

# 2. Join game (Bob) - use game_id from step 1
curl -X POST http://localhost:8000/games/{game_id}/join \
  -H "Content-Type: application/json" \
  -d '{"player_name": "Bob"}'

# 3. Lock Alice's number
curl -X POST http://localhost:8000/games/{game_id}/players/{alice_player_id}/lock-number \
  -H "Content-Type: application/json" \
  -d '{"secret_number": "1234"}'

# 4. Lock Bob's number
curl -X POST http://localhost:8000/games/{game_id}/players/{bob_player_id}/lock-number \
  -H "Content-Type: application/json" \
  -d '{"secret_number": "5678"}'

# 5. Alice guesses
curl -X POST http://localhost:8000/games/{game_id}/guess \
  -H "Content-Type: application/json" \
  -d '{"player_id": "{alice_player_id}", "guessed_number": "5679"}'

# 6. Check turn
curl http://localhost:8000/games/{game_id}/turn

# 7. Get guess history
curl http://localhost:8000/games/{game_id}/guesses
```

---

## Error Responses

All endpoints return consistent error responses:

```json
{
    "detail": "Human-readable error message",
    "error_code": "MACHINE_READABLE_CODE"
}
```

| Error Code | HTTP Status | Scenario |
|------------|-------------|----------|
| `GAME_NOT_FOUND` | 404 | Invalid game_id |
| `PLAYER_NOT_FOUND` | 404 | Invalid player_id |
| `GAME_FULL` | 409 | Joining full game |
| `NOT_YOUR_TURN` | 409 | Guessing out of turn |
| `GAME_NOT_STARTED` | 409 | Guessing before game starts |
| `NUMBER_ALREADY_LOCKED` | 409 | Changing locked number |
| `GAME_ALREADY_COMPLETED` | 409 | Playing finished game |
| `PLAYER_NOT_IN_GAME` | 403 | Player not in game |

---

## Next Steps (Phase 5 - Optional)

Potential enhancements:
- Add unit tests for all endpoints
- Add integration tests for complete game flows
- Add WebSocket support for real-time updates
- Add database persistence

---

## Summary

Phase 4 completes the API layer:
- **3 router files** created
- **12 total endpoints** available
- **Full game flow** supported via REST API
- **Swagger UI** auto-generated at `/docs`
- **All error cases** handled with proper HTTP status codes
