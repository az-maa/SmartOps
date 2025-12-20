from app.repositories.notification_repository import NotificationRepository
from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
    NotificationListResponse,
    NotificationStats
)
from app.core.exceptions import NotFoundException, ForbiddenException
from typing import Optional


class NotificationService:
    def __init__(self, notification_repo: NotificationRepository):
        self.notification_repo = notification_repo
    
    async def create_notification(
        self,
        notification_data: NotificationCreate
    ) -> NotificationResponse:
        """Create a notification (internal use)"""
        notification = await self.notification_repo.create_notification(
            user_id=notification_data.user_id,
            title=notification_data.title,
            message=notification_data.message,
            type=notification_data.type,
            severity=notification_data.severity,
            related_id=notification_data.related_id,
            related_type=notification_data.related_type
        )
        
        return NotificationResponse.model_validate(notification)
    
    async def get_user_notifications(
        self,
        user_id: str,
        is_read: Optional[bool] = None,
        type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> NotificationListResponse:
        """Get user's notifications"""
        notifications = await self.notification_repo.get_user_notifications(
            user_id=user_id,
            is_read=is_read,
            type=type,
            limit=limit,
            offset=offset
        )
        
        total = await self.notification_repo.get_notification_count(
            user_id=user_id,
            is_read=is_read,
            type=type
        )
        
        unread_count = await self.notification_repo.get_notification_count(
            user_id=user_id,
            is_read=False
        )
        
        return NotificationListResponse(
            notifications=[NotificationResponse.model_validate(n) for n in notifications],
            total=total,
            unread_count=unread_count
        )
    
    async def mark_as_read(
        self,
        notification_id: str,
        user_id: str
    ) -> NotificationResponse:
        """Mark notification as read"""
        notification = await self.notification_repo.mark_as_read(notification_id, user_id)
        return NotificationResponse.model_validate(notification)
    
    async def mark_all_as_read(self, user_id: str) -> dict:
        """Mark all notifications as read"""
        count = await self.notification_repo.mark_all_as_read(user_id)
        return {"marked_as_read": count}
    
    async def delete_notification(
        self,
        notification_id: str,
        user_id: str
    ) -> bool:
        """Delete notification"""
        return await self.notification_repo.delete_notification(notification_id, user_id)
    
    async def get_stats(self, user_id: str) -> NotificationStats:
        """Get notification statistics"""
        stats = await self.notification_repo.get_notification_stats(user_id)
        return NotificationStats(**stats)