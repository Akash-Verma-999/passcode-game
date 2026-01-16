from app.models.player import Player
from app.storage import store
from app.utils.exceptions import (
    GameNotFoundError,
    PlayerNotFoundError,
    PlayerNotInGameError,
)


def get_player_info(game_id: str, player_id: str) -> dict:
    """
    Get player information (excluding secret number for security).
    
    Returns:
        {
            "player_id": str,
            "name": str,
            "is_ready": bool
        }
    """
    game = store.get_game(game_id)
    if not game:
        raise GameNotFoundError(f"Game with ID '{game_id}' not found")
    
    # Find player in game
    player = None
    if game.player_1 and game.player_1.player_id == player_id:
        player = game.player_1
    elif game.player_2 and game.player_2.player_id == player_id:
        player = game.player_2
    
    if not player:
        raise PlayerNotInGameError(f"Player '{player_id}' is not in this game")
    
    return {
        "player_id": player.player_id,
        "name": player.name,
        "is_ready": player.is_ready
    }


def get_player_by_id(player_id: str) -> Player:
    """Get a player by their ID."""
    player = store.get_player(player_id)
    if not player:
        raise PlayerNotFoundError(f"Player with ID '{player_id}' not found")
    return player


def get_both_players_info(game_id: str) -> dict:
    """
    Get information about both players in a game.
    
    Returns:
        {
            "player_1": {"player_id": str, "name": str, "is_ready": bool},
            "player_2": {"player_id": str, "name": str, "is_ready": bool} | None
        }
    """
    game = store.get_game(game_id)
    if not game:
        raise GameNotFoundError(f"Game with ID '{game_id}' not found")
    
    result = {
        "player_1": {
            "player_id": game.player_1.player_id,
            "name": game.player_1.name,
            "is_ready": game.player_1.is_ready
        },
        "player_2": None
    }
    
    if game.player_2:
        result["player_2"] = {
            "player_id": game.player_2.player_id,
            "name": game.player_2.name,
            "is_ready": game.player_2.is_ready
        }
    
    return result
