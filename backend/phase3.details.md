# Phase 3: Core Game Logic - Implementation Details

## Overview
Phase 3 implements the core business logic for the Passcode Guessing Game. This includes the match calculation algorithm, turn management, win condition checking, and all game/guess/player services.

---

## What Was Done

### 1. Game Service (`app/services/game_service.py`)

Central service for game management operations.

#### 1.1 Game Lifecycle Functions

| Function | Description |
|----------|-------------|
| `create_new_game(player_name)` | Creates game + player 1, returns (game, player_id) |
| `join_game(game_id, player_name)` | Adds player 2 to game, returns (game, player_id) |
| `lock_player_number(game_id, player_id, secret_number)` | Locks secret, starts game if both ready |
| `get_game_status(game_id)` | Returns current game state |
| `delete_game_by_id(game_id)` | Deletes a game |
| `list_all_games()` | Returns all games |

#### 1.2 Turn Management Functions

| Function | Description |
|----------|-------------|
| `get_current_turn(game_id)` | Returns player_id of current turn |
| `validate_turn(game, player_id)` | Checks if it's the player's turn |
| `switch_turn(game)` | Switches to other player, returns new turn |
| `get_opponent(game, player_id)` | Returns the opponent Player object |

#### 1.3 Win Condition Functions

| Function | Description |
|----------|-------------|
| `check_winner(correct_positions)` | Returns True if all 4 positions correct |
| `set_winner(game, winner_id)` | Sets winner and marks game COMPLETED |

---

### 2. Guess Service (`app/services/guess_service.py`)

Handles all guess-related operations including the core matching algorithm.

#### 2.1 The `calculate_match()` Algorithm

```python
def calculate_match(secret: str, guess: str) -> dict:
    """
    Returns:
        correct_digits: How many digits from guess exist in secret
        correct_positions: How many digits are in exact position
    """
```

**Algorithm Explanation:**

1. **Correct Positions**: Direct comparison at each index
   ```python
   for i in range(4):
       if secret[i] == guess[i]:
           correct_positions += 1
   ```

2. **Correct Digits**: Count occurrences and take minimum
   ```python
   # Count digits in both numbers
   secret_count = {"1": 2, "3": 1, "4": 1}  # for "1134"
   guess_count = {"1": 1, "2": 1, "3": 1, "4": 1}  # for "1234"
   
   # For each digit in guess, add min(secret_count, guess_count)
   correct_digits = min(2,1) + min(0,1) + min(1,1) + min(1,1) = 3
   ```

**Examples:**

| Secret | Guess | Correct Digits | Correct Positions |
|--------|-------|----------------|-------------------|
| 1234 | 1234 | 4 | 4 (WIN!) |
| 1234 | 4321 | 4 | 0 |
| 1234 | 1243 | 4 | 2 |
| 1234 | 5678 | 0 | 0 |
| 1234 | 1111 | 1 | 1 |
| 1122 | 2211 | 4 | 0 |

#### 2.2 Guess Processing

| Function | Description |
|----------|-------------|
| `process_guess(game_id, player_id, guessed_number)` | Full guess workflow |
| `get_game_guesses(game_id)` | Get all guesses for a game |
| `get_player_guesses(game_id, player_id)` | Get guesses by specific player |

**`process_guess()` Flow:**

```
1. Validate game exists
2. Check game status (must be IN_PROGRESS)
3. Validate player is in game
4. Validate it's player's turn
5. Get opponent's secret number
6. Calculate match (correct_digits, correct_positions)
7. Increment turn count
8. Create and store Guess record
9. Check for winner (correct_positions == 4)
10. If winner: set winner, return result
11. If not: switch turn, return result
```

---

### 3. Player Service (`app/services/player_service.py`)

Handles player information retrieval.

| Function | Description |
|----------|-------------|
| `get_player_info(game_id, player_id)` | Get player info (excludes secret) |
| `get_player_by_id(player_id)` | Get player by ID |
| `get_both_players_info(game_id)` | Get both players' info |

