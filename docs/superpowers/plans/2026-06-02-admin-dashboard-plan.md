# Admin Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a standalone admin dashboard (Vue 3 SPA on port 3001) with article management, student progress tracking, and a dashboard overview.

**Architecture:** Extend the existing FastAPI backend with admin routes under `/admin` prefix. Create a new independent `frontend-admin/` Vite project. Backend changes add `role` to users, an `exam_results` table, and admin-specific APIs. Frontend is a dark-sidebar professional admin panel.

**Tech Stack:** Python/FastAPI, MySQL/pymysql, Vue 3 + Vite + Vue Router, JWT auth

---

### Task 1: Add `role` field to User schema and DAO

**Files:**
- Modify: `backend/schema/user.py`
- Modify: `backend/dao/user_dao.py`

- [ ] **Step 1: Add `role` to User schema**

In `backend/schema/user.py`, add `role` field:

```python
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
```

- [ ] **Step 2: Add `role` column migration and update UserDao queries**

In `backend/dao/user_dao.py`, update `init_table()` to add role column:

```python
@staticmethod
def init_table():
    sql = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            role VARCHAR(20) DEFAULT 'user',
            avatar VARCHAR(500),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
    """
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            conn.commit()
    # Migration: add role column if it doesn't exist (for existing tables)
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user'")
                conn.commit()
    except Exception:
        pass  # column already exists
```

Update all SELECT queries to include `role`. The pattern repeats — change each SELECT's column list from:
```python
"SELECT id, name, email, password, avatar, created_at, updated_at FROM users ..."
```
to:
```python
"SELECT id, name, email, password, role, avatar, created_at, updated_at FROM users ..."
```

Update all `User(...)` constructor calls to include `role=row[N]` (where N is the new position). For example, `get_by_id`:

```python
@staticmethod
def get_by_id(user_id: int) -> Optional[User]:
    sql = "SELECT id, name, email, password, role, avatar, created_at, updated_at FROM users WHERE id = %s"
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (user_id,))
            row = cursor.fetchone()
            if row:
                return User(
                    id=row[0], name=row[1], email=row[2], password=row[3],
                    role=row[4], avatar=row[5], created_at=row[6], updated_at=row[7]
                )
            return None
```

Apply the same pattern to `get_by_email`, `get_all`. The `create` method stays the same (role defaults in DB).

Update `create` method to also accept role:

```python
@staticmethod
def create(user: User) -> int:
    sql = """
        INSERT INTO users (name, email, password, role, avatar, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    now = datetime.now()
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (
                user.name, user.email, user.password, user.role,
                user.avatar, now, now
            ))
            conn.commit()
            return cursor.lastrowid
```

- [ ] **Step 3: Commit**

```bash
git add backend/schema/user.py backend/dao/user_dao.py
git commit -m "feat: add role field to User model and DAO"
```

---

### Task 2: Create ExamResult schema and DAO

**Files:**
- Create: `backend/schema/exam_result.py`
- Create: `backend/dao/exam_result_dao.py`

- [ ] **Step 1: Create ExamResult schema**

```python
# backend/schema/exam_result.py
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
```

- [ ] **Step 2: Create ExamResultDao**

```python
# backend/dao/exam_result_dao.py
from typing import List, Optional
from datetime import datetime
from schema.exam_result import ExamResult
from middleware.database import get_db
import json


class ExamResultDao:

    @staticmethod
    def init_table():
        sql = """
            CREATE TABLE IF NOT EXISTS exam_results (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                article_name VARCHAR(255) NOT NULL,
                score INT DEFAULT 0,
                max_score INT DEFAULT 100,
                passed BOOLEAN DEFAULT FALSE,
                cases_json TEXT,
                submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                conn.commit()

    @staticmethod
    def create(result: ExamResult) -> int:
        sql = """
            INSERT INTO exam_results (user_id, article_name, score, max_score, passed, cases_json)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (
                    result.user_id, result.article_name, result.score,
                    result.max_score, result.passed, result.cases_json
                ))
                conn.commit()
                return cursor.lastrowid

    @staticmethod
    def get_by_user(user_id: int) -> List[ExamResult]:
        sql = """
            SELECT id, user_id, article_name, score, max_score, passed, cases_json, submitted_at
            FROM exam_results WHERE user_id = %s ORDER BY submitted_at DESC
        """
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (user_id,))
                return [
                    ExamResult(
                        id=r[0], user_id=r[1], article_name=r[2], score=r[3],
                        max_score=r[4], passed=r[5], cases_json=r[6], submitted_at=r[7]
                    ) for r in cursor.fetchall()
                ]

    @staticmethod
    def get_user_article_best(user_id: int, article_name: str) -> Optional[ExamResult]:
        sql = """
            SELECT id, user_id, article_name, score, max_score, passed, cases_json, submitted_at
            FROM exam_results WHERE user_id = %s AND article_name = %s
            ORDER BY score DESC LIMIT 1
        """
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (user_id, article_name))
                r = cursor.fetchone()
                if r:
                    return ExamResult(
                        id=r[0], user_id=r[1], article_name=r[2], score=r[3],
                        max_score=r[4], passed=r[5], cases_json=r[6], submitted_at=r[7]
                    )
                return None

    @staticmethod
    def get_submission_count(user_id: int, article_name: str) -> int:
        sql = "SELECT COUNT(*) FROM exam_results WHERE user_id = %s AND article_name = %s"
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (user_id, article_name))
                return cursor.fetchone()[0]

    @staticmethod
    def get_all_users_stats() -> List[dict]:
        """返回每个用户在各题目的汇总统计"""
        sql = """
            SELECT u.id, u.name, u.email, er.article_name,
                   MAX(er.score) as best_score, er.max_score,
                   MAX(er.passed) as ever_passed, COUNT(*) as submission_count,
                   MAX(er.submitted_at) as last_submitted
            FROM users u
            LEFT JOIN exam_results er ON u.id = er.user_id
            WHERE u.role = 'user'
            GROUP BY u.id, er.article_name
            ORDER BY u.id, er.article_name
        """
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                columns = [d[0] for d in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]

    @staticmethod
    def get_overall_stats() -> dict:
        """总览统计"""
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'user'")
                total_users = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM exam_results")
                total_submissions = cursor.fetchone()[0]
                cursor.execute(
                    "SELECT COUNT(DISTINCT user_id) FROM exam_results WHERE passed = TRUE"
                )
                passed_users = cursor.fetchone()[0]
        return {
            "total_users": total_users,
            "total_submissions": total_submissions,
            "passed_users": passed_users,
            "pass_rate": round(passed_users / total_users * 100) if total_users > 0 else 0
        }


try:
    ExamResultDao.init_table()
except Exception:
    pass
```

