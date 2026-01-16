# Passcode Guessing Game - FastAPI Backend Plan

## 1. Game Overview

A two-player passcode guessing game where:
- Each player selects a secret 4-digit number
- Players take turns guessing the opponent's number
- After each guess, the opponent provides feedback:
  - **Correct Digits**: How many digits from the guess exist in the secret number
  - **Correct Positions**: How many digits are in the exact correct position
- The first player to correctly guess the opponent's number wins

---

## 2. Tech Stack

| Component | Technology |
|-----------|------------|
| Backend Framework | FastAPI |
| Data Storage | In-Memory (Python dictionaries) |
| API Documentation | Swagger UI (auto-generated) |
| Validation | Pydantic |
| Server | Uvicorn |

---

## 3. Data Models (Pydantic Schemas)

### 3.1 Player Model
```python
class Player:
    player_id: str          # Unique identifier (e.g., UUID or custom ID)
    name: str               # Player display name
    secret_number: str      # 4-digit secret number (stored as string to preserve leading zeros)
    is_ready: bool          # True when player has locked their number
```

### 3.2 Guess Model
```python
class Guess:
    guess_id: str           # Unique identifier for the guess
    game_id: str            # Reference to the game
    guesser_player_id: str  # Player who made the guess
    target_player_id: str   # Player whose number is being guessed
    guessed_number: str     # The 4-digit guess
    correct_digits: int     # Count of digits present in target's number
    correct_positions: int  # Count of digits in exact position
    timestamp: datetime     # When the guess was made
    turn_number: int        # Which turn this guess was made on
```

### 3.3 Game Model
```python
class Game:
    game_id: str            # Unique game identifier
    player_1: Player        # First player
    player_2: Player        # Second player
    current_turn: str       # player_id of whose turn it is
    status: GameStatus      # WAITING, IN_PROGRESS, COMPLETED
    winner_id: str | None   # player_id of winner (None if game ongoing)
    guesses: List[Guess]    # History of all guesses
    created_at: datetime    # Game creation timestamp
    turn_count: int         # Total turns played
```

### 3.4 Enums
```python
class GameStatus(Enum):
    WAITING = "waiting"           # Waiting for players to join/lock numbers
    IN_PROGRESS = "in_progress"   # Game is active
    COMPLETED = "completed"       # Game has a winner
```

---

## 4. In-Memory Data Storage Structure

```python
# Main storage dictionaries
games_db: Dict[str, Game] = {}           # game_id -> Game object
players_db: Dict[str, Player] = {}       # player_id -> Player object
game_guesses_db: Dict[str, List[Guess]] = {}  # game_id -> List of Guesses
```

### 4.1 Storage Helper Functions
```python
def generate_game_id() -> str
def generate_player_id() -> str
def generate_guess_id() -> str
def get_game(game_id: str) -> Game | None
def get_player(player_id: str) -> Player | None
def save_game(game: Game) -> None
def save_guess(guess: Guess) -> None
```

---

## 5. API Endpoints

### 5.1 Game Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/games` | Create a new game |
| `GET` | `/games/{game_id}` | Get game details |
| `GET` | `/games` | List all active games |
| `DELETE` | `/games/{game_id}` | Delete/cancel a game |

### 5.2 Player Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/games/{game_id}/join` | Join an existing game |
| `POST` | `/games/{game_id}/players/{player_id}/lock-number` | Lock the 4-digit secret number |
| `GET` | `/games/{game_id}/players/{player_id}` | Get player info (excluding secret number) |

### 5.3 Gameplay

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/games/{game_id}/guess` | Make a guess |
| `GET` | `/games/{game_id}/guesses` | Get all guesses in a game |
| `GET` | `/games/{game_id}/guesses/{player_id}` | Get guesses made by a specific player |
| `GET` | `/games/{game_id}/turn` | Get current turn information |

### 5.4 Game State

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/games/{game_id}/status` | Get current game status |
| `GET` | `/games/{game_id}/history` | Get complete game history |

---

## 6. Detailed Endpoint Specifications

### 6.1 Create Game
```
POST /games
```
**Request Body:**
```json
{
    "player_name": "Player1"
}
```
**Response:**
```json
{
    "game_id": "game_abc123",
    "player_id": "player_xyz789",
    "status": "waiting",
    "message": "Game created. Share game_id with opponent to join."
}
```

---

### 6.2 Join Game
```
POST /games/{game_id}/join
```
**Request Body:**
```json
{
    "player_name": "Player2"
}
```
**Response:**
```json
{
    "game_id": "game_abc123",
    "player_id": "player_def456",
    "status": "waiting",
    "message": "Joined game. Both players need to lock their numbers."
}
```

---

