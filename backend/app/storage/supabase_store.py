from typing import Optional, List
from datetime import datetime
from dateutil import parser as date_parser

from app.models.game import Game, GameStatus
from app.models.player import Player
from app.models.guess import Guess
from app.storage.supabase_client import get_supabase_client


# ==================== PLAYER CRUD ====================

def create_player(player: Player) -> Player:
    """Store a new player in Supabase."""
    client = get_supabase_client()
    data = {
        "player_id": player.player_id,
        "name": player.name,
        "secret_number": player.secret_number,
        "is_ready": player.is_ready,
    }
    client.table("players").insert(data).execute()
    return player


def get_player(player_id: str) -> Optional[Player]:
    """Retrieve a player by their ID."""
    client = get_supabase_client()
    response = client.table("players").select("*").eq("player_id", player_id).execute()
    if response.data:
        row = response.data[0]
        return Player(
            player_id=row["player_id"],
            name=row["name"],
            secret_number=row["secret_number"],
            is_ready=row["is_ready"],
        )
    return None


def update_player(player: Player) -> Player:
    """Update an existing player."""
    client = get_supabase_client()
    data = {
        "name": player.name,
        "secret_number": player.secret_number,
        "is_ready": player.is_ready,
    }
    client.table("players").update(data).eq("player_id", player.player_id).execute()
    return player


def delete_player(player_id: str) -> bool:
    """Delete a player."""
    client = get_supabase_client()
    response = client.table("players").delete().eq("player_id", player_id).execute()
    return len(response.data) > 0


# ==================== GAME CRUD ====================

def _game_to_db(game: Game) -> dict:
    """Convert Game model to database row format."""
    return {
        "game_id": game.game_id,
        "player_1_id": game.player_1.player_id if game.player_1 else None,
        "player_2_id": game.player_2.player_id if game.player_2 else None,
        "current_turn": game.current_turn,
        "status": game.status.value,
        "winner_id": game.winner_id,
        "turn_count": game.turn_count,
        "created_at": game.created_at.isoformat(),
    }


def _db_to_game(row: dict, player_1: Optional[Player], player_2: Optional[Player], guesses: List[Guess]) -> Game:
    """Convert database row to Game model."""
    return Game(
        game_id=row["game_id"],
        player_1=player_1,
        player_2=player_2,
        current_turn=row["current_turn"],
        status=GameStatus(row["status"]),
        winner_id=row["winner_id"],
        guesses=guesses,
        created_at=date_parser.parse(row["created_at"]) if isinstance(row["created_at"], str) else row["created_at"],
        turn_count=row["turn_count"],
    )


def create_game(game: Game) -> Game:
    """Store a new game in Supabase."""
    client = get_supabase_client()
    
    # First, ensure player_1 exists in players table
    if game.player_1:
        existing = get_player(game.player_1.player_id)
        if not existing:
            create_player(game.player_1)
    
    data = _game_to_db(game)
    client.table("games").insert(data).execute()
    return game


def get_game(game_id: str) -> Optional[Game]:
    """Retrieve a game by its ID with all related data."""
    client = get_supabase_client()
    response = client.table("games").select("*").eq("game_id", game_id).execute()
    
    if not response.data:
        return None
    
    row = response.data[0]
    
    # Fetch players
    player_1 = get_player(row["player_1_id"]) if row["player_1_id"] else None
    player_2 = get_player(row["player_2_id"]) if row["player_2_id"] else None
    
    # Fetch guesses
    guesses = get_guesses_by_game(game_id)
    
    return _db_to_game(row, player_1, player_2, guesses)


def update_game(game: Game) -> Game:
    """Update an existing game."""
    client = get_supabase_client()
    
    # Update players if they exist
    if game.player_1:
        existing = get_player(game.player_1.player_id)
        if existing:
            update_player(game.player_1)
        else:
            create_player(game.player_1)
    
    if game.player_2:
        existing = get_player(game.player_2.player_id)
        if existing:
            update_player(game.player_2)
        else:
            create_player(game.player_2)
    
    data = {
        "player_1_id": game.player_1.player_id if game.player_1 else None,
        "player_2_id": game.player_2.player_id if game.player_2 else None,
        "current_turn": game.current_turn,
        "status": game.status.value,
        "winner_id": game.winner_id,
        "turn_count": game.turn_count,
    }
    client.table("games").update(data).eq("game_id", game.game_id).execute()
    return game


