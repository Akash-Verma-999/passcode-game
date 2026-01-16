from typing import Optional, Dict, List

from app.models.game import Game
from app.models.player import Player
from app.models.guess import Guess


# In-memory storage dictionaries
games_db: Dict[str, Game] = {}
players_db: Dict[str, Player] = {}
game_guesses_db: Dict[str, List[Guess]] = {}


# ==================== GAME CRUD ====================

def create_game(game: Game) -> Game:
    """Store a new game in the database."""
    games_db[game.game_id] = game
    game_guesses_db[game.game_id] = []
    return game


def get_game(game_id: str) -> Optional[Game]:
    """Retrieve a game by its ID."""
    return games_db.get(game_id)


def update_game(game: Game) -> Game:
    """Update an existing game."""
    games_db[game.game_id] = game
    return game


def delete_game(game_id: str) -> bool:
    """Delete a game and its associated data."""
    if game_id in games_db:
        del games_db[game_id]
        if game_id in game_guesses_db:
            del game_guesses_db[game_id]
        return True
    return False


def get_all_games() -> List[Game]:
    """Retrieve all games."""
    return list(games_db.values())


def get_games_by_status(status: str) -> List[Game]:
    """Retrieve games filtered by status."""
    return [game for game in games_db.values() if game.status.value == status]


# ==================== PLAYER CRUD ====================

def create_player(player: Player) -> Player:
    """Store a new player in the database."""
    players_db[player.player_id] = player
    return player


def get_player(player_id: str) -> Optional[Player]:
    """Retrieve a player by their ID."""
    return players_db.get(player_id)


def update_player(player: Player) -> Player:
    """Update an existing player."""
    players_db[player.player_id] = player
    return player


def delete_player(player_id: str) -> bool:
    """Delete a player."""
    if player_id in players_db:
        del players_db[player_id]
        return True
    return False


# ==================== GUESS CRUD ====================

def add_guess(guess: Guess) -> Guess:
    """Add a guess to a game's history."""
    if guess.game_id not in game_guesses_db:
        game_guesses_db[guess.game_id] = []
    game_guesses_db[guess.game_id].append(guess)
    return guess


def get_guesses_by_game(game_id: str) -> List[Guess]:
    """Retrieve all guesses for a specific game."""
    return game_guesses_db.get(game_id, [])


def get_guesses_by_player(game_id: str, player_id: str) -> List[Guess]:
    """Retrieve all guesses made by a specific player in a game."""
    guesses = game_guesses_db.get(game_id, [])
    return [g for g in guesses if g.guesser_player_id == player_id]


def get_guess_count(game_id: str) -> int:
    """Get the total number of guesses in a game."""
    return len(game_guesses_db.get(game_id, []))


# ==================== UTILITY FUNCTIONS ====================

def clear_all_data() -> None:
    """Clear all data from storage (useful for testing)."""
    games_db.clear()
    players_db.clear()
    game_guesses_db.clear()


def get_player_by_game(game_id: str, player_id: str) -> Optional[Player]:
    """Get a player if they belong to the specified game."""
    game = get_game(game_id)
    if not game:
        return None
    
    if game.player_1 and game.player_1.player_id == player_id:
        return game.player_1
    if game.player_2 and game.player_2.player_id == player_id:
        return game.player_2
    
    return None


def is_player_in_game(game_id: str, player_id: str) -> bool:
    """Check if a player belongs to a specific game."""
    return get_player_by_game(game_id, player_id) is not None
