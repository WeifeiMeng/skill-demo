# Mini CodeSandbox

一个基于 Docker 的在线开发环境管理平台，支持容器化开发环境创建、在线代码编辑、考试评测和管理员后台。

## 项目架构

```
skills-demo/
├── frontend/          # 用户端前端 (Vue 3 + Vite, 端口 3000)
├── frontend-admin/    # 管理后台前端 (Vue 3 + Vite, 端口 3001)
├── backend/           # API 后端 (FastAPI, 端口 8000)
├── docker/            # Docker 镜像构建文件
└── docker-compose.yml
```

## 技术栈

| 层级 | 技术 |
|------|------|
| 用户端前端 | Vue 3 (Composition API) + Vue Router + Vite |
| 管理后台前端 | Vue 3 + Vite |
| 后端 | FastAPI + PyMySQL + Docker Python SDK + JWT 认证 |
| 数据库 | MySQL |
| 容器 | codesandbox-image / ai-coach-codesandbox |

## 快速开始

### 1. 构建 Docker 镜像

项目包含两个 Docker 镜像定义，按顺序构建：

**基础镜像 (ai-coach:0.1)**

基于 `codercom/code-server`，预装 Python 3.12、Node.js 22 和 sudo：

```bash
cd docker
docker build -t ai-coach:0.1 -f Dockerfile .
```

**完整镜像 (ai-coach-codesandbox)**

在基础镜像之上安装 Claude Code CLI 和网络诊断工具：

```bash
docker build -t ai-coach-codesandbox:latest -f Dockerfile.ai-coach .
```

或者使用 docker-compose 一键构建：

```bash
docker compose build
```

### 2. 启动后端

```bash
cd backend

# 安装依赖
uv sync

# 启动服务
uvicorn main:app --port 8000 --reload
```

后端默认运行在 `http://localhost:8000`。

### 3. 启动前端

**用户端 (端口 3000)**

```bash
cd frontend
npm install
npm run dev
```

**管理后台 (端口 3001)**

```bash
cd frontend-admin
npm install
npm run dev
```

### 4. 访问系统

| 入口 | 地址 |
|------|------|
| 用户端 | http://localhost:3000 |
| 管理后台 | http://localhost:3001/login |
| API 文档 | http://localhost:8000/docs |

## 管理员账号

| 邮箱 | 密码 |
|------|------|
| `admin@test.com` | `admin123` |

## API 路由

### 认证 (`/auth`)

| 端点 | 方法 | 描述 |
|------|------|------|
| `/auth/login` | POST | 用户登录 |
| `/auth/register` | POST | 用户注册 |

### 容器管理 (`/containers`)

| 端点 | 方法 | 描述 |
|------|------|------|
| `/containers/create_env` | POST | 创建新开发容器，返回 `{container_id, port}` |
| `/containers` | GET | 获取所有容器列表 |

### Docker 镜像 (`/images`)

| 端点 | 方法 | 描述 |
|------|------|------|
| `/images/list` | GET | 列出所有可用镜像 |

### 文章 (`/articles`)

| 端点 | 方法 | 描述 |
|------|------|------|
| `/articles` | GET | 获取文章列表 |
| `/articles/{id}` | GET | 获取文章详情 |

### 考试 (`/exams`)

| 端点 | 方法 | 描述 |
|------|------|------|
| `/exams/sessions` | GET | 获取考试场次 |
| `/exams/submit` | POST | 提交考试答案 |

### 管理后台 (`/admin`)

| 端点 | 方法 | 描述 |
|------|------|------|
| `/admin/students` | GET | 学生列表 |
| `/admin/students/{id}` | GET | 学生详情 |
| `/admin/exam-sessions` | GET | 考试场次管理 |
| `/admin/grading` | POST | 批改打分 |
| `/admin/monitor` | GET | 考试监控 |

## 环境变量

后端通过 `backend/setting.toml` 配置文件管理数据库连接等信息。

## 容器端口范围

创建开发环境时，系统会在 `20000-30000` 范围内随机分配端口，创建后可直接在新标签页中打开对应容器环境。
