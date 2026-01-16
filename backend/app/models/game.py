from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field

from app.models.player import Player
from app.models.guess import Guess


class GameStatus(str, Enum):
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Game(BaseModel):
    game_id: str = Field(..., description="Unique game identifier")
    player_1: Player = Field(..., description="First player (game creator)")
    player_2: Optional[Player] = Field(default=None, description="Second player")
    current_turn: Optional[str] = Field(default=None, description="player_id of whose turn it is")
    status: GameStatus = Field(default=GameStatus.WAITING, description="Current game status")
    winner_id: Optional[str] = Field(default=None, description="player_id of winner")
    guesses: List[Guess] = Field(default_factory=list, description="History of all guesses")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Game creation timestamp")
    turn_count: int = Field(default=0, description="Total turns played")
