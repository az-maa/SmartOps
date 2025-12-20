from fastapi import APIRouter, Depends, Query
from supabase import Client
from app.schemas.server import ServerCreate, ServerUpdate, ServerResponse, ServerListResponse
from app.services.server_service import ServerService
from app.repositories.server_repository import ServerRepository
from app.database.supabase import get_supabase
from app.core.dependencies import get_current_user_id

router = APIRouter()


def get_server_service(supabase: Client = Depends(get_supabase)) -> ServerService:
    """Dependency to get ServerService instance"""
    server_repo = ServerRepository(supabase)
    return ServerService(server_repo)


@router.post("", response_model=ServerResponse, status_code=201)
async def create_server(
    server_data: ServerCreate,
    user_id: str = Depends(get_current_user_id),
    server_service: ServerService = Depends(get_server_service)
):
    """
    **Create a new server**
    
    - **name**: Server name (1-100 characters)
    - **ip**: Server IP address (IPv4 or IPv6)
    
    Returns server info with generated API key for agent authentication
    
    Requires authentication token
    """
    return await server_service.create_server(user_id, server_data)


@router.get("", response_model=ServerListResponse)
async def get_my_servers(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    user_id: str = Depends(get_current_user_id),
    server_service: ServerService = Depends(get_server_service)
):
    """
    **Get all your servers**
    
    Returns paginated list of all servers owned by current user
    
    Requires authentication token
    """
    return await server_service.get_user_servers(user_id, limit, offset)


@router.get("/{server_id}", response_model=ServerResponse)
async def get_server(
    server_id: str,
    user_id: str = Depends(get_current_user_id),
    server_service: ServerService = Depends(get_server_service)
):
    """
    **Get specific server by ID**
    
    Returns server details (only if you own it)
    
    Requires authentication token
    """
    return await server_service.get_server(server_id, user_id)


@router.put("/{server_id}", response_model=ServerResponse)
async def update_server(
    server_id: str,
    update_data: ServerUpdate,
    user_id: str = Depends(get_current_user_id),
    server_service: ServerService = Depends(get_server_service)
):
    """
    **Update server information**
    
    All fields are optional:
    - **name**: Updated server name
    - **ip**: Updated IP address
    - **status**: Updated status (online/offline/warning)
    
    Requires authentication token
    """
    return await server_service.update_server(server_id, user_id, update_data)


@router.delete("/{server_id}")
async def delete_server(
    server_id: str,
    user_id: str = Depends(get_current_user_id),
    server_service: ServerService = Depends(get_server_service)
):
    """
    **Delete server (PERMANENT)**
    
    This will also delete all associated metrics, anomalies, and predictions
    
    Requires authentication token
    """
    await server_service.delete_server(server_id, user_id)
    return {"message": "Server deleted successfully"}