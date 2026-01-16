import uuid


def generate_game_id() -> str:
    """Generate a unique game ID with 'game_' prefix."""
    return f"game_{uuid.uuid4().hex[:12]}"


def generate_player_id() -> str:
    """Generate a unique player ID with 'player_' prefix."""
    return f"player_{uuid.uuid4().hex[:12]}"


def generate_guess_id() -> str:
    """Generate a unique guess ID with 'guess_' prefix."""
    return f"guess_{uuid.uuid4().hex[:12]}"
