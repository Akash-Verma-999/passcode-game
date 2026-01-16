from fastapi import APIRouter, Query
from typing import Optional

from app.schemas.requests import MakeGuessRequest
from app.schemas.responses import (
    GuessResponse,
    GuessHistoryResponse,
    GuessDetail,
)
from app.services.guess_service import (
    process_guess,
    get_game_guesses,
    get_player_guesses,
)
from app.services.game_service import get_current_turn, get_game_status

router = APIRouter(prefix="/games", tags=["Gameplay"])


@router.post("/{game_id}/guess", response_model=GuessResponse)
async def make_guess(game_id: str, request: MakeGuessRequest):
    """
    Make a guess for the opponent's secret number.
    
    - Game must be in progress
    - It must be your turn
    - Guess must be exactly 4 digits
    
    Returns:
    - correct_digits: How many digits from your guess exist in opponent's number
    - correct_positions: How many digits are in the exact correct position
    - is_winner: True if you guessed correctly (all 4 positions match)
    """
    result = process_guess(game_id, request.player_id, request.guessed_number)
    
    message = None
    if result["is_winner"]:
        message = "Congratulations! You guessed the correct number and won the game!"
    
    return GuessResponse(
        guess_id=result["guess_id"],
        guessed_number=result["guessed_number"],
        correct_digits=result["correct_digits"],
        correct_positions=result["correct_positions"],
        is_winner=result["is_winner"],
        next_turn=result["next_turn"],
        winner_id=result["winner_id"],
        message=message,
        turn_number=result["turn_number"]
    )


@router.get("/{game_id}/guesses", response_model=GuessHistoryResponse)
async def get_guesses(
    game_id: str,
    player_id: Optional[str] = Query(None, description="Filter guesses by player ID")
):
    """
    Get the history of guesses in a game.
    
    Optionally filter by player_id to see only one player's guesses.
    """
    if player_id:
        guesses = get_player_guesses(game_id, player_id)
    else:
        guesses = get_game_guesses(game_id)
    
    # Get game to resolve player names
    game = get_game_status(game_id)
    
    # Build player_id to name mapping
    player_names = {game.player_1.player_id: game.player_1.name}
    if game.player_2:
        player_names[game.player_2.player_id] = game.player_2.name
    
    guess_details = []
    for guess in guesses:
        guess_details.append(GuessDetail(
            guess_id=guess.guess_id,
            guesser=player_names.get(guess.guesser_player_id, "Unknown"),
            guessed_number=guess.guessed_number,
            correct_digits=guess.correct_digits,
            correct_positions=guess.correct_positions,
            turn_number=guess.turn_number
        ))
    
    return GuessHistoryResponse(
        game_id=game_id,
        total_guesses=len(guess_details),
        guesses=guess_details
    )


@router.get("/{game_id}/turn")
async def get_turn_info(game_id: str):
    """
    Get current turn information.
    
    Returns whose turn it is and the current turn count.
    """
    game = get_game_status(game_id)
    
    current_player_name = None
    if game.current_turn:
        if game.player_1.player_id == game.current_turn:
            current_player_name = game.player_1.name
        elif game.player_2 and game.player_2.player_id == game.current_turn:
            current_player_name = game.player_2.name
    
    return {
        "game_id": game_id,
        "current_turn": game.current_turn,
        "current_player_name": current_player_name,
        "turn_count": game.turn_count,
        "game_status": game.status.value
    }
