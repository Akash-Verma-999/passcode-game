from fastapi import APIRouter, status

from app.schemas.requests import JoinGameRequest, LockNumberRequest
from app.schemas.responses import (
    JoinGameResponse,
    LockNumberResponse,
    PlayerInfo,
)
from app.services.game_service import (
    join_game,
    lock_player_number,
    get_game_status,
)
from app.services.player_service import get_player_info

router = APIRouter(prefix="/games", tags=["Players"])


@router.post("/{game_id}/join", response_model=JoinGameResponse)
async def join_existing_game(game_id: str, request: JoinGameRequest):
    """
    Join an existing game as Player 2.
    
    The game must exist and not already have two players.
    """
    game, player_id = join_game(game_id, request.player_name)
    
    return JoinGameResponse(
        game_id=game.game_id,
        player_id=player_id,
        status=game.status.value,
        message="Joined game successfully. Both players need to lock their numbers to start."
    )


@router.post("/{game_id}/players/{player_id}/lock-number", response_model=LockNumberResponse)
async def lock_secret_number(game_id: str, player_id: str, request: LockNumberRequest):
    """
    Lock your secret 4-digit number.
    
    Once both players have locked their numbers, the game starts automatically.
    Player 1 (game creator) goes first.
    """
    game = lock_player_number(game_id, player_id, request.secret_number)
    
    # Check if this player is player_1 or player_2
    if game.player_1.player_id == player_id:
        is_ready = game.player_1.is_ready
    else:
        is_ready = game.player_2.is_ready
    
    message = "Number locked successfully."
    if game.status.value == "in_progress":
        message = "Number locked. Game started! Player 1 goes first."
    elif game.player_2 is None:
        message = "Number locked. Waiting for Player 2 to join."
    else:
        message = "Number locked. Waiting for opponent to lock their number."
    
    return LockNumberResponse(
        player_id=player_id,
        is_ready=is_ready,
        message=message,
        game_status=game.status.value
    )


@router.get("/{game_id}/players/{player_id}", response_model=PlayerInfo)
async def get_player(game_id: str, player_id: str):
    """
    Get player information.
    
    Note: Secret number is never exposed through this endpoint.
    """
    player_data = get_player_info(game_id, player_id)
    
    return PlayerInfo(
        player_id=player_data["player_id"],
        name=player_data["name"],
        is_ready=player_data["is_ready"]
    )
