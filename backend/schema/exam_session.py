from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ExamSession:
    """考试会话实体"""
    id: Optional[int] = None
    user_id: int = 0
    article_name: str = ""
    container_id: Optional[str] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    status: str = "active"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
