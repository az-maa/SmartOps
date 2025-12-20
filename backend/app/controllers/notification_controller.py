from fastapi import APIRouter, Depends, Query
from supabase import Client
from app.schemas.notification import (
    NotificationResponse,
    NotificationListResponse,
    NotificationStats
)
from app.services.notification_service import NotificationService
from app.repositories.notification_repository import NotificationRepository
from app.database.supabase import get_supabase
from app.core.dependencies import get_current_user_id
from typing import Optional

router = APIRouter()


def get_notification_service(supabase: Client = Depends(get_supabase)) -> NotificationService:
    """Dependency to get NotificationService instance"""
    notification_repo = NotificationRepository(supabase)
    return NotificationService(notification_repo)


@router.get("", response_model=NotificationListResponse)
async def get_my_notifications(
    is_read: Optional[bool] = Query(None, description="Filter by read status"),
    type: Optional[str] = Query(None, pattern="^(anomaly|prediction|server|system)$"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user_id: str = Depends(get_current_user_id),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    **Get your notifications**
    
    Filters:
    - **is_read**: true (read only), false (unread only), null (all)
    - **type**: anomaly, prediction, server, system
    - **limit**: Max results per page (default: 50)
    - **offset**: Pagination offset
    
    Requires authentication token
    """
    return await notification_service.get_user_notifications(
        user_id=user_id,
        is_read=is_read,
        type=type,
        limit=limit,
        offset=offset
    )


@router.get("/unread/count")
async def get_unread_count(
    user_id: str = Depends(get_current_user_id),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    **Get unread notification count**
    
    Returns just the count of unread notifications (for badge display)
    
    Requires authentication token
    """
    result = await notification_service.get_user_notifications(user_id=user_id, limit=1)
    return {"unread_count": result.unread_count}


@router.get("/stats", response_model=NotificationStats)
async def get_notification_stats(
    user_id: str = Depends(get_current_user_id),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    **Get notification statistics**
    
    Returns counts by type and severity
    
    Requires authentication token
    """
    return await notification_service.get_stats(user_id)


@router.put("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_as_read(
    notification_id: str,
    user_id: str = Depends(get_current_user_id),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    **Mark notification as read**
    
    Requires authentication token
    """
    return await notification_service.mark_as_read(notification_id, user_id)


@router.put("/read-all")
async def mark_all_as_read(
    user_id: str = Depends(get_current_user_id),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    **Mark all notifications as read**
    
    Requires authentication token
    """
    return await notification_service.mark_all_as_read(user_id)


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    user_id: str = Depends(get_current_user_id),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    **Delete notification**
    
    Requires authentication token
    """
    await notification_service.delete_notification(notification_id, user_id)
    return {"message": "Notification deleted successfully"}