def delete_game(game_id: str) -> bool:
    """Delete a game and its associated guesses (cascade)."""
    client = get_supabase_client()
    response = client.table("games").delete().eq("game_id", game_id).execute()
    return len(response.data) > 0


def get_all_games() -> List[Game]:
    """Retrieve all games."""
    client = get_supabase_client()
    response = client.table("games").select("*").order("created_at", desc=True).execute()
    
    games = []
    for row in response.data:
        player_1 = get_player(row["player_1_id"]) if row["player_1_id"] else None
        player_2 = get_player(row["player_2_id"]) if row["player_2_id"] else None
        guesses = get_guesses_by_game(row["game_id"])
        games.append(_db_to_game(row, player_1, player_2, guesses))
    
    return games


def get_games_by_status(status: str) -> List[Game]:
    """Retrieve games filtered by status."""
    client = get_supabase_client()
    response = client.table("games").select("*").eq("status", status).order("created_at", desc=True).execute()
    
    games = []
    for row in response.data:
        player_1 = get_player(row["player_1_id"]) if row["player_1_id"] else None
        player_2 = get_player(row["player_2_id"]) if row["player_2_id"] else None
        guesses = get_guesses_by_game(row["game_id"])
        games.append(_db_to_game(row, player_1, player_2, guesses))
    
    return games


# ==================== GUESS CRUD ====================

def add_guess(guess: Guess) -> Guess:
    """Add a guess to a game's history."""
    client = get_supabase_client()
    data = {
        "guess_id": guess.guess_id,
        "game_id": guess.game_id,
        "guesser_player_id": guess.guesser_player_id,
        "target_player_id": guess.target_player_id,
        "guessed_number": guess.guessed_number,
        "correct_digits": guess.correct_digits,
        "correct_positions": guess.correct_positions,
        "turn_number": guess.turn_number,
        "timestamp": guess.timestamp.isoformat(),
    }
    client.table("guesses").insert(data).execute()
    return guess


def get_guesses_by_game(game_id: str) -> List[Guess]:
    """Retrieve all guesses for a specific game."""
    client = get_supabase_client()
    response = client.table("guesses").select("*").eq("game_id", game_id).order("turn_number").execute()
    
    guesses = []
    for row in response.data:
        guesses.append(Guess(
            guess_id=row["guess_id"],
            game_id=row["game_id"],
            guesser_player_id=row["guesser_player_id"],
            target_player_id=row["target_player_id"],
            guessed_number=row["guessed_number"],
            correct_digits=row["correct_digits"],
            correct_positions=row["correct_positions"],
            timestamp=date_parser.parse(row["timestamp"]) if isinstance(row["timestamp"], str) else row["timestamp"],
            turn_number=row["turn_number"],
        ))
    
    return guesses


def get_guesses_by_player(game_id: str, player_id: str) -> List[Guess]:
    """Retrieve all guesses made by a specific player in a game."""
    client = get_supabase_client()
    response = (
        client.table("guesses")
        .select("*")
        .eq("game_id", game_id)
        .eq("guesser_player_id", player_id)
        .order("turn_number")
        .execute()
    )
    
    guesses = []
    for row in response.data:
        guesses.append(Guess(
            guess_id=row["guess_id"],
            game_id=row["game_id"],
            guesser_player_id=row["guesser_player_id"],
            target_player_id=row["target_player_id"],
            guessed_number=row["guessed_number"],
            correct_digits=row["correct_digits"],
            correct_positions=row["correct_positions"],
            timestamp=date_parser.parse(row["timestamp"]) if isinstance(row["timestamp"], str) else row["timestamp"],
            turn_number=row["turn_number"],
        ))
    
    return guesses


def get_guess_count(game_id: str) -> int:
    """Get the total number of guesses in a game."""
    client = get_supabase_client()
    response = client.table("guesses").select("guess_id", count="exact").eq("game_id", game_id).execute()
    return response.count or 0


# ==================== UTILITY FUNCTIONS ====================

def clear_all_data() -> None:
    """Clear all data from storage (useful for testing)."""
    client = get_supabase_client()
    # Delete in order due to foreign key constraints
    client.table("guesses").delete().neq("guess_id", "").execute()
    client.table("games").delete().neq("game_id", "").execute()
    client.table("players").delete().neq("player_id", "").execute()


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