### 6.3 Lock Secret Number
```
POST /games/{game_id}/players/{player_id}/lock-number
```
**Request Body:**
```json
{
    "secret_number": "1234"
}
```
**Validations:**
- Must be exactly 4 digits
- Must contain only numeric characters (0-9)
- Player must belong to the game
- Number cannot be changed once locked

**Response:**
```json
{
    "player_id": "player_xyz789",
    "is_ready": true,
    "message": "Number locked successfully.",
    "game_status": "waiting"  // or "in_progress" if both players ready
}
```

---

### 6.4 Make a Guess
```
POST /games/{game_id}/guess
```
**Request Body:**
```json
{
    "player_id": "player_xyz789",
    "guessed_number": "5678"
}
```
**Validations:**
- Game must be in "in_progress" status
- Must be the player's turn
- Guessed number must be exactly 4 digits
- Both players must have locked their numbers

**Response:**
```json
{
    "guess_id": "guess_001",
    "guessed_number": "5678",
    "correct_digits": 2,
    "correct_positions": 1,
    "is_winner": false,
    "next_turn": "player_def456",
    "turn_number": 1
}
```

**Winning Response:**
```json
{
    "guess_id": "guess_015",
    "guessed_number": "9876",
    "correct_digits": 4,
    "correct_positions": 4,
    "is_winner": true,
    "winner_id": "player_xyz789",
    "message": "Congratulations! You guessed the correct number!",
    "total_turns": 8
}
```

---

### 6.5 Get Game Status
```
GET /games/{game_id}/status
```
**Response:**
```json
{
    "game_id": "game_abc123",
    "status": "in_progress",
    "player_1": {
        "player_id": "player_xyz789",
        "name": "Player1",
        "is_ready": true
    },
    "player_2": {
        "player_id": "player_def456",
        "name": "Player2",
        "is_ready": true
    },
    "current_turn": "player_xyz789",
    "turn_count": 5,
    "winner_id": null
}
```

---

### 6.6 Get Guess History
```
GET /games/{game_id}/guesses
```
**Query Parameters:**
- `player_id` (optional): Filter by player

**Response:**
```json
{
    "game_id": "game_abc123",
    "total_guesses": 6,
    "guesses": [
        {
            "guess_id": "guess_001",
            "guesser": "Player1",
            "guessed_number": "1234",
            "correct_digits": 2,
            "correct_positions": 0,
            "turn_number": 1
        },
        {
            "guess_id": "guess_002",
            "guesser": "Player2",
            "guessed_number": "5678",
            "correct_digits": 1,
            "correct_positions": 1,
            "turn_number": 2
        }
    ]
}
```

---

## 7. Core Game Logic Functions

### 7.1 Calculate Match Results
```python
def calculate_match(secret_number: str, guessed_number: str) -> Tuple[int, int]:
    """
    Returns (correct_digits, correct_positions)
    
    Example:
    secret = "1234"
    guess  = "1325"
    
    correct_positions = 2 (1 at pos 0, 3 at pos 1... wait, let me recalculate)
    Actually: 1 is at correct position (index 0), 2 is not, 3 is not, 5 is not
    correct_positions = 1
    
    correct_digits: 1, 2, 3 exist in secret = 3
    """
    pass
```

### 7.2 Detailed Algorithm for Match Calculation
```python
def calculate_match(secret: str, guess: str) -> dict:
    correct_positions = 0
    correct_digits = 0
    
    # Count exact position matches
    for i in range(4):
        if secret[i] == guess[i]:
            correct_positions += 1
    
    # Count digit matches (regardless of position)
    secret_digit_count = {}
    guess_digit_count = {}
    
    for digit in secret:
        secret_digit_count[digit] = secret_digit_count.get(digit, 0) + 1
    
    for digit in guess:
        guess_digit_count[digit] = guess_digit_count.get(digit, 0) + 1
    
    # For each digit, take minimum of occurrences in both
    for digit in guess_digit_count:
        if digit in secret_digit_count:
            correct_digits += min(secret_digit_count[digit], guess_digit_count[digit])
    
    return {
        "correct_digits": correct_digits,
        "correct_positions": correct_positions
    }
```

### 7.3 Turn Management
```python
def switch_turn(game: Game) -> str:
    """Switch turn to the other player and return new current_turn player_id"""
    pass

def validate_turn(game: Game, player_id: str) -> bool:
    """Check if it's the given player's turn"""
    pass
```

### 7.4 Win Condition Check
```python
def check_winner(correct_positions: int) -> bool:
    """Returns True if all 4 positions are correct"""
    return correct_positions == 4
```

---

## 8. Project Structure

