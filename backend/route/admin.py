import os
import json
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from schema.user import User
from route.dependencies import get_admin_user
from service.article_service import ARTICLES_DIR

router = APIRouter(prefix="/admin", tags=["admin"])


class ArticleCreate(BaseModel):
    filename: str
    title: str
    content: str
    test_config: dict = {}


class ArticleUpdate(BaseModel):
    title: str
    content: str
    test_config: dict = {}


# ─── Article CRUD ─────────────────────────────────────────────

@router.get("/articles")
def list_articles(admin: User = Depends(get_admin_user)):
    """列出所有题目（含 test_config 和附件列表）"""
    from service.article_service import list_articles as get_articles
    title_map = {a["filename"]: a["title"] for a in get_articles()}

    result = []
    if not os.path.exists(ARTICLES_DIR):
        return result
    for fname in sorted(os.listdir(ARTICLES_DIR)):
        dirpath = os.path.join(ARTICLES_DIR, fname)
        if not os.path.isdir(dirpath):
            continue
        readme_file = os.path.join(dirpath, "readme.md")
        config_file = os.path.join(dirpath, "test_config.json")
        attachments_dir = os.path.join(dirpath, "attachments")

        content = ""
        if os.path.exists(readme_file):
            with open(readme_file, "r", encoding="utf-8") as f:
                content = f.read()

        test_config = {}
        if os.path.exists(config_file):
            with open(config_file, "r", encoding="utf-8") as f:
                test_config = json.load(f)

        attachments = []
        if os.path.exists(attachments_dir):
            attachments = os.listdir(attachments_dir)

        result.append({
            "filename": fname,
            "title": title_map.get(fname, fname),
            "content": content,
            "test_config": test_config,
            "attachments": attachments
        })
    return result


@router.post("/articles")
def create_article(req: ArticleCreate, admin: User = Depends(get_admin_user)):
    """新建题目"""
    dirpath = os.path.join(ARTICLES_DIR, req.filename)
    if os.path.exists(dirpath):
        raise HTTPException(status_code=400, detail="Article already exists")

    os.makedirs(dirpath, exist_ok=True)
    os.makedirs(os.path.join(dirpath, "attachments"), exist_ok=True)

    with open(os.path.join(dirpath, "readme.md"), "w", encoding="utf-8") as f:
        f.write(req.content)

    with open(os.path.join(dirpath, "test_config.json"), "w", encoding="utf-8") as f:
        json.dump(req.test_config, f, ensure_ascii=False, indent=2)

    return {"success": True, "filename": req.filename}


@router.put("/articles/{name}")
def update_article(name: str, req: ArticleUpdate, admin: User = Depends(get_admin_user)):
    """更新题目"""
    dirpath = os.path.join(ARTICLES_DIR, name)
    if not os.path.exists(dirpath):
        raise HTTPException(status_code=404, detail="Article not found")

    with open(os.path.join(dirpath, "readme.md"), "w", encoding="utf-8") as f:
        f.write(req.content)

    with open(os.path.join(dirpath, "test_config.json"), "w", encoding="utf-8") as f:
        json.dump(req.test_config, f, ensure_ascii=False, indent=2)

    return {"success": True}


@router.delete("/articles/{name}")
def delete_article(name: str, admin: User = Depends(get_admin_user)):
    """删除题目"""
    dirpath = os.path.join(ARTICLES_DIR, name)
    if not os.path.exists(dirpath):
        raise HTTPException(status_code=404, detail="Article not found")
    shutil.rmtree(dirpath)
    return {"success": True}


# ─── Attachments ──────────────────────────────────────────────

@router.post("/articles/{name}/attachments")
def upload_attachment(name: str, file: UploadFile = File(...), admin: User = Depends(get_admin_user)):
    """上传附件"""
    dirpath = os.path.join(ARTICLES_DIR, name)
    if not os.path.exists(dirpath):
        raise HTTPException(status_code=404, detail="Article not found")

    attachments_dir = os.path.join(dirpath, "attachments")
    os.makedirs(attachments_dir, exist_ok=True)

    safe_name = os.path.basename(file.filename)
    filepath = os.path.join(attachments_dir, safe_name)
    with open(filepath, "wb") as f:
        f.write(file.file.read())

    return {"success": True, "filename": safe_name}


@router.delete("/articles/{name}/attachments/{filename}")
def delete_attachment(name: str, filename: str, admin: User = Depends(get_admin_user)):
    """删除附件"""
    safe_name = os.path.basename(filename)
    filepath = os.path.join(ARTICLES_DIR, name, "attachments", safe_name)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Attachment not found")
    os.remove(filepath)
    return {"success": True}


