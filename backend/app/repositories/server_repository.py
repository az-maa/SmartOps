from typing import Optional
from supabase import Client
from app.models.server import Server
from app.core.exceptions import ConflictException, NotFoundException
import secrets


class ServerRepository:
    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.table = "servers"
    
    def _generate_api_key(self) -> str:
        """Generate a secure API key for the server"""
        return f"sk_{secrets.token_urlsafe(32)}"
    
    async def create_server(
        self,
        user_id: str,
        name: str,
        ip: str
    ) -> Server:
        """Create a new server"""
        try:
            api_key = self._generate_api_key()
            
            response = self.supabase.table(self.table).insert({
                "user_id": user_id,
                "name": name,
                "ip": ip,
                "api_key": api_key,
                "status": "online"
            }).execute()
            
            if not response.data:
                raise Exception("Failed to create server")
            
            return Server(**response.data[0])
        except Exception as e:
            error_msg = str(e).lower()
            if "duplicate key" in error_msg or "unique" in error_msg:
                raise ConflictException(detail="Server with this name already exists")
            raise e
    
    async def get_server_by_id(self, server_id: str) -> Optional[Server]:
        """Get server by ID"""
        response = self.supabase.table(self.table).select("*").eq("id", server_id).execute()
        
        if not response.data:
            return None
        
        return Server(**response.data[0])
    
    async def get_servers_by_user(
        self,
        user_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> list[Server]:
        """Get all servers for a user"""
        response = self.supabase.table(self.table).select("*").eq(
            "user_id", user_id
        ).range(offset, offset + limit - 1).execute()
        
        if not response.data:
            return []
        
        return [Server(**server_data) for server_data in response.data]
    
    async def get_user_server_count(self, user_id: str) -> int:
        """Get total number of servers for a user"""
        response = self.supabase.table(self.table).select(
            "id", count="exact"
        ).eq("user_id", user_id).execute()
        
        return response.count if response.count else 0
    
    async def update_server(
        self,
        server_id: str,
        name: Optional[str] = None,
        ip: Optional[str] = None,
        status: Optional[str] = None
    ) -> Server:
        """Update server information"""
        # Build update data
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if ip is not None:
            update_data["ip"] = ip
        if status is not None:
            update_data["status"] = status
        
        if not update_data:
            # Nothing to update
            return await self.get_server_by_id(server_id)
        
        response = self.supabase.table(self.table).update(
            update_data
        ).eq("id", server_id).execute()
        
        if not response.data:
            raise NotFoundException(detail="Server not found")
        
        return Server(**response.data[0])
    
    async def update_last_seen(self, server_id: str) -> bool:
        """Update server's last seen timestamp"""
        from datetime import datetime
        
        response = self.supabase.table(self.table).update({
            "last_seen": datetime.utcnow().isoformat()
        }).eq("id", server_id).execute()
        
        return bool(response.data)
    
    async def delete_server(self, server_id: str) -> bool:
        """Delete server"""
        response = self.supabase.table(self.table).delete().eq("id", server_id).execute()
        
        if not response.data:
            raise NotFoundException(detail="Server not found")
        
        return True
    
    async def get_server_by_api_key(self, api_key: str) -> Optional[Server]:
        """Get server by API key (for agent authentication)"""
        response = self.supabase.table(self.table).select("*").eq("api_key", api_key).execute()
        
        if not response.data:
            return None
        
        return Server(**response.data[0])