from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routers import games, players, gameplay
from app.utils.exceptions import (
    GameNotFoundError,
    PlayerNotFoundError,
    GameFullError,
    NotYourTurnError,
    GameNotStartedError,
    NumberAlreadyLockedError,
    InvalidNumberFormatError,
    GameAlreadyCompletedError,
    PlayerNotInGameError,
)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A two-player passcode guessing game API",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)


@app.get("/")
async def root():
    return {
        "message": "Welcome to Passcode Guessing Game API",
        "version": settings.app_version,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# ==================== REGISTER ROUTERS ====================

app.include_router(games.router)
app.include_router(players.router)
app.include_router(gameplay.router)


# ==================== EXCEPTION HANDLERS ====================

@app.exception_handler(GameNotFoundError)
async def game_not_found_handler(request: Request, exc: GameNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc) or "Game not found", "error_code": "GAME_NOT_FOUND"}
    )


@app.exception_handler(PlayerNotFoundError)
async def player_not_found_handler(request: Request, exc: PlayerNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc) or "Player not found", "error_code": "PLAYER_NOT_FOUND"}
    )


@app.exception_handler(GameFullError)
async def game_full_handler(request: Request, exc: GameFullError):
    return JSONResponse(
        status_code=409,
        content={"detail": str(exc) or "Game is full", "error_code": "GAME_FULL"}
    )


@app.exception_handler(NotYourTurnError)
async def not_your_turn_handler(request: Request, exc: NotYourTurnError):
    return JSONResponse(
        status_code=409,
        content={"detail": str(exc) or "It's not your turn", "error_code": "NOT_YOUR_TURN"}
    )


@app.exception_handler(GameNotStartedError)
async def game_not_started_handler(request: Request, exc: GameNotStartedError):
    return JSONResponse(
        status_code=409,
        content={"detail": str(exc) or "Game has not started yet", "error_code": "GAME_NOT_STARTED"}
    )


@app.exception_handler(NumberAlreadyLockedError)
async def number_already_locked_handler(request: Request, exc: NumberAlreadyLockedError):
    return JSONResponse(
        status_code=409,
        content={"detail": str(exc) or "Number is already locked", "error_code": "NUMBER_ALREADY_LOCKED"}
    )


@app.exception_handler(InvalidNumberFormatError)
async def invalid_number_format_handler(request: Request, exc: InvalidNumberFormatError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc) or "Invalid number format", "error_code": "INVALID_NUMBER_FORMAT"}
    )


@app.exception_handler(GameAlreadyCompletedError)
async def game_already_completed_handler(request: Request, exc: GameAlreadyCompletedError):
    return JSONResponse(
        status_code=409,
        content={"detail": str(exc) or "Game is already completed", "error_code": "GAME_ALREADY_COMPLETED"}
    )


@app.exception_handler(PlayerNotInGameError)
async def player_not_in_game_handler(request: Request, exc: PlayerNotInGameError):
    return JSONResponse(
        status_code=403,
        content={"detail": str(exc) or "Player is not in this game", "error_code": "PLAYER_NOT_IN_GAME"}
    )
