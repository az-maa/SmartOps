import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any
from datetime import datetime
from app.config import get_settings

class EmailService:
    def __init__(self):
        settings = get_settings()
        self.gmail_user = settings.GMAIL_USER
        self.gmail_password = settings.GMAIL_PASSWORD
    
    async def send_anomaly_email(
        self,
        to_email: str,
        user_name: str,
        server_name: str,
        anomaly_data: Dict[str, Any]
    ) -> bool:
        """Send email for a new anomaly"""
        
        # Format date if it's a datetime object
        timestamp = anomaly_data.get('timestamp', '')
        if isinstance(timestamp, datetime):
            timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        
        subject = f"[Smart OPS] {anomaly_data.get('severity', '').upper()} Anomaly on {server_name}"
        
        body = f"""Hello {user_name},

An anomaly has been detected on server {server_name}.

Type: {anomaly_data.get('type', '')}
Severity: {anomaly_data.get('severity', '')}
Date: {timestamp}

Explanation:
{anomaly_data.get('explanation', '')}

Regards,
Smart OPS Monitoring
This is an automated email. Please do not reply."""
        
        try:
            msg = MIMEMultipart()
            msg['From'] = f"Smart OPS <{self.gmail_user}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(self.gmail_user, self.gmail_password)
                server.send_message(msg)
            
            print(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"Email sending error: {e}")
            return False

# Global instance
email_service = EmailService()