- [ ] **Step 3: Commit**

```bash
git add backend/schema/exam_result.py backend/dao/exam_result_dao.py
git commit -m "feat: add ExamResult schema and DAO"
```

---

### Task 3: Add `role` to JWT, auth response, and create admin dependency

**Files:**
- Modify: `backend/service/auth_service.py`
- Modify: `backend/route/auth.py`
- Modify: `backend/route/dependencies.py`

- [ ] **Step 1: Add role to JWT token creation**

In `backend/service/auth_service.py`, update `create_token`:

```python
def create_token(user_id: int, email: str, role: str = "user") -> str:
    """创建 JWT token"""
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "exp": expire
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
```

- [ ] **Step 2: Pass role when creating token in auth routes**

In `backend/route/auth.py`, update `register` and `login` to pass role:

```python
# In register():
token = create_token(user.id, user.email, user.role or "user")

# In login():
token = create_token(user.id, user.email, user.role or "user")
```

Also update the user object returned in both endpoints to include `role`:

```python
"user": {
    "id": user.id,
    "name": user.name,
    "email": user.email,
    "role": user.role or "user",
    "avatar": user.avatar
}
```

And update `/auth/me` similarly to return role.

- [ ] **Step 3: Add `get_admin_user` dependency and update `get_current_user`**

In `backend/route/dependencies.py`:

```python
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取当前登录用户"""
    token = credentials.credentials
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = int(payload.get("sub"))
    user = UserDao.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def get_admin_user(user: User = Depends(get_current_user)):
    """获取当前管理员用户，非 admin 则拒绝"""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
```

Add the `HTTPException` import at the top:
```python
from fastapi import Depends, HTTPException
```

- [ ] **Step 4: Commit**

```bash
git add backend/service/auth_service.py backend/route/auth.py backend/route/dependencies.py
git commit -m "feat: add role to JWT, auth response, and admin dependency"
```

---

### Task 4: Save exam results on submit

**Files:**
- Modify: `backend/route/exam.py`

- [ ] **Step 1: Update submit_exam to save results**

In `backend/route/exam.py`, add import at top:

```python
from dao.exam_result_dao import ExamResultDao
from schema.exam_result import ExamResult
import json
```

In `submit_exam`, after getting result from `exec_test`, save to DB:

```python
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
```

- [ ] **Step 2: Commit**

```bash
git add backend/route/exam.py
git commit -m "feat: save exam results to database on submit"
```

---

### Task 5: Create admin routes — article CRUD

**Files:**
- Create: `backend/route/admin.py`

- [ ] **Step 1: Create article CRUD endpoints**

```python
# backend/route/admin.py
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
    filename: str       # 文件夹名，如 "my-new-article"
    title: str
    content: str        # markdown 内容
    test_config: dict = {}


class ArticleUpdate(BaseModel):
    title: str
    content: str
    test_config: dict = {}


# ─── Article CRUD ─────────────────────────────────────────────

@router.get("/articles")
def list_articles(admin: User = Depends(get_admin_user)):
    """列出所有题目（含 test_config）"""
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

    # Write readme.md
    with open(os.path.join(dirpath, "readme.md"), "w", encoding="utf-8") as f:
        f.write(req.content)

    # Write test_config.json
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

    filepath = os.path.join(attachments_dir, file.filename)
    with open(filepath, "wb") as f:
        f.write(file.file.read())

    return {"success": True, "filename": file.filename}


@router.delete("/articles/{name}/attachments/{filename}")
def delete_attachment(name: str, filename: str, admin: User = Depends(get_admin_user)):
    """删除附件"""
    filepath = os.path.join(ARTICLES_DIR, name, "attachments", filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Attachment not found")
    os.remove(filepath)
    return {"success": True}
```

- [ ] **Step 2: Commit**

```bash
git add backend/route/admin.py
git commit -m "feat: add admin article CRUD and attachment routes"
```

---

### Task 6: Add admin dashboard and student data routes

**Files:**
- Modify: `backend/route/admin.py` (append to existing file)

- [ ] **Step 1: Add student/dashboard endpoints to admin route**

Append these endpoints to `backend/route/admin.py` (after the attachment endpoints):

```python
# ─── Dashboard ────────────────────────────────────────────────

@router.get("/dashboard")
def dashboard(admin: User = Depends(get_admin_user)):
    """仪表盘总览"""
    from dao.exam_result_dao import ExamResultDao
    from service.article_service import list_articles

    stats = ExamResultDao.get_overall_stats()
    articles = list_articles()

    # Per-article pass rate
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
    from service.article_service import list_articles

    users = [u for u in UserDao.get_all() if u.role != "admin"]
    articles = list_articles()
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

    # Summary
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
    from service.article_service import list_articles
    from middleware.database import get_db
    import json as _json

    user = UserDao.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    articles = list_articles()
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
                "cases": _json.loads(latest[3]) if latest[3] else [],
                "submitted_at": latest[4].isoformat() if latest[4] else None
            })
        else:
            record.update({
                "latest_score": None, "max_score": None,
                "passed": None, "cases": [], "submitted_at": None
            })
        article_records.append(record)

    # Compute summary
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
```

- [ ] **Step 2: Commit**

```bash
git add backend/route/admin.py
git commit -m "feat: add admin dashboard and student data endpoints"
```

---

### Task 7: Register admin router and update CORS

