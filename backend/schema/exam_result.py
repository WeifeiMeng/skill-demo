from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ExamResult:
    """考试提交结果实体"""
    id: Optional[int] = None
    user_id: int = 0
    article_name: str = ""
    score: int = 0
    max_score: int = 100
    passed: bool = False
    cases_json: str = "[]"
    submitted_at: Optional[datetime] = None
