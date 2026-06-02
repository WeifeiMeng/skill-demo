from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """用户实体"""
    id: Optional[int] = None
    name: str = ""
    email: str = ""
    password: str = ""
    role: str = "user"          # "user" | "admin"
    avatar: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
