from typing import Optional, List, Tuple
from datetime import datetime

from app.models.game import Game, GameStatus
from app.models.player import Player
from app.storage import store
from app.utils.id_generator import generate_game_id, generate_player_id
from app.utils.exceptions import (
    GameNotFoundError,
    PlayerNotFoundError,
    GameFullError,
    GameNotStartedError,
    NumberAlreadyLockedError,
    GameAlreadyCompletedError,
    PlayerNotInGameError,
)


def create_new_game(player_name: str) -> Tuple[Game, str]:
    """
    Create a new game with the first player.
    Returns (game, player_id).
    """
    player_id = generate_player_id()
    player = Player(
        player_id=player_id,
        name=player_name,
        secret_number=None,
        is_ready=False
    )
    store.create_player(player)
    
    game_id = generate_game_id()
    game = Game(
        game_id=game_id,
        player_1=player,
        player_2=None,
        current_turn=None,
        status=GameStatus.WAITING,
        winner_id=None,
        guesses=[],
        created_at=datetime.utcnow(),
        turn_count=0
    )
    store.create_game(game)
    
    return game, player_id


def join_game(game_id: str, player_name: str) -> Tuple[Game, str]:
    """
    Join an existing game as player 2.
    Returns (game, player_id).
    """
    game = store.get_game(game_id)
    if not game:
        raise GameNotFoundError(f"Game with ID '{game_id}' not found")
    
    if game.player_2 is not None:
        raise GameFullError("Game already has two players")
    
    if game.status == GameStatus.COMPLETED:
        raise GameAlreadyCompletedError("Cannot join a completed game")
    
    player_id = generate_player_id()
    player = Player(
        player_id=player_id,
        name=player_name,
        secret_number=None,
        is_ready=False
    )
    store.create_player(player)
    
    game.player_2 = player
    store.update_game(game)
    
    return game, player_id


def lock_player_number(game_id: str, player_id: str, secret_number: str) -> Game:
    """
    Lock a player's secret number.
    If both players have locked, start the game.
    """
    game = store.get_game(game_id)
    if not game:
        raise GameNotFoundError(f"Game with ID '{game_id}' not found")
    
    if game.status == GameStatus.COMPLETED:
        raise GameAlreadyCompletedError("Game is already completed")
    
    # Find the player in the game
    if game.player_1 and game.player_1.player_id == player_id:
        if game.player_1.is_ready:
            raise NumberAlreadyLockedError("Your number is already locked")
        game.player_1.secret_number = secret_number
        game.player_1.is_ready = True
    elif game.player_2 and game.player_2.player_id == player_id:
        if game.player_2.is_ready:
            raise NumberAlreadyLockedError("Your number is already locked")
        game.player_2.secret_number = secret_number
        game.player_2.is_ready = True
    else:
        raise PlayerNotInGameError(f"Player '{player_id}' is not in this game")
    
    # Check if both players are ready to start the game
    if (game.player_1 and game.player_1.is_ready and 
        game.player_2 and game.player_2.is_ready):
        game.status = GameStatus.IN_PROGRESS
        game.current_turn = game.player_1.player_id  # Player 1 goes first
    
    store.update_game(game)
    return game


def get_game_status(game_id: str) -> Game:
    """Get the current game status."""
    game = store.get_game(game_id)
    if not game:
        raise GameNotFoundError(f"Game with ID '{game_id}' not found")
    return game


def delete_game_by_id(game_id: str) -> bool:
    """Delete a game by its ID."""
    game = store.get_game(game_id)
    if not game:
        raise GameNotFoundError(f"Game with ID '{game_id}' not found")
    return store.delete_game(game_id)


def list_all_games() -> List[Game]:
    """List all games."""
    return store.get_all_games()


# ==================== TURN MANAGEMENT ====================

def get_current_turn(game_id: str) -> Optional[str]:
    """Get the player_id of whose turn it is."""
    game = store.get_game(game_id)
    if not game:
        raise GameNotFoundError(f"Game with ID '{game_id}' not found")
    return game.current_turn


def validate_turn(game: Game, player_id: str) -> bool:
    """Check if it's the given player's turn."""
    return game.current_turn == player_id


def switch_turn(game: Game) -> str:
    """
    Switch turn to the other player.
    Returns the new current_turn player_id.
    """
    if game.current_turn == game.player_1.player_id:
        game.current_turn = game.player_2.player_id
    else:
        game.current_turn = game.player_1.player_id
    
    return game.current_turn


def get_opponent(game: Game, player_id: str) -> Player:
    """Get the opponent player."""
    if game.player_1.player_id == player_id:
        return game.player_2
    return game.player_1


# ==================== WIN CONDITION ====================

def check_winner(correct_positions: int) -> bool:
    """Returns True if all 4 positions are correct (player wins)."""
    return correct_positions == 4


def set_winner(game: Game, winner_id: str) -> Game:
    """Set the winner and mark game as completed."""
    game.winner_id = winner_id
    game.status = GameStatus.COMPLETED
    store.update_game(game)
    return game
