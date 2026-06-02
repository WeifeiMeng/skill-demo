import traceback
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from schema.user import User
from route.dependencies import get_current_user
from dao.exam_session_dao import ExamSessionDao
from dao.exam_result_dao import ExamResultDao
from schema.exam_result import ExamResult
from service.docker_manager import exec_test
import json

router = APIRouter(prefix="/exam", tags=["exam"])

EXAM_DURATION = 7200  # 2 hours in seconds


class StartExamRequest(BaseModel):
    article: str
    container_id: str


class SubmitExamRequest(BaseModel):
    article: str
    container_id: str


@router.post("/start")
def start_exam(req: StartExamRequest, user: User = Depends(get_current_user)):
    """开始考试（记录开始时间）"""
    try:
        session = ExamSessionDao.start_or_get(user.id, req.article, req.container_id)
        elapsed = (datetime.now() - session.started_at).total_seconds()
        remaining = max(0, EXAM_DURATION - int(elapsed))
        return {
            "remaining": remaining,
            "started_at": session.started_at.isoformat(),
            "total": EXAM_DURATION
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


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


@router.post("/submit")
def submit_exam(req: SubmitExamRequest, user: User = Depends(get_current_user)):
    """提交测试，在容器中执行测试脚本并返回结果"""
    result = exec_test(req.container_id, req.article)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    # Save result to database
    exam_result = ExamResult(
        user_id=user.id,
        article_name=req.article,
        score=result.get("score", 0),
        max_score=result.get("max_score", 100),
        passed=result.get("passed", False),
        cases_json=json.dumps(result.get("cases", []))
    )
    ExamResultDao.create(exam_result)

    return result
