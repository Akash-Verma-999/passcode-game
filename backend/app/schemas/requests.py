from pydantic import BaseModel, Field


class CreateGameRequest(BaseModel):
    player_name: str = Field(..., min_length=1, max_length=50, description="Name of the player creating the game")


class JoinGameRequest(BaseModel):
    player_name: str = Field(..., min_length=1, max_length=50, description="Name of the player joining the game")


class LockNumberRequest(BaseModel):
    secret_number: str = Field(..., pattern=r"^\d{4}$", description="4-digit secret number")


class MakeGuessRequest(BaseModel):
    player_id: str = Field(..., description="ID of the player making the guess")
    guessed_number: str = Field(..., pattern=r"^\d{4}$", description="4-digit guess")