```
Passcode_Game/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app initialization, CORS, routers
│   ├── config.py               # Configuration settings
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── game.py             # Game, GameStatus models
│   │   ├── player.py           # Player model
│   │   └── guess.py            # Guess model
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── requests.py         # Request body schemas
│   │   └── responses.py        # Response schemas
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── games.py            # Game management endpoints
│   │   ├── players.py          # Player endpoints
│   │   └── gameplay.py         # Guess and turn endpoints
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── game_service.py     # Game business logic
│   │   ├── player_service.py   # Player business logic
│   │   └── guess_service.py    # Guess calculation logic
│   │
│   ├── storage/
│   │   ├── __init__.py
│   │   └── memory_store.py     # In-memory data storage
│   │
│   └── utils/
│       ├── __init__.py
│       ├── validators.py       # Input validation helpers
│       └── id_generator.py     # UUID generation utilities
│
├── tests/
│   ├── __init__.py
│   ├── test_game_logic.py      # Unit tests for game logic
│   ├── test_endpoints.py       # API endpoint tests
│   └── test_match_calculation.py
│
├── requirements.txt
├── README.md
└── plan.md                     # This file
```

---

## 9. Request/Response Schemas

### 9.1 Request Schemas
```python
# requests.py

class CreateGameRequest(BaseModel):
    player_name: str = Field(..., min_length=1, max_length=50)

class JoinGameRequest(BaseModel):
    player_name: str = Field(..., min_length=1, max_length=50)

class LockNumberRequest(BaseModel):
    secret_number: str = Field(..., pattern=r"^\d{4}$")

class MakeGuessRequest(BaseModel):
    player_id: str
    guessed_number: str = Field(..., pattern=r"^\d{4}$")
```

### 9.2 Response Schemas
```python
# responses.py

class CreateGameResponse(BaseModel):
    game_id: str
    player_id: str
    status: str
    message: str

class JoinGameResponse(BaseModel):
    game_id: str
    player_id: str
    status: str
    message: str

class LockNumberResponse(BaseModel):
    player_id: str
    is_ready: bool
    message: str
    game_status: str

class GuessResponse(BaseModel):
    guess_id: str
    guessed_number: str
    correct_digits: int
    correct_positions: int
    is_winner: bool
    next_turn: str | None
    winner_id: str | None
    message: str | None
    turn_number: int

class GameStatusResponse(BaseModel):
    game_id: str
    status: str
    player_1: PlayerInfo
    player_2: PlayerInfo | None
    current_turn: str | None
    turn_count: int
    winner_id: str | None

class PlayerInfo(BaseModel):
    player_id: str
    name: str
    is_ready: bool

class GuessHistoryResponse(BaseModel):
    game_id: str
    total_guesses: int
    guesses: List[GuessDetail]

class GuessDetail(BaseModel):
    guess_id: str
    guesser: str
    guessed_number: str
    correct_digits: int
    correct_positions: int
    turn_number: int
```

---

## 10. Error Handling

### 10.1 Custom Exceptions
```python
class GameNotFoundError(Exception):
    """Raised when game_id doesn't exist"""

class PlayerNotFoundError(Exception):
    """Raised when player_id doesn't exist"""

class GameFullError(Exception):
    """Raised when trying to join a game with 2 players"""

class NotYourTurnError(Exception):
    """Raised when player tries to guess out of turn"""

class GameNotStartedError(Exception):
    """Raised when trying to guess before both players lock numbers"""

class NumberAlreadyLockedError(Exception):
    """Raised when trying to change locked number"""

class InvalidNumberFormatError(Exception):
    """Raised when number is not 4 digits"""

class GameAlreadyCompletedError(Exception):
    """Raised when trying to play a finished game"""
```

### 10.2 HTTP Error Responses
| Status Code | Scenario |
|-------------|----------|
| 400 | Invalid input (wrong format, validation failed) |
| 404 | Game or Player not found |
| 409 | Conflict (game full, number already locked, not your turn) |
| 422 | Unprocessable entity (Pydantic validation) |

### 10.3 Exception Handler Example
```python
@app.exception_handler(GameNotFoundError)
async def game_not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Game not found", "error_code": "GAME_NOT_FOUND"}
    )
```

---

## 11. Game Flow Sequence

```
┌─────────────────────────────────────────────────────────────────────┐
│                         GAME FLOW                                   │
└─────────────────────────────────────────────────────────────────────┘

1. GAME CREATION
   Player 1 ──POST /games──> Server creates game (status: WAITING)
                             Returns: game_id, player_1_id

2. PLAYER 2 JOINS
   Player 2 ──POST /games/{id}/join──> Server adds Player 2
                                       Returns: player_2_id

3. LOCK NUMBERS (Both players, any order)
   Player 1 ──POST /lock-number──> Locks "1234"
   Player 2 ──POST /lock-number──> Locks "5678"
   
   When both locked: status changes to IN_PROGRESS
   Player 1 gets first turn (game creator)

4. GAMEPLAY LOOP
   ┌────────────────────────────────────────────────────┐
   │  While no winner:                                  │
   │                                                    │
   │  Player 1's Turn:                                  │
   │    POST /guess {"guessed_number": "5679"}         │
   │    Response: correct_digits=3, correct_positions=2│
   │                                                    │
   │  Player 2's Turn:                                  │
   │    POST /guess {"guessed_number": "1235"}         │
   │    Response: correct_digits=3, correct_positions=3│
   │                                                    │
   │  ... continues ...                                 │
   └────────────────────────────────────────────────────┘

5. GAME END
   When correct_positions = 4:
   - status changes to COMPLETED
   - winner_id is set
   - Response includes victory message
```