**Security Note:** Player info functions never expose the `secret_number` field.

---

## Files Created in Phase 3

| File | Lines | Description |
|------|-------|-------------|
| `app/services/game_service.py` | 175 | Game lifecycle, turn management, win logic |
| `app/services/guess_service.py` | 170 | Match calculation, guess processing |
| `app/services/player_service.py` | 78 | Player information retrieval |

**Total: 3 files, ~423 lines of code**

---

## Game State Machine

```
                    ┌─────────────────┐
                    │    WAITING      │
                    │  (Game Created) │
                    └────────┬────────┘
                             │
                    Player 2 Joins
                             │
                             ▼
                    ┌─────────────────┐
                    │    WAITING      │
                    │ (Both Players)  │
                    └────────┬────────┘
                             │
               Both Players Lock Numbers
                             │
                             ▼
                    ┌─────────────────┐
        ┌──────────│  IN_PROGRESS    │◄─────────┐
        │          │ (Player 1 Turn) │          │
        │          └────────┬────────┘          │
        │                   │                   │
        │           Player 1 Guesses            │
        │           (Not Winner)                │
        │                   │                   │
        │                   ▼                   │
        │          ┌─────────────────┐          │
        │          │  IN_PROGRESS    │          │
        │          │ (Player 2 Turn) │──────────┘
        │          └────────┬────────┘
        │                   │
        │           Player Guesses
        │           (correct_positions == 4)
        │                   │
        │                   ▼
        │          ┌─────────────────┐
        └─────────►│   COMPLETED     │
                   │  (Has Winner)   │
                   └─────────────────┘
```

---

## Turn Management Logic

```python
# Initial state after both players lock numbers
game.current_turn = game.player_1.player_id  # Player 1 always first

# After each guess (if not winner)
def switch_turn(game):
    if game.current_turn == game.player_1.player_id:
        game.current_turn = game.player_2.player_id
    else:
        game.current_turn = game.player_1.player_id
```

---

## How to Verify Phase 3

### 1. Test calculate_match() in Python REPL
```python
from app.services.guess_service import calculate_match

# Test cases
print(calculate_match("1234", "1234"))  # {'correct_digits': 4, 'correct_positions': 4}
print(calculate_match("1234", "4321"))  # {'correct_digits': 4, 'correct_positions': 0}
print(calculate_match("1234", "1243"))  # {'correct_digits': 4, 'correct_positions': 2}
print(calculate_match("1234", "5678"))  # {'correct_digits': 0, 'correct_positions': 0}
print(calculate_match("1122", "2211"))  # {'correct_digits': 4, 'correct_positions': 0}
```

### 2. Test Full Game Flow
```python
from app.services.game_service import create_new_game, join_game, lock_player_number
from app.services.guess_service import process_guess

# Create game
game, p1_id = create_new_game("Alice")
print(f"Game: {game.game_id}, Player 1: {p1_id}")

# Join game
game, p2_id = join_game(game.game_id, "Bob")
print(f"Player 2: {p2_id}")

# Lock numbers
lock_player_number(game.game_id, p1_id, "1234")
game = lock_player_number(game.game_id, p2_id, "5678")
print(f"Game status: {game.status}")  # IN_PROGRESS

# Make guesses
result = process_guess(game.game_id, p1_id, "5679")
print(result)  # correct_digits, correct_positions, next_turn
```

---

## Next Steps (Phase 4)

Phase 4 will implement the **API Endpoints (Routers)**:
- `POST /games` - Create game
- `POST /games/{game_id}/join` - Join game
- `POST /games/{game_id}/players/{player_id}/lock-number` - Lock number
- `POST /games/{game_id}/guess` - Make guess
- `GET /games/{game_id}/status` - Get status
- `GET /games/{game_id}/guesses` - Get history

---

## Summary

Phase 3 establishes the core game logic:
- **3 service files** created
- **~423 lines** of business logic
- **Match algorithm** handles duplicate digits correctly
- **Turn management** ensures fair play
- **Win detection** triggers game completion
- **All validations** throw appropriate exceptions
