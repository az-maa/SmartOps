from app.repositories.anomaly_repository import AnomalyRepository
from app.repositories.server_repository import ServerRepository
from app.repositories.user_repository import UserRepository  
from app.services.email_service import email_service  
from app.schemas.anomaly import (
    AnomalyCreate,
    AnomalyResponse,
    AnomalyListResponse,
    AnomalyStats
)
from app.core.exceptions import NotFoundException, ForbiddenException
from datetime import datetime
from typing import Optional
from app.repositories.notification_repository import NotificationRepository
from app.schemas.notification import NotificationCreate

class AnomalyService:
    def __init__(self, anomaly_repo: AnomalyRepository, server_repo: ServerRepository, notification_repo: NotificationRepository,user_repo: UserRepository):
        self.anomaly_repo = anomaly_repo
        self.server_repo = server_repo
        self.notification_repo = notification_repo
        self.user_repo = user_repo
    
    async def create_anomaly(self, anomaly_data: AnomalyCreate) -> AnomalyResponse:
        """
        Create anomaly (called by AI service)
        In production, this should require special AI service authentication
        """
        # Verify server exists
        server = await self.server_repo.get_server_by_id(anomaly_data.server_id)
        if not server:
            raise NotFoundException(detail="Server not found")
        
        # Create anomaly
        anomaly = await self.anomaly_repo.create_anomaly(
            server_id=anomaly_data.server_id,
            timestamp=anomaly_data.timestamp,
            type=anomaly_data.type,
            severity=anomaly_data.severity,
            explanation=anomaly_data.explanation,
            metrics=anomaly_data.metrics
        )
        # 🔔 CREATE NOTIFICATION FOR USER
        notification_title = f"Anomaly Detected: {anomaly_data.type.replace('_', ' ').title()}"
        notification_message = f"Server '{server.name}': {anomaly_data.explanation[:200]}"
        
        await self.notification_repo.create_notification(
            user_id=str(server.user_id),
            title=notification_title,
            message=notification_message,
            type="anomaly",
            severity=anomaly_data.severity,
            related_id=str(anomaly.id),
            related_type="anomaly"
        )
        if anomaly_data.severity in ['critical', 'high']:
    # Fire and forget - don't wait for email to complete
         import asyncio
         asyncio.create_task(
         self._send_anomaly_email_async(
            user_id=str(server.user_id),
            server_name=server.name,
            anomaly_data=anomaly_data
         )
    )
        
        
        return AnomalyResponse.model_validate(anomaly)
    
    async def get_server_anomalies(
        self,
        server_id: str,
        user_id: str,
        severity: Optional[str] = None,
        from_time: Optional[datetime] = None,
        to_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> AnomalyListResponse:
        """Get anomalies for a server (with authorization)"""
        # Check authorization
        server = await self.server_repo.get_server_by_id(server_id)
        
        if not server:
            raise NotFoundException(detail="Server not found")
        
        if str(server.user_id) != user_id:
            raise ForbiddenException(detail="You don't have access to this server")
        
        # Get anomalies
        anomalies = await self.anomaly_repo.get_anomalies_by_server(
            server_id=server_id,
            severity=severity,
            from_time=from_time,
            to_time=to_time,
            limit=limit,
            offset=offset
        )
        
        total = await self.anomaly_repo.get_anomaly_count(
            server_id=server_id,
            severity=severity,
            from_time=from_time,
            to_time=to_time
        )
        
        return AnomalyListResponse(
            anomalies=[AnomalyResponse.model_validate(a) for a in anomalies],
            total=total,
            server_id=server_id
        )
    
    async def get_anomaly(
        self,
        anomaly_id: str,
        user_id: str
    ) -> AnomalyResponse:
        """Get specific anomaly (with authorization)"""
        anomaly = await self.anomaly_repo.get_anomaly_by_id(anomaly_id)
        
        if not anomaly:
            raise NotFoundException(detail="Anomaly not found")
        
        # Check if user owns the server
        server = await self.server_repo.get_server_by_id(str(anomaly.server_id))
        
        if not server or str(server.user_id) != user_id:
            raise ForbiddenException(detail="You don't have access to this anomaly")
        
        return AnomalyResponse.model_validate(anomaly)
    
    async def get_anomaly_stats(
        self,
        server_id: str,
        user_id: str,
        days: int = 7
    ) -> AnomalyStats:
        """Get anomaly statistics for a server"""
        # Check authorization
        server = await self.server_repo.get_server_by_id(server_id)
        
        if not server:
            raise NotFoundException(detail="Server not found")
        
        if str(server.user_id) != user_id:
            raise ForbiddenException(detail="You don't have access to this server")
        
        # Get stats
        stats = await self.anomaly_repo.get_anomaly_stats(server_id, days)
        
        return AnomalyStats(**stats)
    
    async def _send_anomaly_email_async(
        self,
        user_id: str,
        server_name: str,
        anomaly_data: AnomalyCreate
    ):
        """Méthode privée pour envoyer l'email en arrière-plan"""
        try:
            # Récupère l'utilisateur
            user = await self.user_repo.get_user_by_id(user_id)
            if not user or not user.email:
                print(f"⚠️  Utilisateur {user_id} non trouvé ou sans email")
                return
            
            # Envoie l'email
            success = await email_service.send_anomaly_email(
                to_email=user.email,
                user_name=user.first_name or user.email.split('@')[0],
                server_name=server_name,
                anomaly_data={
                    'type': anomaly_data.type,
                    'severity': anomaly_data.severity,
                    'timestamp': anomaly_data.timestamp,
                    'explanation': anomaly_data.explanation
                }
            )
            
            if success:
                print(f"📧 Email envoyé avec succès à {user.email}")
            else:
                print(f"❌ Échec d'envoi d'email à {user.email}")
                
        except Exception as e:
            # On catch toutes les exceptions pour ne pas bloquer la création d'anomalie
            print(f"⚠️  Erreur lors de l'envoi d'email: {e}")