---

## 12. Implementation Phases

### Phase 1: Project Setup
- [ ] Initialize project structure
- [ ] Create `requirements.txt` with dependencies
- [ ] Set up FastAPI app with CORS
- [ ] Create base Pydantic models

### Phase 2: In-Memory Storage
- [ ] Implement `memory_store.py`
- [ ] Create storage dictionaries
- [ ] Implement CRUD helper functions
- [ ] Add ID generation utilities

### Phase 3: Core Game Logic
- [ ] Implement `calculate_match()` function
- [ ] Implement turn management
- [ ] Implement win condition check
- [ ] Write unit tests for game logic

### Phase 4: Game Management Endpoints
- [ ] `POST /games` - Create game
- [ ] `GET /games/{game_id}` - Get game
- [ ] `GET /games` - List games
- [ ] `DELETE /games/{game_id}` - Delete game

### Phase 5: Player Endpoints
- [ ] `POST /games/{game_id}/join` - Join game
- [ ] `POST /lock-number` - Lock secret number
- [ ] `GET /players/{player_id}` - Get player info

### Phase 6: Gameplay Endpoints
- [ ] `POST /games/{game_id}/guess` - Make guess
- [ ] `GET /games/{game_id}/guesses` - Get history
- [ ] `GET /games/{game_id}/turn` - Get turn info
- [ ] `GET /games/{game_id}/status` - Get status

### Phase 7: Error Handling & Validation
- [ ] Create custom exceptions
- [ ] Add exception handlers
- [ ] Add input validation
- [ ] Test edge cases

### Phase 8: Testing & Documentation
- [ ] Write comprehensive tests
- [ ] Add API documentation
- [ ] Create README with usage examples
- [ ] Manual testing with Swagger UI

---

## 13. Dependencies (requirements.txt)

```
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
pydantic>=2.5.0
python-multipart>=0.0.6
```

---

## 14. Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Access API docs
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

---

## 15. Example Game Session (API Calls)

```bash
# 1. Player 1 creates a game
curl -X POST http://localhost:8000/games \
  -H "Content-Type: application/json" \
  -d '{"player_name": "Alice"}'
# Response: {"game_id": "g_abc123", "player_id": "p_alice01", ...}

# 2. Player 2 joins the game
curl -X POST http://localhost:8000/games/g_abc123/join \
  -H "Content-Type: application/json" \
  -d '{"player_name": "Bob"}'
# Response: {"game_id": "g_abc123", "player_id": "p_bob02", ...}

# 3. Player 1 locks their number
curl -X POST http://localhost:8000/games/g_abc123/players/p_alice01/lock-number \
  -H "Content-Type: application/json" \
  -d '{"secret_number": "1234"}'

# 4. Player 2 locks their number
curl -X POST http://localhost:8000/games/g_abc123/players/p_bob02/lock-number \
  -H "Content-Type: application/json" \
  -d '{"secret_number": "5678"}'

# 5. Player 1 makes a guess
curl -X POST http://localhost:8000/games/g_abc123/guess \
  -H "Content-Type: application/json" \
  -d '{"player_id": "p_alice01", "guessed_number": "5679"}'
# Response: {"correct_digits": 3, "correct_positions": 2, ...}

# 6. Player 2 makes a guess
curl -X POST http://localhost:8000/games/g_abc123/guess \
  -H "Content-Type: application/json" \
  -d '{"player_id": "p_bob02", "guessed_number": "1235"}'

# ... game continues until someone wins
```

---

## 16. Future Enhancements (Out of Scope for Now)

- WebSocket support for real-time updates
- Database persistence (PostgreSQL/MongoDB)
- User authentication (JWT)
- Game replay functionality
- Leaderboard system
- Time limits per turn
- Spectator mode
- Game room codes (human-readable)

---

## 17. Notes & Considerations

1. **Leading Zeros**: Store numbers as strings to preserve leading zeros (e.g., "0123")
2. **Concurrency**: In-memory storage is not thread-safe; consider using locks for production
3. **Data Loss**: All data is lost on server restart (acceptable for MVP)
4. **Turn Order**: Player 1 (game creator) always goes first
5. **Duplicate Digits**: The match algorithm handles duplicate digits correctly
