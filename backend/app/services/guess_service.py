from datetime import datetime
from typing import List

from app.models.game import Game, GameStatus
from app.models.guess import Guess
from app.storage import store
from app.services.game_service import (
    validate_turn,
    switch_turn,
    get_opponent,
    check_winner,
    set_winner,
)
from app.utils.id_generator import generate_guess_id
from app.utils.exceptions import (
    GameNotFoundError,
    NotYourTurnError,
    GameNotStartedError,
    GameAlreadyCompletedError,
    PlayerNotInGameError,
)


def calculate_match(secret: str, guess: str) -> dict:
    """
    Calculate how many digits match between secret and guess.
    
    Returns:
        {
            "correct_digits": int,    # Digits present in secret (regardless of position)
            "correct_positions": int  # Digits in exact correct position
        }
    
    Example:
        secret = "1234", guess = "1325"
        correct_positions = 1 (only '1' at position 0)
        correct_digits = 3 ('1', '2', '3' are present)
    """
    correct_positions = 0
    
    # Count exact position matches
    for i in range(4):
        if secret[i] == guess[i]:
            correct_positions += 1
    
    # Count digit matches (regardless of position)
    # For each digit, take minimum of occurrences in both numbers
    secret_digit_count = {}
    guess_digit_count = {}
    
    for digit in secret:
        secret_digit_count[digit] = secret_digit_count.get(digit, 0) + 1
    
    for digit in guess:
        guess_digit_count[digit] = guess_digit_count.get(digit, 0) + 1
    
    correct_digits = 0
    for digit in guess_digit_count:
        if digit in secret_digit_count:
            correct_digits += min(secret_digit_count[digit], guess_digit_count[digit])
    
    return {
        "correct_digits": correct_digits,
        "correct_positions": correct_positions
    }


def process_guess(game_id: str, player_id: str, guessed_number: str) -> dict:
    """
    Process a player's guess.
    
    Returns:
        {
            "guess_id": str,
            "guessed_number": str,
            "correct_digits": int,
            "correct_positions": int,
            "is_winner": bool,
            "next_turn": str | None,
            "winner_id": str | None,
            "turn_number": int
        }
    """
    game = store.get_game(game_id)
    if not game:
        raise GameNotFoundError(f"Game with ID '{game_id}' not found")
    
    # Validate game state
    if game.status == GameStatus.WAITING:
        raise GameNotStartedError("Game has not started. Both players must lock their numbers first.")
    
    if game.status == GameStatus.COMPLETED:
        raise GameAlreadyCompletedError("Game is already completed")
    
    # Validate player is in game
    is_player_1 = game.player_1 and game.player_1.player_id == player_id
    is_player_2 = game.player_2 and game.player_2.player_id == player_id
    
    if not is_player_1 and not is_player_2:
        raise PlayerNotInGameError(f"Player '{player_id}' is not in this game")
    
    # Validate it's the player's turn
    if not validate_turn(game, player_id):
        raise NotYourTurnError(f"It's not your turn. Current turn: {game.current_turn}")
    
    # Get opponent's secret number
    opponent = get_opponent(game, player_id)
    secret_number = opponent.secret_number
    
    # Calculate match
    match_result = calculate_match(secret_number, guessed_number)
    
    # Increment turn count
    game.turn_count += 1
    
    # Create guess record
    guess = Guess(
        guess_id=generate_guess_id(),
        game_id=game_id,
        guesser_player_id=player_id,
        target_player_id=opponent.player_id,
        guessed_number=guessed_number,
        correct_digits=match_result["correct_digits"],
        correct_positions=match_result["correct_positions"],
        timestamp=datetime.utcnow(),
        turn_number=game.turn_count
    )
    store.add_guess(guess)
    
    # Add guess to game's guesses list
    game.guesses.append(guess)
    
    # Check for winner
    is_winner = check_winner(match_result["correct_positions"])
    
    if is_winner:
        set_winner(game, player_id)
        return {
            "guess_id": guess.guess_id,
            "guessed_number": guessed_number,
            "correct_digits": match_result["correct_digits"],
            "correct_positions": match_result["correct_positions"],
            "is_winner": True,
            "next_turn": None,
            "winner_id": player_id,
            "turn_number": game.turn_count
        }
    
    # Switch turn
    next_turn = switch_turn(game)
    store.update_game(game)
    
    return {
        "guess_id": guess.guess_id,
        "guessed_number": guessed_number,
        "correct_digits": match_result["correct_digits"],
        "correct_positions": match_result["correct_positions"],
        "is_winner": False,
        "next_turn": next_turn,
        "winner_id": None,
        "turn_number": game.turn_count
    }


def get_game_guesses(game_id: str) -> List[Guess]:
    """Get all guesses for a game."""
    game = store.get_game(game_id)
    if not game:
        raise GameNotFoundError(f"Game with ID '{game_id}' not found")
    return store.get_guesses_by_game(game_id)


def get_player_guesses(game_id: str, player_id: str) -> List[Guess]:
    """Get all guesses made by a specific player in a game."""
    game = store.get_game(game_id)
    if not game:
        raise GameNotFoundError(f"Game with ID '{game_id}' not found")
    return store.get_guesses_by_player(game_id, player_id)
