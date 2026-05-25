from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from schema.user import User
from route.dependencies import get_current_user
from dao.exam_session_dao import ExamSessionDao

router = APIRouter(prefix="/exam", tags=["exam"])

EXAM_DURATION = 7200  # 2 hours in seconds


class StartExamRequest(BaseModel):
    article: str
    container_id: str


@router.post("/start")
def start_exam(req: StartExamRequest, user: User = Depends(get_current_user)):
    """开始考试（记录开始时间）"""
    session = ExamSessionDao.start_or_get(user.id, req.article, req.container_id)

    elapsed = (datetime.now() - session.started_at).total_seconds()
    remaining = max(0, EXAM_DURATION - int(elapsed))

    return {
        "remaining": remaining,
        "started_at": session.started_at.isoformat(),
        "total": EXAM_DURATION
    }


@router.get("/time")
def get_exam_time(article: str, user: User = Depends(get_current_user)):
    """获取考试剩余时间"""
    session = ExamSessionDao.get_active(user.id, article)
    if not session:
        raise HTTPException(status_code=404, detail="No active exam session found")

    elapsed = (datetime.now() - session.started_at).total_seconds()
    remaining = max(0, EXAM_DURATION - int(elapsed))

    return {
        "remaining": remaining,
        "started_at": session.started_at.isoformat(),
        "total": EXAM_DURATION
    }


@router.post("/finish")
def finish_exam(article: str, user: User = Depends(get_current_user)):
    """结束考试"""
    ExamSessionDao.finish(user.id, article)
    return {"success": True}
