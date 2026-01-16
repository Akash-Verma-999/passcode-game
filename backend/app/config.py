from typing import List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Passcode Guessing Game"
    app_version: str = "1.0.0"
    debug: bool = True
    
    cors_origins: List[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]
    
    # Supabase configuration
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None
    use_supabase: bool = True  # Set to True to use Supabase instead of in-memory storage
    
    class Config:
        env_file = ".env"


settings = Settings()
