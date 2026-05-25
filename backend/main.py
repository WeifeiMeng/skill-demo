from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from middleware.database import get_db
from route import auth, article, docker_container, exam

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)
app.include_router(article.router)
app.include_router(docker_container.router)
app.include_router(exam.router)


@app.get("/db/test")
def test_db():
    """测试数据库连接"""
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return {"success": True, "result": result[0]}
    except Exception as e:
        return {"success": False, "error": str(e)}
