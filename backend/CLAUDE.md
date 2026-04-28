# Claude Code 项目笔记

## 项目概述
Mini CodeSandbox - Docker 开发环境管理界面

## 技术栈
- 前端：Vue 3 + Vite
- 后端：FastAPI + Docker Python SDK
- 容器镜像：codesandbox-image

## 项目结构
```
backend/
  main.py              # FastAPI 应用入口
  setting.toml        # 配置文件（数据库、Docker、JWT）
  route/
    auth.py            # 认证路由（注册/登录）
    docker_container.py  # 容器管理路由
    docker_image.py   # 镜像列表路由
    dependencies.py   # JWT 认证依赖
  service/
    auth_service.py    # 密码哈希、JWT 令牌
    docker_manager.py  # Docker 操作封装
  middleware/
    database.py        # MySQL 数据库连接
  dao/
    user_dao.py        # 用户数据访问层
  schema/
    user.py            # User 数据类

frontend/
  src/
    App.vue            # 主组件
    Login.vue          # 登录页面
```

## 关键文件说明

### main.py
- `POST /create_env` - 创建新 Docker 容器
- `GET /containers` - 获取所有容器列表
- `GET /db/test` - 测试数据库连接
- CORS 配置允许 http://localhost:3000

### service/docker_manager.py
- `create_container()` - 随机端口(20000-30000)启动 codesandbox-image
- `get_containers()` - 返回所有 Docker 容器
- `stop_container()` / `start_container()` / `remove_container()`
- `get_images()` - 获取 Docker 镜像列表

### service/auth_service.py
- JWT 认证，7 天过期
- bcrypt 密码哈希

### setting.toml
```toml
[database]
host = "localhost"
port = 3306
user = "root"
password = ""
database = "skills_demo"

[docker]
workspaces_base = "workspaces"

[auth]
secret = "your-secret-key-change-in-production"
```

## 端口
- 后端：8000
- 前端：3000
- 容器：20000-30000 随机

## 依赖管理（uv）
- 所有依赖在 `.venv` 中
- 启动后端：`uvicorn main:app --reload --port 8000`
- 安装依赖：`uv sync`

## 数据库
- MySQL，需提前创建 `skills_demo` 数据库
- 用户表自动创建（module 加载时）
