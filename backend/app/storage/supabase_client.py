from typing import Optional
from supabase import create_client, Client
from app.config import settings


_supabase_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """Get or create the Supabase client singleton."""
    global _supabase_client
    
    if _supabase_client is None:
        if not settings.supabase_url or not settings.supabase_key:
            raise ValueError(
                "Supabase credentials not configured. "
                "Please set SUPABASE_URL and SUPABASE_KEY in your .env file."
            )
        _supabase_client = create_client(settings.supabase_url, settings.supabase_key)
    
    return _supabase_client
