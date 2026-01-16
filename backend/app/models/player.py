from typing import Optional
from pydantic import BaseModel, Field


class Player(BaseModel):
    player_id: str = Field(..., description="Unique identifier for the player")
    name: str = Field(..., min_length=1, max_length=50, description="Player display name")
    secret_number: Optional[str] = Field(default=None, description="4-digit secret number")
    is_ready: bool = Field(default=False, description="True when player has locked their number")
