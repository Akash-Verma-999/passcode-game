from typing import Optional, List
from pydantic import BaseModel, Field


class CreateGameResponse(BaseModel):
    game_id: str
    player_id: str
    status: str
    message: str


class JoinGameResponse(BaseModel):
    game_id: str
    player_id: str
    status: str
    message: str


class LockNumberResponse(BaseModel):
    player_id: str
    is_ready: bool
    message: str
    game_status: str


class GuessResponse(BaseModel):
    guess_id: str
    guessed_number: str
    correct_digits: int
    correct_positions: int
    is_winner: bool
    next_turn: Optional[str] = None
    winner_id: Optional[str] = None
    message: Optional[str] = None
    turn_number: int


class PlayerInfo(BaseModel):
    player_id: str
    name: str
    is_ready: bool


class GameStatusResponse(BaseModel):
    game_id: str
    status: str
    player_1: PlayerInfo
    player_2: Optional[PlayerInfo] = None
    current_turn: Optional[str] = None
    turn_count: int
    winner_id: Optional[str] = None


class GuessDetail(BaseModel):
    guess_id: str
    guesser: str
    guessed_number: str
    correct_digits: int
    correct_positions: int
    turn_number: int


class GuessHistoryResponse(BaseModel):
    game_id: str
    total_guesses: int
    guesses: List[GuessDetail]


class ErrorResponse(BaseModel):
    detail: str
    error_code: str
