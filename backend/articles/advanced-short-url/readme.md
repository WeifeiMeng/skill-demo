题目名称
RateLink — 高性能短链接服务（含分布式限流）
题目描述
想象一下你用过 t.cn、bit.ly 这种短链接服务：把一个巨长的网址 https://www.example.com/very/long/url/... 变成一个短的 https://short.xyz/abc123。
你需要用 Python 写一个这样的后端接口服务。
1. 两个核心功能（你必须实现的两个 HTTP 接口）
暂时无法在飞书文档外展示此内容
2. 滑动窗口限流
每个 user_id 在 10 秒内最多允许创建 5 个短链接（需使用滑动窗口算法）。
- 现实场景：如果有恶意用户写了个脚本，1 秒钟疯狂调用 10000 次生成短链接的接口，数据库会被瞬间打爆，服务器也会卡死。
- 解决办法：限流。就像地铁站限流一样，每分钟只放 100 个人进去。
- 题目具体要求：对于同一个 user_id="张三"，最近的 10 秒内，他只允许生成 5 次。
- 固定窗口的问题（题目严禁使用）：
  - 假设时间块是 10:00:00 - 10:00:10 这 10 秒。
  - 张三在 10:00:09 发了 5 个请求（用完了配额）。
  - 1 秒钟后到了 10:00:10，计数器归零，他又能发 5 个。
  - 结果：他在 2 秒内（10:00:09 和 10:00:10）实际上发出了 10 个请求，这就把服务器冲垮了。
- 滑动窗口的逻辑（题目强制要求）：
  - 系统会记住张三每一次请求发生的精确时间点（毫秒级）。
  - 每次新请求进来，系统会查一下：过去 10 秒内，张三的请求记录有几条？
  - 如果 ≥ 5 条，直接拒绝（返回 429 Too Many Requests）。
你需要实现一个类似 TinyURL 的短链接生成与跳转服务。该服务需要将长 URL 映射为短码，并支持重定向访问。
核心挑战：系统必须实现基于用户ID的滑动窗口限流，防止单个用户高频创建短链接挤占系统资源。
业务逻辑约束：
1. 短码生成：接收长 URL，返回唯一的短码标识符（长度为 6-8 位字符，由 [a-zA-Z0-9] 组成）。
2. 重定向：访问短码时，返回 302 状态码并跳转至原始长 URL。
3. 限流策略：每个 user_id 在 10 秒内最多允许创建 5 个 短链接（需使用滑动窗口算法，严禁使用固定窗口计数器）。
4. 数据持久化：映射关系需持久化保存（可使用 SQLite 或 PostgreSQL）。
项目结构（云端提供的初始代码框架）
ratelink/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 入口文件（已定义路由骨架）
│   ├── core/
│   │   ├── limiter.py       # 【待实现】滑动窗口限流器
│   │   ├── shortener.py     # 【待实现】短码生成逻辑
│   │   └── storage.py       # 【待实现】数据库存储操作
│   └── models.py            # Pydantic 请求/响应模型（已提供）
├── tests/                   # 评测脚本会动态挂载到此目录（考生无需关心）
├── Dockerfile               # 考生需完善依赖安装部分
├── requirements.txt         # 考生需填写依赖列表
└── docker-compose.yml       # 启动 Redis（用于限流）和数据库（PostgreSQL）
1. app/init.py
# 标记 app 为 Python 包

2. app/models.py
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
from datetime import datetime

class ShortenRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=64, description="用户唯一标识")
    long_url: HttpUrl = Field(..., description="需要缩短的原始长链接")

class ShortenResponse(BaseModel):
    short_url: str = Field(..., description="生成的短链接")
    short_code: str = Field(..., description="短码标识符")
    expires_at: Optional[datetime] = Field(None, description="过期时间，本题暂不使用")

class ErrorResponse(BaseModel):
    detail: str = Field(..., description="错误详情")

3. app/main.py (FastAPI 入口，路由已定义，调用了待实现的模块)
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
from app.models import ShortenRequest, ShortenResponse, ErrorResponse
from app.core import limiter, shortener, storage

app = FastAPI(title="RateLink - High Performance URL Shortener")

@app.on_event("startup")
async def startup_event():
    """服务启动时初始化数据库连接"""
    await storage.initialize()

@app.on_event("shutdown")
async def shutdown_event():
    """服务关闭时清理资源"""
    await storage.cleanup()

@app.post(
    "/api/shorten",
    response_model=ShortenResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}, 429: {"model": ErrorResponse}}
)
async def create_short_url(request: ShortenRequest):
    """
    生成短链接接口
    需依次完成：限流检查 -> 生成短码 -> 持久化存储
    """
    # 1. 检查限流
    allowed = await limiter.check_and_record(request.user_id)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Max 5 requests per 10 seconds."
        )

    # 2. 生成短码并存储
    long_url_str = str(request.long_url)
    short_code = await shortener.generate_unique_code(long_url_str)
    await storage.save_mapping(short_code, long_url_str, request.user_id)

    # 3. 构造响应（域名在评测环境中会被正确处理，此处使用占位符）
    base_url = "http://localhost:8000"
    return ShortenResponse(
        short_url=f"{base_url}/{short_code}",
        short_code=short_code,
        expires_at=None
    )

@app.get(
    "/{short_code}",
    responses={404: {"model": ErrorResponse}}
)
async def redirect_to_long_url(short_code: str):
    """
    短链接跳转接口
    """
    long_url = await storage.get_long_url(short_code)
    if long_url is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short code not found"
        )
    return RedirectResponse(url=long_url, status_code=status.HTTP_302_FOUND)

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "ok"}
4. app/core/init.py
from . import limiter, shortener, storage