**Files:**
- Modify: `backend/main.py`

- [ ] **Step 1: Register admin router and update CORS**

In `backend/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from middleware.database import get_db
from route import auth, article, docker_container, exam, admin

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(article.router)
app.include_router(docker_container.router)
app.include_router(exam.router)
app.include_router(admin.router)
```

- [ ] **Step 2: Verify backend starts**

```bash
cd backend && timeout 5 uv run uvicorn main:app --port 8000 2>&1 || true
```
Expected: No import errors, Application startup complete.

- [ ] **Step 3: Commit**

```bash
git add backend/main.py
git commit -m "feat: register admin router and add CORS for port 3001"
```

---

### Task 8: Scaffold frontend-admin project

**Files:**
- Create: `frontend-admin/index.html`
- Create: `frontend-admin/package.json`
- Create: `frontend-admin/vite.config.js`
- Create: `frontend-admin/src/main.js`
- Create: `frontend-admin/src/router.js`
- Create: `frontend-admin/src/style.css`
- Create: `frontend-admin/src/App.vue`
- Create: `frontend-admin/src/components/Sidebar.vue`

- [ ] **Step 1: Create project files**

`frontend-admin/package.json`:
```json
{
  "name": "coding-coach-admin",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite --port 3001"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.6.4"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "vite": "^5.0.0"
  }
}
```

`frontend-admin/index.html`:
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>管理后台 - Coding Coach</title>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.js"></script>
</body>
</html>
```

`frontend-admin/vite.config.js`:
```js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: { port: 3001 }
})
```

`frontend-admin/src/main.js`:
```js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router.js'
import './style.css'

createApp(App).use(router).mount('#app')
```

- [ ] **Step 2: Create router**

`frontend-admin/src/router.js`:
```js
import { createRouter, createWebHistory } from 'vue-router'
import Login from './views/Login.vue'
import Dashboard from './views/Dashboard.vue'
import ArticleList from './views/ArticleList.vue'
import ArticleEdit from './views/ArticleEdit.vue'
import StudentList from './views/StudentList.vue'
import StudentDetail from './views/StudentDetail.vue'

