from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
from uuid import UUID
import re


class ServerCreate(BaseModel):
    """Schema for creating a new server"""
    name: str = Field(..., min_length=1, max_length=100, description="Server name")
    ip: str = Field(..., min_length=7, max_length=45, description="Server IP address (IPv4 or IPv6)")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate server name"""
        v = v.strip()
        if not v:
            raise ValueError('Server name cannot be empty')
        return v
    
    @field_validator('ip')
    @classmethod
    def validate_ip(cls, v: str) -> str:
        """Validate IP address format (basic validation)"""
        v = v.strip()
        # Basic IPv4 pattern
        ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        # Basic IPv6 pattern (simplified)
        ipv6_pattern = r'^([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$'
        
        if not (re.match(ipv4_pattern, v) or re.match(ipv6_pattern, v)):
            raise ValueError('Invalid IP address format')
        
        return v


class ServerUpdate(BaseModel):
    """Schema for updating server"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    ip: Optional[str] = Field(None, min_length=7, max_length=45)
    status: Optional[str] = Field(None, pattern="^(online|offline|warning)$")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('Server name cannot be empty')
        return v
    
    @field_validator('ip')
    @classmethod
    def validate_ip(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
            ipv6_pattern = r'^([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$'
            
            if not (re.match(ipv4_pattern, v) or re.match(ipv6_pattern, v)):
                raise ValueError('Invalid IP address format')
        return v


class ServerResponse(BaseModel):
    """Schema for server in responses"""
    id: UUID
    user_id: UUID
    name: str
    ip: str
    status: str
    api_key: Optional[str] = None
    created_at: datetime
    last_seen: datetime
    
    class Config:
        from_attributes = True


class ServerListResponse(BaseModel):
    """Schema for list of servers"""
    servers: list[ServerResponse]
    total: int