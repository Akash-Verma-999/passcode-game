from typing import List
from fastapi import APIRouter, status

from app.schemas.requests import CreateGameRequest
from app.schemas.responses import (
    CreateGameResponse,
    GameStatusResponse,
    PlayerInfo,
)
from app.services.game_service import (
    create_new_game,
    get_game_status,
    delete_game_by_id,
    list_all_games,
)

router = APIRouter(prefix="/games", tags=["Games"])


@router.post("", response_model=CreateGameResponse, status_code=status.HTTP_201_CREATED)
async def create_game(request: CreateGameRequest):
    """
    Create a new game.
    
    The player who creates the game becomes Player 1.
    Share the game_id with another player to let them join.
    """
    game, player_id = create_new_game(request.player_name)
    
    return CreateGameResponse(
        game_id=game.game_id,
        player_id=player_id,
        status=game.status.value,
        message="Game created successfully. Share game_id with opponent to join."
    )


@router.get("", response_model=List[GameStatusResponse])
async def list_games():
    """
    List all games.
    """
    games = list_all_games()
    
    result = []
    for game in games:
        player_1_info = PlayerInfo(
            player_id=game.player_1.player_id,
            name=game.player_1.name,
            is_ready=game.player_1.is_ready
        )
        
        player_2_info = None
        if game.player_2:
            player_2_info = PlayerInfo(
                player_id=game.player_2.player_id,
                name=game.player_2.name,
                is_ready=game.player_2.is_ready
            )
        
        result.append(GameStatusResponse(
            game_id=game.game_id,
            status=game.status.value,
            player_1=player_1_info,
            player_2=player_2_info,
            current_turn=game.current_turn,
            turn_count=game.turn_count,
            winner_id=game.winner_id
        ))
    
    return result


@router.get("/{game_id}", response_model=GameStatusResponse)
async def get_game(game_id: str):
    """
    Get game details by ID.
    """
    game = get_game_status(game_id)
    
    player_1_info = PlayerInfo(
        player_id=game.player_1.player_id,
        name=game.player_1.name,
        is_ready=game.player_1.is_ready
    )
    
    player_2_info = None
    if game.player_2:
        player_2_info = PlayerInfo(
            player_id=game.player_2.player_id,
            name=game.player_2.name,
            is_ready=game.player_2.is_ready
        )
    
    return GameStatusResponse(
        game_id=game.game_id,
        status=game.status.value,
        player_1=player_1_info,
        player_2=player_2_info,
        current_turn=game.current_turn,
        turn_count=game.turn_count,
        winner_id=game.winner_id
    )


@router.delete("/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_game(game_id: str):
    """
    Delete a game by ID.
    """
    delete_game_by_id(game_id)
    return None