5. app/core/limiter.py (待实现：滑动窗口限流器)
"""
滑动窗口限流器
要求：使用 Redis Sorted Set 实现精确的 10 秒滑动窗口，每个 user_id 最多 5 次请求。

提示：
- 使用 redis.asyncio 客户端
- Key 格式: rate_limit:{user_id}
- Score: 请求时间戳（毫秒或秒）
- Member: 唯一标识（建议用 uuid4 字符串）
- 步骤：
  1. 计算窗口起始时间 = 当前时间 - 10 秒
  2. 删除窗口之前的旧记录 (ZREMRANGEBYSCORE)
  3. 统计当前集合大小 (ZCARD)
  4. 若 >= 5，返回 False
  5. 否则添加当前记录 (ZADD) 并返回 True
"""

import redis.asyncio as redis
from typing import Optional

REDIS_URL = "redis://redis:6379/0"
WINDOW_SECONDS = 10
MAX_REQUESTS = 5

_redis_client: Optional[redis.Redis] = None

async def get_redis() -> redis.Redis:
    """获取 Redis 连接单例"""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    return _redis_client

async def check_and_record(user_id: str) -> bool:
    """
    检查用户是否超过限流阈值，若未超过则记录本次请求。
    返回 True 表示允许通过，False 表示被限流。
    """
    # TODO: 实现滑动窗口限流逻辑
    # 提示：使用 await get_redis() 获取连接
    pass
6. app/core/shortener.py (待实现：短码生成逻辑)
"""
短码生成模块
要求：生成长度为 6-8 位的随机字符串，字符集为 [a-zA-Z0-9]。
需保证全局唯一性（建议生成后检查数据库是否已存在）。
"""

import secrets
import string

ALPHABET = string.ascii_letters + string.digits
CODE_LENGTH = 6  # 可考虑在 6-8 之间动态选择

async def generate_unique_code(long_url: str) -> str:
    """
    生成一个全局唯一的短码。
    若生成的短码已存在于数据库中，需重新生成（最多重试 3 次）。
    """
    # TODO: 实现短码生成逻辑，并检查唯一性
    # 提示：需调用 storage.code_exists() 方法
    pass
7. app/core/storage.py (待实现：数据库存储操作)
"""
数据持久化模块
要求：使用 asyncpg 连接 PostgreSQL，存储短码与长 URL 的映射关系。
表结构需在 initialize() 中自动创建。
"""

import asyncpg
from typing import Optional

_pool: Optional[asyncpg.Pool] = None

DATABASE_URL = "postgresql://postgres:postgres@postgres:5432/ratelink"

async def initialize():
    """初始化数据库连接池并创建表（如不存在）"""
    global _pool
    # TODO: 创建连接池
    # TODO: 执行 CREATE TABLE IF NOT EXISTS 语句
    # 建议表结构：
    # CREATE TABLE url_mappings (
    #     id SERIAL PRIMARY KEY,
    #     short_code VARCHAR(8) UNIQUE NOT NULL,
    #     long_url TEXT NOT NULL,
    #     user_id VARCHAR(64) NOT NULL,
    #     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    # );
    pass

async def cleanup():
    """关闭数据库连接池"""
    global _pool
    # TODO: 关闭连接池
    pass

async def save_mapping(short_code: str, long_url: str, user_id: str) -> None:
    """保存短码与长 URL 的映射"""
    # TODO: 插入数据，注意处理 UNIQUE 冲突（若短码已存在应抛出异常）
    pass

async def get_long_url(short_code: str) -> Optional[str]:
    """根据短码查询原始长 URL，不存在则返回 None"""
    # TODO: 查询数据库
    pass

async def code_exists(short_code: str) -> bool:
    """检查短码是否已被占用"""
    # TODO: 查询数据库判断是否存在
    pass
8. requirements.txt
fastapi==0.115.6
uvicorn[standard]==0.34.0
redis==5.2.1
asyncpg==0.30.0
pydantic==2.10.4
9. Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

10. docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./app:/app/app  # 热加载，代码修改后自动重启
    depends_on:
      - redis
      - postgres
    environment:
      - REDIS_URL=redis://redis:6379/0
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/ratelink

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: ratelink
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:


评分规则
评测系统将通过执行一个 Python 测试套件来打分。
暂时无法在飞书文档外展示此内容
作答环境说明
1. 开发环境：本题在 Docker 隔离环境中作答，平台为你分配一个独立的云端 VS Code 窗口（基于 code-server），你可以直接在浏览器中进行编码和调试。
2. 语言版本：Python 3.11。
3. 依赖服务：作答环境中已通过 docker-compose 启动以下辅助容器：
  - Redis 7.0（地址：redis:6379，用于实现滑动窗口计数）。
  - PostgreSQL 15（地址：postgres:5432，数据库名 ratelink，用户名 postgres，密码 postgres）。
4. 热加载：修改代码后保存，FastAPI 服务会自动重启，方便你使用内置终端进行 curl 测试。
5. 提交方式：点击界面上的 【提交评测】 按钮，系统会拉取你当前的代码快照，执行隐藏的测试套件，并在 30 秒内返回详细得分报告。
资源配额（每个作答实例）
- CPU 限制：1.0 核（若超限使用会被 Docker 内核节流，导致延迟飙升影响得分）。
- 内存限制：512 MB（超出会被 OOM Killer 强制终止，得分为 0）。
- 磁盘限制：1 GB。
- 网络：容器内部可互通（App -> Redis/Postgres），外网访问受限（无法下载未预置的第三方库，请在 requirements.txt 中提前声明）。