# ─── Dashboard ────────────────────────────────────────────────

@router.get("/dashboard")
def dashboard(admin: User = Depends(get_admin_user)):
    """仪表盘总览"""
    from dao.exam_result_dao import ExamResultDao
    from service.article_service import list_articles as get_articles

    stats = ExamResultDao.get_overall_stats()
    articles = get_articles()

    article_stats = []
    from middleware.database import get_db
    for a in articles:
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(DISTINCT user_id) FROM exam_results WHERE article_name = %s",
                    (a["filename"],)
                )
                attempted = cursor.fetchone()[0]
                cursor.execute(
                    "SELECT COUNT(DISTINCT user_id) FROM exam_results WHERE article_name = %s AND passed = TRUE",
                    (a["filename"],)
                )
                passed = cursor.fetchone()[0]
        article_stats.append({
            "filename": a["filename"],
            "title": a["title"],
            "attempted": attempted,
            "passed": passed,
            "pass_rate": round(passed / attempted * 100) if attempted > 0 else 0
        })

    return {
        "total_users": stats["total_users"],
        "total_submissions": stats["total_submissions"],
        "passed_users": stats["passed_users"],
        "overall_pass_rate": stats["pass_rate"],
        "total_articles": len(articles),
        "article_stats": article_stats
    }


# ─── Students ─────────────────────────────────────────────────

@router.get("/students")
def list_students(admin: User = Depends(get_admin_user)):
    """考生列表（仅 role=user 的账号）"""
    from dao.user_dao import UserDao
    from middleware.database import get_db
    from service.article_service import list_articles as get_articles

    users = [u for u in UserDao.get_all() if u.role != "admin"]
    articles = get_articles()
    total_articles = len(articles)

    result = []
    for user in users:
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(DISTINCT article_name) FROM exam_results WHERE user_id = %s",
                    (user.id,)
                )
                completed = cursor.fetchone()[0]
                cursor.execute(
                    "SELECT COUNT(DISTINCT article_name) FROM exam_results WHERE user_id = %s AND passed = TRUE",
                    (user.id,)
                )
                passed = cursor.fetchone()[0]

        result.append({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "completed": completed,
            "total": total_articles,
            "passed_count": passed,
            "pass_rate": round(passed / total_articles * 100) if total_articles > 0 else 0
        })

    passed_users = sum(1 for r in result if r["passed_count"] > 0)
    return {
        "total_students": len(result),
        "passed_students": passed_users,
        "failed_students": len(result) - passed_users,
        "students": result
    }


@router.get("/students/{user_id}")
def student_detail(user_id: int, admin: User = Depends(get_admin_user)):
    """考生详情：各题目答题记录"""
    from dao.exam_result_dao import ExamResultDao
    from dao.user_dao import UserDao
    from service.article_service import list_articles as get_articles
    from middleware.database import get_db

    user = UserDao.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    articles = get_articles()
    article_records = []

    for article in articles:
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM exam_results WHERE user_id = %s AND article_name = %s",
                    (user_id, article["filename"])
                )
                submission_count = cursor.fetchone()[0]
                cursor.execute(
                    """SELECT score, max_score, passed, cases_json, submitted_at
                       FROM exam_results WHERE user_id = %s AND article_name = %s
                       ORDER BY submitted_at DESC LIMIT 1""",
                    (user_id, article["filename"])
                )
                latest = cursor.fetchone()

        record = {
            "article_name": article["filename"],
            "article_title": article["title"],
            "submission_count": submission_count,
        }
        if latest:
            record.update({
                "latest_score": latest[0],
                "max_score": latest[1],
                "passed": latest[2],
                "cases": json.loads(latest[3]) if latest[3] else [],
                "submitted_at": latest[4].isoformat() if latest[4] else None
            })
        else:
            record.update({
                "latest_score": None, "max_score": None,
                "passed": None, "cases": [], "submitted_at": None
            })
        article_records.append(record)

    completed = sum(1 for r in article_records if r["submission_count"] > 0)
    passed_count = sum(1 for r in article_records if r["passed"])
    total_articles = len(articles)

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "completed": completed,
        "total": total_articles,
        "passed_count": passed_count,
        "pass_rate": round(passed_count / total_articles * 100) if total_articles > 0 else 0,
        "avg_score": round(
            sum(r["latest_score"] for r in article_records if r["latest_score"] is not None)
            / max(completed, 1)
        ),
        "article_records": article_records
    }
