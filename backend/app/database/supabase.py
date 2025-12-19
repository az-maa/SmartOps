from supabase import create_client, Client
from app.config import get_settings

settings = get_settings()


class SupabaseClient:
    _instance: Client = None
    
    @classmethod
    def get_client(cls) -> Client:
        if cls._instance is None:
            cls._instance = create_client(
                supabase_url=settings.SUPABASE_URL,
                supabase_key=settings.SUPABASE_KEY
            )
        return cls._instance


def get_supabase() -> Client:
    """Dependency for FastAPI routes"""
    return SupabaseClient.get_client()