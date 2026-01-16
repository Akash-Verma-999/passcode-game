from datetime import datetime
from pydantic import BaseModel, Field


class Guess(BaseModel):
    guess_id: str = Field(..., description="Unique identifier for the guess")
    game_id: str = Field(..., description="Reference to the game")
    guesser_player_id: str = Field(..., description="Player who made the guess")
    target_player_id: str = Field(..., description="Player whose number is being guessed")
    guessed_number: str = Field(..., description="The 4-digit guess")
    correct_digits: int = Field(..., ge=0, le=4, description="Count of digits present in target's number")
    correct_positions: int = Field(..., ge=0, le=4, description="Count of digits in exact position")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the guess was made")
    turn_number: int = Field(..., ge=1, description="Which turn this guess was made on")
