"""
Storage module with support for both in-memory and Supabase backends.

Usage:
    from app.storage import store
    
    # All storage operations go through the 'store' module
    game = store.create_game(game)
    player = store.get_player(player_id)
    
The backend is determined by the USE_SUPABASE environment variable.
"""

from app.config import settings

if settings.use_supabase:
    from app.storage import supabase_store as store
else:
    from app.storage import memory_store as store

__all__ = ["store"]
