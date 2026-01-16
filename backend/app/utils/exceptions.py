class GameNotFoundError(Exception):
    """Raised when game_id doesn't exist."""
    pass


class PlayerNotFoundError(Exception):
    """Raised when player_id doesn't exist."""
    pass


class GameFullError(Exception):
    """Raised when trying to join a game with 2 players."""
    pass


class NotYourTurnError(Exception):
    """Raised when player tries to guess out of turn."""
    pass


class GameNotStartedError(Exception):
    """Raised when trying to guess before both players lock numbers."""
    pass


class NumberAlreadyLockedError(Exception):
    """Raised when trying to change locked number."""
    pass


class InvalidNumberFormatError(Exception):
    """Raised when number is not 4 digits."""
    pass


class GameAlreadyCompletedError(Exception):
    """Raised when trying to play a finished game."""
    pass


class PlayerNotInGameError(Exception):
    """Raised when player doesn't belong to the game."""
    pass