const routes = [
  { path: '/login', name: 'login', component: Login },
  { path: '/dashboard', name: 'dashboard', component: Dashboard },
  { path: '/articles', name: 'articles', component: ArticleList },
  { path: '/articles/new', name: 'article-new', component: ArticleEdit },
  { path: '/articles/:name/edit', name: 'article-edit', component: ArticleEdit },
  { path: '/students', name: 'students', component: StudentList },
  { path: '/students/:id', name: 'student-detail', component: StudentDetail },
  { path: '/:pathMatch(.*)*', redirect: '/dashboard' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Auth guard: all routes except /login require token
router.beforeEach((to, from) => {
  const token = localStorage.getItem('admin_token')
  if (to.name !== 'login' && !token) {
    return { name: 'login' }
  }
})

export default router
```

- [ ] **Step 3: Create global styles**

`frontend-admin/src/style.css`:
```css
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #f1f5f9;
  color: #1e293b;
}
a { text-decoration: none; color: inherit; }
button { cursor: pointer; font-family: inherit; }
input, textarea { font-family: inherit; }
```

- [ ] **Step 4: Create App.vue with sidebar layout**

`frontend-admin/src/App.vue`:
```vue
<template>
  <div class="admin-layout">
    <Sidebar />
    <main class="admin-main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import Sidebar from './components/Sidebar.vue'
</script>

<style scoped>
.admin-layout { display: flex; min-height: 100vh; }
.admin-main { flex: 1; padding: 32px; overflow-y: auto; }
</style>
```

- [ ] **Step 5: Create Sidebar component**

`frontend-admin/src/components/Sidebar.vue`:
```vue
<template>
  <aside class="sidebar">
    <div class="sidebar-brand">
      <span class="sidebar-logo">A</span>
      <span class="sidebar-title">管理后台</span>
    </div>
    <nav class="sidebar-nav">
      <router-link to="/dashboard" class="nav-item" active-class="nav-active">
        <span>📊</span> 仪表盘
      </router-link>
      <router-link to="/articles" class="nav-item" active-class="nav-active">
        <span>📝</span> 题目管理
      </router-link>
      <router-link to="/students" class="nav-item" active-class="nav-active">
        <span>👥</span> 考生数据
      </router-link>
    </nav>
    <div class="sidebar-footer">
      <button class="btn-logout" @click="logout">退出登录</button>
    </div>
  </aside>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const logout = () => {
  localStorage.removeItem('admin_token')
  localStorage.removeItem('admin_user')
  router.push({ name: 'login' })
}
</script>

<style scoped>
.sidebar {
  width: 220px;
  background: #0f172a;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  padding: 24px 0;
}
.sidebar-brand {
  display: flex; align-items: center; gap: 10px;
  padding: 0 20px; margin-bottom: 32px;
}
.sidebar-logo {
  width: 34px; height: 34px;
  background: linear-gradient(135deg, #4a6cf7, #6a3de8);
  border-radius: 8px; display: flex;
  align-items: center; justify-content: center;
  color: #fff; font-weight: 700; font-size: 16px;
}
.sidebar-title { color: #fff; font-weight: 700; font-size: 16px; }
.sidebar-nav { flex: 1; display: flex; flex-direction: column; gap: 4px; padding: 0 12px; }
.nav-item {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 12px; border-radius: 8px;
  color: #94a3b8; font-size: 14px; font-weight: 500;
  transition: all 0.15s;
}
.nav-item:hover { color: #e2e8f0; background: rgba(255,255,255,0.05); }
.nav-active { color: #818cf8; background: rgba(74,108,247,0.15); font-weight: 600; }
.sidebar-footer { padding: 0 12px; }
.btn-logout {
  width: 100%; padding: 10px;
  background: transparent; border: 1px solid #334155;
  color: #64748b; border-radius: 8px; font-size: 13px;
}
.btn-logout:hover { background: rgba(255,255,255,0.05); color: #94a3b8; }
</style>
```

- [ ] **Step 6: Install deps and verify startup**

```bash
cd frontend-admin && npm install
```
Then dev server should start without errors.

- [ ] **Step 7: Commit**

```bash
git add frontend-admin/index.html frontend-admin/package.json frontend-admin/vite.config.js \
        frontend-admin/src/main.js frontend-admin/src/router.js frontend-admin/src/style.css \
        frontend-admin/src/App.vue frontend-admin/src/components/Sidebar.vue
git commit -m "feat: scaffold admin frontend project with layout and router"
```

---

### Task 9: Admin Login page

**Files:**
- Create: `frontend-admin/src/views/Login.vue`

- [ ] **Step 1: Create Login view**

```vue
<!-- frontend-admin/src/views/Login.vue -->
<template>
  <div class="login-page">
    <form class="login-card" @submit.prevent="handleSubmit">
      <h1 class="login-title">管理员登录</h1>
      <p class="login-subtitle">Coding Coach 管理后台</p>
      <div class="form-group">
        <label class="form-label">邮箱</label>
        <input v-model="form.email" type="email" class="form-input" placeholder="admin@example.com" required />
      </div>
      <div class="form-group">
        <label class="form-label">密码</label>
        <input v-model="form.password" type="password" class="form-input" placeholder="请输入密码" required />
      </div>
      <div v-if="error" class="form-error">{{ error }}</div>
      <button type="submit" class="btn-submit" :disabled="loading">
        {{ loading ? '登录中...' : '登录' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const API_BASE = 'http://localhost:8000'
const router = useRouter()

const form = ref({ email: '', password: '' })
const loading = ref(false)
const error = ref('')

const handleSubmit = async () => {
  error.value = ''
  loading.value = true
  try {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value)
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail || '登录失败')
    if (data.user.role !== 'admin') throw new Error('非管理员账号，无权访问')

    localStorage.setItem('admin_token', data.token)
    localStorage.setItem('admin_user', JSON.stringify(data.user))
    router.push({ name: 'dashboard' })
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  display: flex; align-items: center; justify-content: center;
  min-height: 100vh; background: #0f172a;
}
.login-card {
  width: 400px; background: #1e293b; border-radius: 16px; padding: 40px;
  border: 1px solid #334155;
}
.login-title { font-size: 22px; font-weight: 700; color: #f1f5f9; margin-bottom: 6px; }
.login-subtitle { font-size: 14px; color: #64748b; margin-bottom: 28px; }
.form-group { margin-bottom: 18px; }
.form-label { display: block; font-size: 13px; color: #94a3b8; margin-bottom: 6px; }
.form-input {
  width: 100%; padding: 12px 14px;
  background: #0f172a; border: 1px solid #334155;
  border-radius: 10px; color: #e2e8f0; font-size: 14px; outline: none;
}
.form-input:focus { border-color: #4a6cf7; }
.form-input::placeholder { color: #475569; }
.form-error { color: #ef4444; font-size: 13px; margin-bottom: 16px; text-align: center; }
.btn-submit {
  width: 100%; padding: 13px;
  background: linear-gradient(135deg, #4a6cf7, #6a3de8);
  color: #fff; border: none; border-radius: 10px;
  font-size: 15px; font-weight: 600;
}
.btn-submit:hover:not(:disabled) { opacity: 0.9; }
.btn-submit:disabled { opacity: 0.6; cursor: not-allowed; }
</style>
```

- [ ] **Step 2: Commit**

```bash
git add frontend-admin/src/views/Login.vue
git commit -m "feat: add admin login page"
```

---

### Task 10: Dashboard page with stat cards and pass-rate bars

**Files:**
- Create: `frontend-admin/src/components/StatCard.vue`
- Create: `frontend-admin/src/views/Dashboard.vue`

- [ ] **Step 1: Create StatCard component**

```vue
<!-- frontend-admin/src/components/StatCard.vue -->
<template>
  <div class="stat-card" :style="{ borderLeftColor: color }">
    <div class="stat-label">{{ label }}</div>
    <div class="stat-value">{{ value }}</div>
  </div>
</template>

<script setup>
defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], required: true },
  color: { type: String, default: '#4a6cf7' }
})
</script>

<style scoped>
.stat-card {
  background: #fff; border-radius: 8px; padding: 20px;
  border-left: 4px solid #4a6cf7;
}
.stat-label {
  font-size: 12px; color: #94a3b8;
  text-transform: uppercase; letter-spacing: 1px;
}
.stat-value {
  font-size: 32px; font-weight: 800; color: #0f172a; margin-top: 4px;
}
</style>
```

- [ ] **Step 2: Create Dashboard view**

```vue
<!-- frontend-admin/src/views/Dashboard.vue -->
<template>
  <div class="dashboard">
    <h2 class="page-title">仪表盘</h2>

    <div class="stat-grid">
      <StatCard label="总考生数" :value="data.total_users" color="#4a6cf7" />
      <StatCard label="总通过率" :value="data.overall_pass_rate + '%'" color="#22c55e" />
      <StatCard label="题目数" :value="data.total_articles" color="#f59e0b" />
    </div>

    <div class="card">
      <h3 class="card-title">各题目通过率</h3>
      <div class="bar-list">
        <div v-for="a in data.article_stats" :key="a.filename" class="bar-item">
          <div class="bar-header">
            <span class="bar-label">{{ a.title }}</span>
            <span class="bar-value">{{ a.pass_rate }}% ({{ a.passed }}/{{ a.attempted }})</span>
          </div>
          <div class="bar-track">
            <div class="bar-fill" :style="{ width: a.pass_rate + '%' }"></div>
          </div>
        </div>
        <div v-if="!data.article_stats?.length" class="empty">暂无数据</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import StatCard from '../components/StatCard.vue'

const API_BASE = 'http://localhost:8000'
const data = ref({ total_users: 0, overall_pass_rate: 0, total_articles: 0, article_stats: [] })

const getHeaders = () => {
  const t = localStorage.getItem('admin_token')
  return t ? { Authorization: `Bearer ${t}` } : {}
}

onMounted(async () => {
  try {
    const res = await fetch(`${API_BASE}/admin/dashboard`, { headers: getHeaders() })
    if (res.ok) data.value = await res.json()
    else if (res.status === 401 || res.status === 403) {
      localStorage.clear(); window.location.hash = '#/login'
    }
  } catch (e) { console.error(e) }
})
</script>

<style scoped>
.dashboard { max-width: 960px; }
.page-title { font-size: 22px; font-weight: 700; color: #0f172a; margin-bottom: 24px; }
.stat-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 28px; }
.card { background: #fff; border-radius: 10px; padding: 24px; border: 1px solid #e2e8f0; }
.card-title { font-size: 15px; font-weight: 600; color: #0f172a; margin-bottom: 18px; }
.bar-list { display: flex; flex-direction: column; gap: 16px; }
.bar-header { display: flex; justify-content: space-between; margin-bottom: 6px; }
.bar-label { font-size: 13px; color: #475569; font-weight: 500; }
.bar-value { font-size: 12px; color: #64748b; }
.bar-track { height: 8px; background: #e2e8f0; border-radius: 4px; }
.bar-fill { height: 8px; background: linear-gradient(90deg, #4a6cf7, #6a3de8); border-radius: 4px; transition: width 0.6s ease; }
.empty { color: #94a3b8; font-size: 13px; text-align: center; padding: 20px 0; }
</style>
```

- [ ] **Step 3: Commit**

```bash
git add frontend-admin/src/components/StatCard.vue frontend-admin/src/views/Dashboard.vue
git commit -m "feat: add admin dashboard with stat cards and pass-rate bars"
```

---

### Task 11: ArticleList and ArticleEdit pages

**Files:**
- Create: `frontend-admin/src/views/ArticleList.vue`
- Create: `frontend-admin/src/views/ArticleEdit.vue`
- Create: `frontend-admin/src/components/TestCaseEditor.vue`
- Create: `frontend-admin/src/components/AttachmentList.vue`

- [ ] **Step 1: Create TestCaseEditor component**

```vue
<!-- frontend-admin/src/components/TestCaseEditor.vue -->
<template>
  <div class="tce">
    <div class="tce-list">
      <div v-for="(c, i) in modelValue" :key="i" class="tce-row">
        <input v-model="c.name" class="tce-input-name" placeholder="用例名称" />
        <input v-model.number="c.score" type="number" class="tce-input-score" placeholder="分值" />
        <button class="tce-btn-del" @click="remove(i)">✕</button>
      </div>
    </div>
    <button class="tce-btn-add" @click="add">+ 添加用例</button>
  </div>
</template>

<script setup>
const props = defineProps({ modelValue: { type: Array, default: () => [] } })
const emit = defineEmits(['update:modelValue'])

const add = () => {
  const list = [...props.modelValue, { name: '', score: 0 }]
  emit('update:modelValue', list)
}
const remove = (i) => {
  const list = props.modelValue.filter((_, idx) => idx !== i)
  emit('update:modelValue', list)
}
</script>

<style scoped>
.tce-list { display: flex; flex-direction: column; gap: 8px; margin-bottom: 12px; }
.tce-row { display: flex; gap: 8px; align-items: center; }
.tce-input-name {
  flex: 1; padding: 8px 12px; background: #f8fafc;
  border: 1px solid #e2e8f0; border-radius: 6px; font-size: 13px;
}
.tce-input-score {
  width: 80px; padding: 8px 12px; background: #f8fafc;
  border: 1px solid #e2e8f0; border-radius: 6px; font-size: 13px;
}
.tce-btn-del {
  width: 28px; height: 28px; background: #fef2f2; color: #ef4444;
  border: none; border-radius: 6px; font-size: 14px;
}
.tce-btn-add {
  padding: 8px 16px; background: #f1f5f9; color: #475569;
  border: 1px dashed #cbd5e1; border-radius: 6px; font-size: 13px;
}
</style>
```

- [ ] **Step 2: Create AttachmentList component**

```vue
<!-- frontend-admin/src/components/AttachmentList.vue -->
<template>
  <div class="att">
    <div class="att-list">
      <div v-for="f in files" :key="f" class="att-row">
        <span>📄 {{ f }}</span>
        <button class="att-btn-del" @click="$emit('delete', f)">删除</button>
      </div>
      <div v-if="!files.length" class="att-empty">暂无附件</div>
    </div>
    <div class="att-upload">
      <input type="file" ref="fileInput" @change="handleUpload" class="att-input" />
      <button class="att-btn-upload" @click="$refs.fileInput.click()">
        {{ uploading ? '上传中...' : '📎 选择文件上传' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({ files: { type: Array, default: () => [] }, articleName: String })
const emit = defineEmits(['uploaded', 'delete'])

const fileInput = ref(null)
const uploading = ref(false)
const API_BASE = 'http://localhost:8000'

const getHeaders = () => {
  const t = localStorage.getItem('admin_token')
  return t ? { Authorization: `Bearer ${t}` } : {}
}

const handleUpload = async (e) => {
  const file = e.target.files[0]
  if (!file) return
  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    const res = await fetch(
      `${API_BASE}/admin/articles/${props.articleName}/attachments`,
      { method: 'POST', headers: getHeaders(), body: formData }
    )
    if (res.ok) emit('uploaded', file.name)
  } catch (err) { console.error(err) }
  finally { uploading.value = false; e.target.value = '' }
}
</script>

<style scoped>
.att-list { margin-bottom: 16px; }
.att-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 8px 12px; background: #f8fafc; border-radius: 6px;
  font-size: 13px; color: #475569; margin-bottom: 6px;
}
.att-btn-del { background: none; border: none; color: #ef4444; font-size: 12px; }
.att-empty { color: #94a3b8; font-size: 13px; padding: 12px 0; }
.att-input { display: none; }
.att-btn-upload {
  padding: 8px 16px; background: #f1f5f9; color: #475569;
  border: 1px dashed #cbd5e1; border-radius: 6px; font-size: 13px;
}
</style>
```

- [ ] **Step 3: Create ArticleList view**

```vue
<!-- frontend-admin/src/views/ArticleList.vue -->
<template>
  <div class="article-list">
    <div class="page-header">
      <h2 class="page-title">题目管理</h2>
      <router-link to="/articles/new" class="btn-primary">+ 新建题目</router-link>
    </div>
    <div class="card">
      <table class="table" v-if="articles.length">
        <thead>
          <tr>
            <th>文件夹</th><th>标题</th><th>附件数</th><th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="a in articles" :key="a.filename">
            <td><code>{{ a.filename }}</code></td>
            <td>{{ a.filename }}</td>
            <td>{{ a.attachments?.length || 0 }}</td>
            <td class="actions">
              <router-link :to="`/articles/${a.filename}/edit`" class="btn-edit">编辑</router-link>
              <button class="btn-del" @click="handleDelete(a.filename)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else class="empty">暂无题目</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const API_BASE = 'http://localhost:8000'
const articles = ref([])

const getHeaders = () => {
  const t = localStorage.getItem('admin_token')
  return t ? { Authorization: `Bearer ${t}` } : {}
}

const load = async () => {
  const res = await fetch(`${API_BASE}/admin/articles`, { headers: getHeaders() })
  if (res.ok) articles.value = await res.json()
}
const handleDelete = async (filename) => {
  if (!confirm(`确认删除 "${filename}"？此操作不可恢复。`)) return
  const res = await fetch(`${API_BASE}/admin/articles/${filename}`, {
    method: 'DELETE', headers: getHeaders()
  })
  if (res.ok) await load()
}
onMounted(load)
</script>

<style scoped>
.article-list { max-width: 960px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.page-title { font-size: 22px; font-weight: 700; color: #0f172a; }
.btn-primary {
  padding: 10px 22px; background: #4a6cf7; color: #fff;
  border: none; border-radius: 8px; font-size: 14px; font-weight: 600;
}
.btn-primary:hover { opacity: 0.9; }
.card { background: #fff; border-radius: 10px; border: 1px solid #e2e8f0; overflow: hidden; }
.table { width: 100%; border-collapse: collapse; font-size: 13px; }
.table th { text-align: left; padding: 12px 16px; background: #f8fafc; color: #64748b; font-weight: 600; font-size: 12px; text-transform: uppercase; }
.table td { padding: 12px 16px; border-top: 1px solid #f1f5f9; color: #334155; }
.table code { background: #f1f5f9; padding: 3px 8px; border-radius: 4px; font-size: 12px; }
.actions { display: flex; gap: 8px; }
.btn-edit { padding: 5px 14px; background: #eff6ff; color: #2563eb; border-radius: 6px; font-size: 12px; font-weight: 500; }
.btn-del { padding: 5px 14px; background: #fef2f2; color: #ef4444; border: none; border-radius: 6px; font-size: 12px; font-weight: 500; }
.empty { color: #94a3b8; font-size: 13px; text-align: center; padding: 32px 0; }
</style>
```

- [ ] **Step 4: Create ArticleEdit view**

```vue
<!-- frontend-admin/src/views/ArticleEdit.vue -->
<template>
  <div class="article-edit">
    <div class="page-header">
      <h2 class="page-title">{{ isNew ? '新建题目' : '编辑题目：' + articleName }}</h2>
      <div class="header-actions">
        <button class="btn-save" @click="save">保存</button>
      </div>
    </div>

    <div class="field">
      <label class="field-label">文件夹名（英文标识）</label>
      <input v-model="filename" class="field-input" :disabled="!isNew" placeholder="my-new-article" />
    </div>

    <div class="card">
      <div class="tabs">
        <button class="tab" :class="{ active: tab === 'md' }" @click="tab = 'md'">📄 Markdown</button>
        <button class="tab" :class="{ active: tab === 'test' }" @click="tab = 'test'">🧪 测试用例</button>
        <button class="tab" :class="{ active: tab === 'att' }" @click="tab = 'att'">📎 附件</button>
      </div>

      <div v-show="tab === 'md'" class="tab-content">
        <textarea v-model="content" class="md-editor" rows="20" placeholder="# 题目名称&#10;&#10;## 题目描述&#10;..."></textarea>
      </div>

      <div v-show="tab === 'test'" class="tab-content">
        <div class="field">
          <label class="field-label">测试命令</label>
          <input v-model="testConfig.test_command" class="field-input" placeholder="python test.py" />
        </div>
        <TestCaseEditor v-model="testConfig.cases" />
      </div>

      <div v-show="tab === 'att'" class="tab-content">
        <AttachmentList
          :files="attachments"
          :articleName="articleName"
          @uploaded="attachments.push($event)"
          @delete="handleDeleteAttachment"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import TestCaseEditor from '../components/TestCaseEditor.vue'
import AttachmentList from '../components/AttachmentList.vue'

const route = useRoute()
const router = useRouter()
const API_BASE = 'http://localhost:8000'

const articleName = computed(() => route.params.name || '')
const isNew = computed(() => !route.params.name)

const tab = ref('md')
const filename = ref('')
const content = ref('')
const testConfig = ref({ test_command: 'python test.py', max_score: 100, cases: [] })
const attachments = ref([])

const getHeaders = () => {
  const t = localStorage.getItem('admin_token')
  return t ? { Authorization: `Bearer ${t}` } : {}
}

onMounted(async () => {
  if (!isNew.value) {
    const res = await fetch(`${API_BASE}/admin/articles`, { headers: getHeaders() })
    if (res.ok) {
      const articles = await res.json()
      const article = articles.find(a => a.filename === articleName.value)
      if (article) {
        filename.value = article.filename
        content.value = article.content
        testConfig.value = article.test_config || { test_command: 'python test.py', max_score: 100, cases: [] }
        attachments.value = article.attachments || []
      }
    }
  }
})

const save = async () => {
  if (isNew.value) {
    const res = await fetch(`${API_BASE}/admin/articles`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getHeaders() },
      body: JSON.stringify({ filename: filename.value, title: filename.value, content: content.value, test_config: testConfig.value })
    })
    if (res.ok) {
      router.push({ name: 'article-edit', params: { name: filename.value } })
    } else {
      const err = await res.json()
      alert(err.detail || '创建失败')
    }
  } else {
    await fetch(`${API_BASE}/admin/articles/${articleName.value}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', ...getHeaders() },
      body: JSON.stringify({ title: articleName.value, content: content.value, test_config: testConfig.value })
    })
    alert('保存成功')
  }
}

const handleDeleteAttachment = async (filename) => {
  await fetch(`${API_BASE}/admin/articles/${articleName.value}/attachments/${filename}`, {
    method: 'DELETE', headers: getHeaders()
  })
  attachments.value = attachments.value.filter(f => f !== filename)
}
</script>

<style scoped>
.article-edit { max-width: 960px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.page-title { font-size: 22px; font-weight: 700; color: #0f172a; }
.btn-save {
  padding: 10px 28px; background: linear-gradient(135deg, #4a6cf7, #6a3de8);
  color: #fff; border: none; border-radius: 8px; font-size: 14px; font-weight: 600;
}
.field { margin-bottom: 18px; }
.field-label { display: block; font-size: 13px; color: #475569; font-weight: 500; margin-bottom: 6px; }
.field-input {
  width: 100%; padding: 10px 14px; background: #fff; border: 1px solid #e2e8f0;
  border-radius: 8px; font-size: 14px; color: #1e293b;
}
.field-input:disabled { background: #f8fafc; color: #94a3b8; }
.card { background: #fff; border-radius: 10px; border: 1px solid #e2e8f0; overflow: hidden; }
.tabs { display: flex; border-bottom: 2px solid #e2e8f0; }
.tab {
  padding: 12px 20px; background: none; border: none; border-bottom: 2px solid transparent;
  margin-bottom: -2px; color: #94a3b8; font-size: 13px; font-weight: 500;
}
.tab.active { color: #4a6cf7; border-bottom-color: #4a6cf7; font-weight: 600; }
.tab-content { padding: 24px; }
.md-editor {
  width: 100%; padding: 16px; background: #f8fafc; border: 1px solid #e2e8f0;
  border-radius: 8px; font-size: 14px; color: #1e293b; resize: vertical;
  font-family: 'SF Mono', 'Fira Code', monospace; line-height: 1.7;
}
</style>
```

- [ ] **Step 5: Commit**

```bash
git add frontend-admin/src/components/TestCaseEditor.vue frontend-admin/src/components/AttachmentList.vue \
        frontend-admin/src/views/ArticleList.vue frontend-admin/src/views/ArticleEdit.vue
git commit -m "feat: add article list and edit pages with test case and attachment management"
```

---

### Task 12: StudentList and StudentDetail pages

**Files:**
- Create: `frontend-admin/src/views/StudentList.vue`
- Create: `frontend-admin/src/views/StudentDetail.vue`

- [ ] **Step 1: Create StudentList view**

```vue
<!-- frontend-admin/src/views/StudentList.vue -->
<template>
  <div class="student-list">
    <h2 class="page-title">考生数据</h2>

    <div class="stat-grid">
      <StatCard label="总考生" :value="data.total_students" color="#4a6cf7" />
      <StatCard label="已通过" :value="data.passed_students" color="#22c55e" />
      <StatCard label="未通过" :value="data.failed_students" color="#ef4444" />
    </div>

    <div class="card">
      <table class="table" v-if="data.students?.length">
        <thead>
          <tr>
            <th>姓名</th><th>邮箱</th><th>完成题数</th><th>通过率</th><th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in data.students" :key="s.id">
            <td class="td-name">{{ s.name }}</td>
            <td class="td-email">{{ s.email }}</td>
            <td class="td-center">{{ s.completed }}/{{ s.total }}</td>
            <td class="td-center">
              <span :class="s.pass_rate >= 50 ? 'rate-pass' : 'rate-fail'">{{ s.pass_rate }}%</span>
            </td>
            <td class="td-center">
              <router-link :to="`/students/${s.id}`" class="btn-detail">详情</router-link>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else class="empty">暂无考生数据</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import StatCard from '../components/StatCard.vue'

const API_BASE = 'http://localhost:8000'
const data = ref({ total_students: 0, passed_students: 0, failed_students: 0, students: [] })

const getHeaders = () => {
  const t = localStorage.getItem('admin_token')
  return t ? { Authorization: `Bearer ${t}` } : {}
}

onMounted(async () => {
  const res = await fetch(`${API_BASE}/admin/students`, { headers: getHeaders() })
  if (res.ok) data.value = await res.json()
})
</script>

<style scoped>
.student-list { max-width: 960px; }
.page-title { font-size: 22px; font-weight: 700; color: #0f172a; margin-bottom: 24px; }
.stat-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 28px; }
.card { background: #fff; border-radius: 10px; border: 1px solid #e2e8f0; overflow: hidden; }
.table { width: 100%; border-collapse: collapse; font-size: 13px; }
.table th { text-align: left; padding: 12px 16px; background: #f8fafc; color: #64748b; font-weight: 600; font-size: 12px; text-transform: uppercase; }
.table td { padding: 12px 16px; border-top: 1px solid #f1f5f9; color: #334155; }
.td-name { font-weight: 500; }
.td-email { color: #64748b; }
.td-center { text-align: center; }
.rate-pass { color: #16a34a; font-weight: 600; }
.rate-fail { color: #dc2626; font-weight: 600; }
.btn-detail { color: #4a6cf7; font-weight: 500; font-size: 12px; }
.empty { color: #94a3b8; font-size: 13px; text-align: center; padding: 32px 0; }
</style>
```

- [ ] **Step 2: Create StudentDetail view**

```vue
<!-- frontend-admin/src/views/StudentDetail.vue -->
<template>
  <div class="student-detail">
    <div class="page-header">
      <router-link to="/students" class="back-link">← 返回列表</router-link>
      <h2 class="page-title">{{ data.name }}</h2>
      <span class="page-email">{{ data.email }}</span>
    </div>

    <div class="stat-grid">
      <div class="sum-card"><div class="sum-label">完成题目</div><div class="sum-value">{{ data.completed }}/{{ data.total }}</div></div>
      <div class="sum-card"><div class="sum-label">总通过率</div><div class="sum-value rate-pass">{{ data.pass_rate }}%</div></div>
      <div class="sum-card"><div class="sum-label">平均得分</div><div class="sum-value">{{ data.avg_score }}</div></div>
    </div>

    <div class="card">
      <h3 class="card-title">答题记录</h3>
      <div v-if="data.article_records?.length">
        <div v-for="r in data.article_records" :key="r.article_name" class="record-item">
          <div class="record-header" @click="toggle(r.article_name)">
            <div class="record-info">
              <span class="record-title">{{ r.article_title }}</span>
              <span class="record-count">{{ r.submission_count }} 次提交</span>
            </div>
            <div class="record-result">
              <span v-if="r.passed === null" class="status-none">未开始</span>
              <span v-else :class="r.passed ? 'status-pass' : 'status-fail'">
                {{ r.latest_score }}分 {{ r.passed ? 'PASS' : 'FAIL' }}
              </span>
              <span class="toggle-arrow">{{ expanded[r.article_name] ? '▾' : '▸' }}</span>
            </div>
          </div>
          <div v-if="expanded[r.article_name] && r.cases?.length" class="record-cases">
            <div v-for="(c, i) in r.cases" :key="i" class="case-row" :class="c.passed ? 'case-pass' : 'case-fail'">
              <span>{{ c.passed ? '✓' : '✗' }} {{ c.name }}</span>
              <span v-if="c.score !== undefined" class="case-score">{{ c.score }}分</span>
              <span v-if="c.message" class="case-msg">{{ c.message }}</span>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="empty">暂无答题记录</div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const API_BASE = 'http://localhost:8000'
const data = ref({ name: '', email: '', completed: 0, total: 0, pass_rate: 0, avg_score: 0, article_records: [] })
const expanded = reactive({})

const getHeaders = () => {
  const t = localStorage.getItem('admin_token')
  return t ? { Authorization: `Bearer ${t}` } : {}
}

const toggle = (name) => { expanded[name] = !expanded[name] }

onMounted(async () => {
  const res = await fetch(`${API_BASE}/admin/students/${route.params.id}`, { headers: getHeaders() })
  if (res.ok) data.value = await res.json()
})
</script>

<style scoped>
.student-detail { max-width: 960px; }
.page-header { margin-bottom: 24px; }
.back-link { color: #64748b; font-size: 13px; display: inline-block; margin-bottom: 8px; }
.back-link:hover { color: #4a6cf7; }
.page-title { font-size: 22px; font-weight: 700; color: #0f172a; display: inline; margin-right: 12px; }
.page-email { color: #64748b; font-size: 14px; }
.stat-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 28px; }
.sum-card { background: #fff; border-radius: 8px; padding: 16px; text-align: center; border: 1px solid #e2e8f0; }
.sum-label { font-size: 12px; color: #94a3b8; }
.sum-value { font-size: 24px; font-weight: 700; color: #0f172a; margin-top: 4px; }
.rate-pass { color: #22c55e; }
.card { background: #fff; border-radius: 10px; border: 1px solid #e2e8f0; padding: 24px; }
.card-title { font-size: 15px; font-weight: 600; color: #0f172a; margin-bottom: 16px; }
.record-item { border-bottom: 1px solid #f1f5f9; }
.record-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 14px 0; cursor: pointer;
}
.record-info { display: flex; gap: 10px; align-items: baseline; }
.record-title { font-size: 14px; font-weight: 500; color: #334155; }
.record-count { font-size: 12px; color: #94a3b8; }
.record-result { display: flex; align-items: center; gap: 12px; }
.status-pass { color: #16a34a; font-weight: 600; font-size: 13px; }
.status-fail { color: #dc2626; font-weight: 600; font-size: 13px; }
.status-none { color: #94a3b8; font-size: 13px; }
.toggle-arrow { color: #94a3b8; font-size: 16px; }
.record-cases { padding: 0 0 14px 14px; }
.case-row {
  display: flex; gap: 12px; align-items: center;
  padding: 8px 12px; border-radius: 6px; font-size: 13px; margin-bottom: 4px;
}
.case-pass { background: #f0fdf4; }
.case-fail { background: #fef2f2; }
.case-score { color: #64748b; font-size: 12px; margin-left: auto; }
.case-msg { color: #94a3b8; font-size: 12px; }
.empty { color: #94a3b8; font-size: 13px; text-align: center; padding: 24px 0; }
</style>
```

- [ ] **Step 2: Commit**

```bash
git add frontend-admin/src/views/StudentList.vue frontend-admin/src/views/StudentDetail.vue
git commit -m "feat: add student list and detail pages"
```

---

### Task 13: Integration — verify end-to-end

- [ ] **Step 1: Start backend and verify admin endpoints**

```bash
cd backend && uv run uvicorn main:app --port 8000 &
sleep 3
# Test dashboard
curl -H "Authorization: Bearer <admin_token>" http://localhost:8000/admin/dashboard
# Test article list
curl -H "Authorization: Bearer <admin_token>" http://localhost:8000/admin/articles
```

- [ ] **Step 2: Start frontend-admin and verify pages load**

```bash
cd frontend-admin && npm run dev &
```

Open `http://localhost:3001/login` — login page should render. After login, navigate to dashboard, articles, students.

- [ ] **Step 3: Create initial admin user in database**

```sql
-- Run in MySQL:
INSERT INTO users (name, email, password, role) VALUES ('Admin', 'admin@example.com', '<bcrypt_hash>', 'admin');
```
Or update an existing user: `UPDATE users SET role = 'admin' WHERE email = 'existing@email.com';`

- [ ] **Step 4: Commit any final tweaks**

```bash
git add -A
git commit -m "chore: final integration fixes"
```
