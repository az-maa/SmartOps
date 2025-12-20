from typing import Optional, List
from supabase import Client
from app.models.notification import Notification
from app.core.exceptions import NotFoundException


class NotificationRepository:
    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.table = "notifications"
    
    async def create_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        type: str,
        severity: Optional[str] = None,
        related_id: Optional[str] = None,
        related_type: Optional[str] = None
    ) -> Notification:
        """Create a new notification"""
        data = {
            "user_id": user_id,
            "title": title,
            "message": message,
            "type": type,
        }
        
        if severity:
            data["severity"] = severity
        if related_id:
            data["related_id"] = related_id
        if related_type:
            data["related_type"] = related_type
        
        response = self.supabase.table(self.table).insert(data).execute()
        
        if not response.data:
            raise Exception("Failed to create notification")
        
        return Notification(**response.data[0])
    
    async def get_notification_by_id(self, notification_id: str) -> Optional[Notification]:
        """Get specific notification by ID"""
        response = self.supabase.table(self.table).select("*").eq("id", notification_id).execute()
        
        if not response.data:
            return None
        
        return Notification(**response.data[0])
    
    async def get_user_notifications(
        self,
        user_id: str,
        is_read: Optional[bool] = None,
        type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Notification]:
        """Get notifications for a user"""
        query = self.supabase.table(self.table).select("*").eq("user_id", user_id)
        
        # Apply filters
        if is_read is not None:
            query = query.eq("is_read", is_read)
        if type:
            query = query.eq("type", type)
        
        # Order and paginate
        response = query.order("created_at", desc=True).range(
            offset, offset + limit - 1
        ).execute()
        
        if not response.data:
            return []
        
        return [Notification(**notif_data) for notif_data in response.data]
    
    async def get_notification_count(
        self,
        user_id: str,
        is_read: Optional[bool] = None,
        type: Optional[str] = None
    ) -> int:
        """Get count of notifications"""
        query = self.supabase.table(self.table).select("id", count="exact").eq("user_id", user_id)
        
        if is_read is not None:
            query = query.eq("is_read", is_read)
        if type:
            query = query.eq("type", type)
        
        response = query.execute()
        return response.count if response.count else 0
    
    async def mark_as_read(self, notification_id: str, user_id: str) -> Notification:
        """Mark notification as read"""
        response = self.supabase.table(self.table).update({
            "is_read": True
        }).eq("id", notification_id).eq("user_id", user_id).execute()
        
        if not response.data:
            raise NotFoundException(detail="Notification not found")
        
        return Notification(**response.data[0])
    
    async def mark_all_as_read(self, user_id: str) -> int:
        """Mark all user's notifications as read"""
        response = self.supabase.table(self.table).update({
            "is_read": True
        }).eq("user_id", user_id).eq("is_read", False).execute()
        
        return len(response.data) if response.data else 0
    
    async def delete_notification(self, notification_id: str, user_id: str) -> bool:
        """Delete notification"""
        response = self.supabase.table(self.table).delete().eq(
            "id", notification_id
        ).eq("user_id", user_id).execute()
        
        if not response.data:
            raise NotFoundException(detail="Notification not found")
        
        return True
    
    async def get_notification_stats(self, user_id: str) -> dict:
        """Get notification statistics"""
        # Get all user notifications
        all_notifs = await self.get_user_notifications(user_id, limit=10000)
        
        # Calculate stats
        total = len(all_notifs)
        unread = sum(1 for n in all_notifs if not n.is_read)
        
        by_type = {}
        by_severity = {}
        
        for notif in all_notifs:
            # Count by type
            by_type[notif.type] = by_type.get(notif.type, 0) + 1
            
            # Count by severity
            if notif.severity:
                by_severity[notif.severity] = by_severity.get(notif.severity, 0) + 1
        
        return {
            "total": total,
            "unread_count": unread,
            "by_type": by_type,
            "by_severity": by_severity
        }