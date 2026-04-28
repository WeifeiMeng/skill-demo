# 项目架构文档

## 项目概述

在线编程考试平台。用户登录后看到题目列表，点击题目进入考试页面，页面内嵌 code-server（VS Code Web 版）进行编程作答，容器按题目隔离工作目录。

## 技术栈

| 层 | 技术 |
| --- | --- |
| 前端 | Vue 3 (Composition API, script setup) + Vite |
| 后端 | FastAPI + Docker Python SDK |
| 数据库 | MySQL (PyMySQL) |
| 认证 | JWT (7 天过期) |
| 容器 | code-server (codercom/code-server) |
| 包管理 | 前端 npm / 后端 uv |

## 项目结构

```
/
├── docker/
│   ├── Dockerfile              # code-server 镜像定义
│   └── docker-compose.yml      # 构建带 ai-coach 前缀的镜像
│
├── backend/
│   ├── main.py                 # FastAPI 入口，注册路由 & CORS
│   ├── setting.toml            # 配置文件（数据库、Docker、JWT）
│   ├── pyproject.toml          # Python 依赖
│   ├── uv.lock
│   │
│   ├── articles/               # 题目 Markdown 文件
│   │   └── deep-face-search.md
│   │
│   ├── workspaces/             # 容器工作目录（自动生成）
│   │   └── {username}/
│   │       └── {article_name}/
│   │
│   ├── route/                  # API 路由层
│   │   ├── auth.py             # POST /auth/login, /auth/register
│   │   ├── article.py          # GET /articles
│   │   ├── docker_container.py # POST /create_env, GET /containers, 容器启停删
│   │   ├── dependencies.py     # JWT 认证依赖
│   │   └── __init__.py
│   │
│   ├── service/                # 业务逻辑层
│   │   ├── article_service.py  # 题目列表 & 名称映射
│   │   ├── docker_manager.py   # Docker 容器/镜像管理
│   │   └── auth_service.py     # 密码哈希 & JWT 令牌
│   │
│   ├── dao/
│   │   └── user_dao.py         # 用户数据访问
│   │
│   ├── middleware/
│   │   └── database.py         # MySQL 数据库连接
│   │
│   └── schema/
│       └── user.py             # User 数据类
│
└── frontend/
    ├── index.html
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── main.js             # Vue 入口
        ├── App.vue             # 根组件（导航：登录 → 题目列表 → 考试）
        ├── Exam.vue            # 考试页面（顶部栏 + iframe code-server）
        ├── Login.vue           # 登录/注册页面
        └── style.css           # 全局样式
```

## 后端架构

### API 路由

| 方法 | 路径 | 说明 | 认证 |
| --- | --- | --- | --- |
| POST | `/auth/register` | 注册 | 否 |
| POST | `/auth/login` | 登录 | 否 |
| GET | `/articles` | 获取题目列表 | JWT |
| POST | `/create_env` | 创建/获取考试容器 | JWT |
| GET | `/containers` | 获取所有容器 | JWT |
| POST | `/containers/{id}/stop` | 停止容器 | JWT |
| POST | `/containers/{id}/start` | 启动容器 | JWT |
| POST | `/containers/{id}/remove` | 删除容器 | JWT |
| GET | `/db/test` | 测试数据库连接 | 否 |

### 数据流：创建考试环境

```
用户点击题目
  → POST /create_env { image, article }
  → docker_container.py
      → find_container_by_article(user, article)
          → 已有容器? → 如果 stopped 则 start → 返回 { container_id, port, status }
          → 没有? → create_container(user, image, article)
  → create_container()
      → 生成 env-xxx 容器名
      → 创建目录 workspaces/{username}/{article}/
      → 复制 articles/{article}.md → workspaces/{username}/{article}/
      → Docker 创建容器，挂载工作目录到 /workspace
      → 返回 { container_id, port, workspace }
```

### 关键函数

#### `service/docker_manager.py`

| 函数 | 说明 |
| --- | --- |
| `create_container(username, image, article_name)` | 创建容器，自动分配端口(20000-30000)，打 label(user/article) |
| `find_container_by_article(username, article_name)` | 按 label 查找已有容器 |
| `get_containers()` | 获取所有容器（含端口、挂载目录） |
| `get_next_env_name()` | 生成递增容器名 env-001, env-002... |
| `stop/start/remove_container(id)` | 容器生命周期管理 |

#### `service/article_service.py`

| 函数 | 说明 |
| --- | --- |
| `list_articles()` | 扫描 articles/ 目录，返回题目列表 [{filename, title}] |

标题获取优先级：
1. `NAME_MAP` 映射表（`deep-face-search.md` → `深度人脸搜索`）
2. markdown 第一个 `# ` 标题
3. 文件名转可读标题（fallback）

## 前端架构

### 组件树

```
App.vue
├── Login.vue          （未登录时）
├── Exam.vue           （点击题目后，currentExam !== null）
│   ├── 顶部栏（标题 + 倒计时 + 完成按钮）
│   └── iframe（code-server）
└── 题目列表            （已登录，无考试时）
    └── 题目卡片（点击 → launchEnv → 切换到 Exam）
```

### 视图切换逻辑

```
未登录        → Login.vue
已登录 + 无考试 → 题目列表
已登录 + 有考试 → Exam.vue
```

### 考试页面 (Exam.vue)

- **挂载时**：调用 `POST /create_env` 获取容器
- **Loading 状态**：显示 spinner + "正在准备考试环境..."
- **就绪后**：顶部栏（题目名 + 倒计时 120 分钟 + 完成按钮）+ iframe 嵌入 code-server
- **倒计时 ≤ 5 分钟**：变红闪烁
- **点击完成/返回**：`emit('finish')` → App.vue 回到题目列表

## Docker

### 镜像构建

```bash
docker build -t ai-coach-codesandbox:latest -f docker/Dockerfile docker/
# 或
docker compose build
```

### 容器默认镜像

配置在 `setting.toml` 的 `docker.default_image`，当前为 `codesandbox-image-new:latest`。

### 容器标签

创建时自动打 label：
- `user={username}` — 所属用户
- `article={article_name}` — 关联题目

用于 `find_container_by_article()` 实现复用（同一用户点同一题目不会重复创建）。

## 配置

`backend/setting.toml`：

```toml
[database]
host = "localhost"
port = 3306
user = "root"
password = "123456"
database = "skills_demo"
charset = "utf8mb4"

[docker]
workspaces_base = "workspaces"
default_image = "codesandbox-image-new:latest"

[auth]
secret = "your-secret-key-change-in-production"
```

## 端口

| 服务 | 端口 |
| --- | --- |
| 后端 (FastAPI) | 8000 |
| 前端 (Vite) | 3000 |
| 容器 (code-server) | 20000-30000 随机 |

## 启动命令

```bash
# 后端
cd backend && uvicorn main:app --reload --port 8000

# 前端
cd frontend && npm install && npm run dev
```

## 关键流程

### 题目 → 考试容器

```
前端                            后端
 │                               │
 ├─ 点击题目卡片 ───────────────→ │
 │                               ├─ find_container_by_article()
 │                               │   ├─ 有 → start() 如果 stopped
 │                               │   └─ 无 → create_container()
 │                               │            ├─ 创建工作目录
 │                               │            ├─ 复制 .md 文件
 │                               │            └─ docker run
 │                               ├─ 返回 { port, ... }
 │←─ 显示 iframe: localhost:port ─│
```

### 复用容器

```
再次点击同一题目
  → find_container_by_article(user, article)
  → label 匹配 → 返回已有容器 port
  → 直接进入 code-server（保留之前的文件）
```
