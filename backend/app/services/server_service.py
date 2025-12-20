from app.repositories.server_repository import ServerRepository
from app.schemas.server import ServerCreate, ServerUpdate, ServerResponse, ServerListResponse
from app.core.exceptions import NotFoundException, ForbiddenException


class ServerService:
    def __init__(self, server_repo: ServerRepository):
        self.server_repo = server_repo
    
    async def create_server(self, user_id: str, server_data: ServerCreate) -> ServerResponse:
        """Create a new server for the user"""
        server = await self.server_repo.create_server(
            user_id=user_id,
            name=server_data.name,
            ip=server_data.ip
        )
        
        return ServerResponse.model_validate(server)
    
    async def get_user_servers(
        self,
        user_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> ServerListResponse:
        """Get all servers for a user"""
        servers = await self.server_repo.get_servers_by_user(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        total = await self.server_repo.get_user_server_count(user_id)
        
        return ServerListResponse(
            servers=[ServerResponse.model_validate(server) for server in servers],
            total=total
        )
    
    async def get_server(self, server_id: str, user_id: str) -> ServerResponse:
        """Get a specific server (with authorization check)"""
        server = await self.server_repo.get_server_by_id(server_id)
        
        if not server:
            raise NotFoundException(detail="Server not found")
        
        # Check if user owns this server
        if str(server.user_id) != user_id:
            raise ForbiddenException(detail="You don't have access to this server")
        
        return ServerResponse.model_validate(server)
    
    async def update_server(
        self,
        server_id: str,
        user_id: str,
        update_data: ServerUpdate
    ) -> ServerResponse:
        """Update server information"""
        # Check if server exists and user owns it
        server = await self.server_repo.get_server_by_id(server_id)
        
        if not server:
            raise NotFoundException(detail="Server not found")
        
        if str(server.user_id) != user_id:
            raise ForbiddenException(detail="You don't have access to this server")
        
        # Update server
        updated_server = await self.server_repo.update_server(
            server_id=server_id,
            name=update_data.name,
            ip=update_data.ip,
            status=update_data.status
        )
        
        return ServerResponse.model_validate(updated_server)
    
    async def delete_server(self, server_id: str, user_id: str) -> bool:
        """Delete a server"""
        # Check if server exists and user owns it
        server = await self.server_repo.get_server_by_id(server_id)
        
        if not server:
            raise NotFoundException(detail="Server not found")
        
        if str(server.user_id) != user_id:
            raise ForbiddenException(detail="You don't have access to this server")
        
        # Delete server
        return await self.server_repo.delete_server(server_id)