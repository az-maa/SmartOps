from supabase import create_client, Client
import os
from dotenv import load_dotenv
from typing import Optional, Dict, List
from datetime import datetime

load_dotenv()

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

class Database:
    """Simple database wrapper for Supabase"""
    
    @staticmethod
    def create_user(email: str, password_hash: str) -> Dict:
        """Create new user"""
        result = supabase.table("users").insert({
            "email": email,
            "password_hash": password_hash
        }).execute()
        return result.data[0] if result.data else None
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict]:
        """Get user by email"""
        result = supabase.table("users").select("*").eq("email", email).execute()
        return result.data[0] if result.data else None
    
    @staticmethod
    def create_server(user_id: str, name: str, ip: str, api_key: str) -> Dict:
        """Create new server"""
        result = supabase.table("servers").insert({
            "user_id": user_id,
            "name": name,
            "ip": ip,
            "api_key": api_key
        }).execute()
        return result.data[0] if result.data else None
    
    @staticmethod
    def get_user_servers(user_id: str) -> List[Dict]:
        """Get all servers for a user"""
        result = supabase.table("servers").select("*").eq("user_id", user_id).execute()
        return result.data
    
    @staticmethod
    def get_server(server_id: str) -> Optional[Dict]:
        """Get server by ID"""
        result = supabase.table("servers").select("*").eq("id", server_id).execute()
        return result.data[0] if result.data else None
    
    @staticmethod
    def delete_server(server_id: str) -> bool:
        """Delete server"""
        supabase.table("servers").delete().eq("id", server_id).execute()
        return True
    
    @staticmethod
    def insert_metrics(server_id: str, metrics: Dict) -> Dict:
        """Insert metrics"""
        data = {
            "server_id": server_id,
            "timestamp": metrics.get("timestamp", datetime.now().isoformat()),
            "cpu_percent": metrics.get("cpu_percent"),
            "ram_percent": metrics.get("ram_percent"),
            "disk_read": metrics.get("disk_read"),
            "disk_write": metrics.get("disk_write"),
            "net_sent": metrics.get("net_sent"),
            "net_recv": metrics.get("net_recv")
        }
        result = supabase.table("metrics").insert(data).execute()
        return result.data[0] if result.data else None
    
    @staticmethod
    def get_metrics(server_id: str, limit: int = 100) -> List[Dict]:
        """Get recent metrics for server"""
        result = (supabase.table("metrics")
                 .select("*")
                 .eq("server_id", server_id)
                 .order("timestamp", desc=True)
                 .limit(limit)
                 .execute())
        return result.data
    
    @staticmethod
    def insert_anomaly(server_id: str, anomaly: Dict) -> Dict:
        """Insert anomaly"""
        data = {
            "server_id": server_id,
            "timestamp": anomaly.get("timestamp"),
            "type": anomaly.get("type"),
            "severity": anomaly.get("severity"),
            "explanation": anomaly.get("explanation"),
            "metrics": anomaly.get("metrics")
        }
        result = supabase.table("anomalies").insert(data).execute()
        return result.data[0] if result.data else None
    
    @staticmethod
    def get_anomalies(server_id: str, limit: int = 50) -> List[Dict]:
        """Get anomalies for server"""
        result = (supabase.table("anomalies")
                 .select("*")
                 .eq("server_id", server_id)
                 .order("timestamp", desc=True)
                 .limit(limit)
                 .execute())
        return result.data
    
    @staticmethod
    def insert_prediction(server_id: str, forecast: List[Dict]) -> Dict:
        """Insert prediction"""
        data = {
            "server_id": server_id,
            "forecast": forecast
        }
        result = supabase.table("predictions").insert(data).execute()
        return result.data[0] if result.data else None
    
    @staticmethod
    def get_latest_prediction(server_id: str) -> Optional[Dict]:
        """Get latest prediction for server"""
        result = (supabase.table("predictions")
                 .select("*")
                 .eq("server_id", server_id)
                 .order("created_at", desc=True)
                 .limit(1)
                 .execute())
        return result.data[0] if result.data else None

# Export instance
db = Database()