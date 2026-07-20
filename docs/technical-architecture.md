# AI Done 技术架构文档

## 一、项目概述

AI Done 是一个**在线编程挑战平台**，为用户提供基于 Docker 容器的隔离式开发环境，支持在线编码、自动评测、考试管理和竞赛排名。平台分为 C 端（考生端）和 B 端（管理后台），并通过 LLM 集成提供 AI 辅助编程能力。

---

## 二、整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户浏览器                                │
└──────────┬──────────────────────────────────┬───────────────────┘
           │                                  │
     localhost:3000                      localhost:3001
     (C端 SPA)                           (管理后台 SPA)
           │                                  │
           ▼                                  ▼
┌──────────────────────┐          ┌──────────────────────┐
│   frontend/          │          │   frontend-admin/    │
│   Vue 3 + Vite       │          │   Vue 3 + Vite       │
│   Vue Router         │          │   Vue Router         │
│   Mock Data 降级     │          │                      │
└──────────┬───────────┘          └──────────┬───────────┘
           │                                  │
           └──────────────┬───────────────────┘
                          │ HTTP REST API
                          ▼
           ┌──────────────────────────────┐
           │  backend/  FastAPI :8000     │
           │  ┌────────  ───────┐        │
           │  │ Route  Layer      │        │
           │  │ Service Layer     │        │
           │  │ DAO    Layer      │        │
           │  │ Schema Layer      │        │
           │  └──────────────────┘        │
           └──────┬───────────┬───────────┘
                  │           │
          PyMySQL │           │ Docker SDK
                  ▼           ▼
        ┌──────────────┐  ┌─────────────────────┐
        │  MySQL       │  │  Docker Engine      │
        │  :3306       │  │  ┌─────────────────┐│
        │              │  │  │ 容器 (env-xxx)   ││
        │  skills_demo │  │  │ :20000~30000     ││
        │              │  │  │ code-server:8080 ││
        └──────────────┘  │  │ AI Coach 环境    ││
                          │  └─────────────────┘│
                          └─────────────────────┘
                                   │
                           llm-pipe :8002
                           (API Key 管理 / Anthropic 代理)
```

### 技术栈总览

| 层级 | 技术选型 | 说明 |
|------|---------|------|
| C 端前端 | Vue 3 + Vite + Vue Router | Composition API，SPA 模式 |
| B 端前端 | Vue 3 + Vite + Vue Router | 独立前端应用（端口 3001） |
| 后端框架 | FastAPI (Python) | 异步 Web 框架，端口 8000 |
| 数据库 | MySQL 8.0 | 关系型数据库，PyMySQL 驱动 |
| 容器编排 | Docker Python SDK | 动态创建/管理隔离开发环境 |
| 认证 | JWT (HS256) + bcrypt | 7 天过期，python-jose + passlib |
| 配置管理 | TOML | setting.toml 集中配置 |
| 包管理 | uv (Python) / npm (Node) | 依赖锁定 |
| 容器镜像 | codercom/code-server | 基于 Web 的 VS Code 环境 |

---

## 三、后端架构详解

### 3.1 目录结构

```
backend/
├── main.py                    # FastAPI 入口，CORS + 路由注册
├── setting.toml               # 全局配置文件
├── pyproject.toml             # Python 依赖声明
│
├── route/                     # 路由层（API 端点）
│   ├── auth.py                # 注册/登录/获取当前用户
│   ├── article.py             # 题目列表（C 端）
│   ├── exam.py                # 考试：开始/计时/提交评测
│   ├── admin.py               # 管理后台：CRUD 题目/仪表盘/考生管理
│   ├── docker_container.py    # 容器生命周期管理
│   ├── docker_image.py        # 镜像列表
│   └── dependencies.py        # JWT 认证依赖注入
│
├── service/                   # 业务逻辑层
│   ├── auth_service.py        # 密码哈希、JWT 签发与验证
│   ├── docker_manager.py      # Docker 容器/镜像/测试执行
│   └── article_service.py     # 题目发现（基于文件系统）
│
├── dao/                       # 数据访问层
│   ├── user_dao.py            # 用户 CRUD + 表初始化
│   ├── exam_session_dao.py    # 考试会话管理
│   └── exam_result_dao.py     # 考试结果存储与统计
│
├── schema/                    # 数据实体定义
│   ├── user.py                # User dataclass
│   ├── exam_session.py        # ExamSession dataclass
│   └── exam_result.py         # ExamResult dataclass
│
├── middleware/
│   └── database.py            # PyMySQL 连接上下文管理器
│
├── articles/                  # 题目文件存储
│   └── {article-name}/
│       ├── readme.md          # 题目描述
│       ├── test_config.json   # 评测配置
│       └── attachments/       # 附件（测试数据等）
│
├── tests/                     # 评测脚本
│   └── {article-name}/
│       └── test.py            # 在容器内执行的测试脚本
│
└── workspaces/                # 用户工作目录
    └── {username}/
        └── {article-name}/    # 挂载到容器的 /workspace
```

### 3.2 分层架构

遵循**三层架构**模式：

```
┌──────────┐     ┌───────────┐     ┌────────┐
│  Route   │ ──▶ │  Service  │ ──▶ │  DAO   │ ──▶ MySQL
│ (API层)  │     │ (业务层)  │     │ (数据层) │
└──────────┘     └───────────┘     └────────┘
      │                │
      │                ▼
      │          ┌───────────┐
      │          │  Docker   │ ──▶ Docker Engine
      │          │  SDK      │
      │          └───────────┘
      │
      ▼
  Schema (dataclass)
  Pydantic (请求模型)
```

- **Route 层**：仅处理 HTTP 请求/响应，参数校验，调用 Service/DAO
- **Service 层**：核心业务逻辑，如 Docker 操作、密码加密、JWT 签发、题目扫描
- **DAO 层**：数据库 CRUD 操作，表结构自动迁移（模块加载时执行 `CREATE TABLE IF NOT EXISTS`）
- **Schema 层**：使用 Python `dataclass` 定义实体，使用 Pydantic `BaseModel` 定义请求模型
- **Middleware 层**：数据库连接管理，通过 `contextmanager` 确保连接正确关闭

### 3.3 API 路由一览

| 前缀 | 模块 | 主要端点 | 认证 |
|------|------|---------|------|
| `/auth` | auth.py | POST `/register`, `/login`, GET `/me` | 部分公开 |
| `/articles` | article.py | GET `/` 题目列表 | 公开 |
| `/challenges` | article.py | GET `/` 题目列表（兼容前端） | 公开 |
| `/exam` | exam.py | POST `/start`, `/submit`, `/finish`, GET `/time` | JWT |
| `/admin` | admin.py | CRUD `/articles`, GET `/dashboard`, `/students` | JWT + Admin |
| `/images` | docker_image.py | GET `/` 镜像列表 | JWT |
| (root) | docker_container.py | POST `/create_env`, GET `/containers`, 容器启停 | JWT |

### 3.4 认证与授权

```
用户注册/登录
      │
      ▼
bcrypt 哈希密码 ──▶ MySQL users 表
      │
      ▼
JWT 签发 (HS256, 7天有效)
sub: user_id, email, role
      │
      ▼
前端 localStorage 存储 token
      │
      ▼
后续请求 header: Authorization: Bearer <token>
      │
      ▼
dependencies.py:
  get_current_user() → 解析 JWT → 查询 user
  get_admin_user()   → 校验 role == "admin"
```

- C 端公开路由：首页、题目列表无需登录
- C 端受限路由：考试相关需要 JWT 认证
- B 端全受限：所有 `/admin/*` 路由需要 JWT + admin 角色

---

## 四、容器化环境机制

### 4.1 镜像体系

```
codercom/code-server:latest          # 基础镜像（Web VS Code）
        │
        ▼
ai-coach:0.1 (Dockerfile)            # + Python 3.12 + Node.js 22
        │
        ▼
ai-coach:1.0 (Dockerfile.ai-coach)   # + Claude Code CLI + 网络工具
                                      #   (ping, curl, wget, dig, telnet, vim)
```

镜像提供标准化的开发环境：
- **code-server**：基于 Web 的 VS Code，监听 8080 端口，无密码认证
- **Python 3.12** + pip：支持 Python 编程题
- **Node.js 22** + npm：支持前端/Node.js 题目
- **Claude Code CLI**：AI 辅助编程工具
- **sudo 权限**：coder 用户拥有无密码 sudo

### 4.2 容器生命周期

```
用户选择题目 → 点击"开始挑战"
      │
      ▼
POST /create_env { image, article }
      │
      ├─ find_container_by_article() → 已有容器？→ 复用/重启
      │
      └─ create_container():
           ├─ 随机端口 20000-30000
           ├─ 创建 workspace 目录并复制题目文件
           ├─ 从 llm-pipe 获取用户 API Key
           ├─ 注入环境变量 (ANTHROPIC_API_KEY, ANTHROPIC_BASE_URL)
           ├─ docker run -p {port}:8080 -v workspace:/workspace
           └─ 返回 container_id + port
      │
      ▼
前端 window.open(http://localhost:{port}) → code-server 界面
      │
      ▼
用户在容器内编码
      │
      ▼
POST /exam/submit { article, container_id }
      │
      └─ exec_test():
           ├─ pip install -r requirements.txt
           ├─ base64 编码 test.py → 容器内 exec_run 执行
           ├─ 解析 stdout 中的 JSON 结果
           └─ 存储到 exam_results 表
```

### 4.3 容器特性

- **标签追踪**：容器打上 `user` 和 `article` 标签，支持按用户/题目查找
- **端口映射**：容器 8080 → 宿主机随机端口 (20000-30000)
- **卷挂载**：`workspaces/{user}/{article}` → 容器 `/workspace`
- **环境注入**：自动注入 Anthropic API 配置到容器环境变量和 `.bashrc`
- **网络配置**：`extra_hosts` 设置使容器可通过 `host.docker.internal` 访问宿主机服务

---

## 五、数据库设计

### 5.1 ER 图

```
┌──────────────┐       ┌──────────────────────┐       ┌──────────────────────┐
│    users     │       │    exam_sessions     │       │    exam_results      │
├──────────────┤       ├──────────────────────┤       ├──────────────────────┤
│ id (PK)      │──┐    │ id (PK)              │       │ id (PK)              │
│ name         │  │    │ user_id (FK)    ─────┼──┐    │ user_id (FK)    ─────┼──┐
│ email (UQ)   │  └───▶│ article_name         │  │    │ article_name         │  │
│ password     │       │ container_id         │  │    │ score               │  │
│ role         │       │ started_at           │  │    │ max_score           │  │
│ avatar       │       │ ended_at             │  │    │ passed              │  │
│ created_at   │       │ status               │  │    │ cases_json          │  │
│ updated_at   │       │ created_at/updated_at│  │    │ submitted_at        │  │
└──────────────┘       └──────────────────────┘  │    └──────────────────────┘  │
                                                  │                             │
              ┌───────────────────────────────────┘                             │
              │  (user_id, article_name) 联合约束                               │
              └─────────────────────────────────────────────────────────────────┘
```

### 5.2 数据表

**users** — 用户表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK AUTO_INCREMENT | 用户 ID |
| name | VARCHAR(100) | 用户名 |
| email | VARCHAR(255) UNIQUE | 邮箱（唯一） |
| password | VARCHAR(255) | bcrypt 哈希密码 |
| role | VARCHAR(20) DEFAULT 'user' | 角色：user / admin |
| avatar | VARCHAR(500) | 头像 URL |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

**exam_sessions** — 考试会话表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK | 会话 ID |
| user_id | INT FK | 用户 ID |
| article_name | VARCHAR(255) | 题目名称 |
| container_id | VARCHAR(255) | 关联容器 ID |
| started_at | DATETIME | 开始时间 |
| ended_at | DATETIME | 结束时间 |
| status | VARCHAR(20) DEFAULT 'active' | active / finished |

> 联合唯一约束 `(user_id, article_name)` 确保每个用户每道题只有一个活跃会话。

**exam_results** — 考试提交记录表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK | 记录 ID |
| user_id | INT FK | 用户 ID |
| article_name | VARCHAR(255) | 题目名称 |
| score | INT DEFAULT 0 | 实际得分 |
| max_score | INT DEFAULT 100 | 满分 |
| passed | BOOLEAN DEFAULT FALSE | 是否通过 |
| cases_json | TEXT | 测试用例详情 (JSON) |
| submitted_at | DATETIME | 提交时间 |

### 5.3 表自动迁移

所有 DAO 模块在加载时自动执行 `CREATE TABLE IF NOT EXISTS`，无需手动运行 SQL 脚本。`UserDao.init_table()` 还包含 `ALTER TABLE` 兼容旧表结构的迁移逻辑。

---

## 六、前端架构

### 6.1 C 端 (frontend/)

```
frontend/src/
├── main.js              # Vue 应用入口
├── App.vue              # 根组件（导航 + 路由出口）
├── style.css            # 全局样式
├── router.js            # 路由定义 + 导航守卫
│
├── data/
│   ├── api.js           # API 封装（自动降级 mock）
│   └── mockData.js      # Mock 数据工厂
│
├── components/          # 可复用组件
│   ├── AdminLayout.vue  # B 端布局外壳
│   ├── StatCard.vue     # 统计卡片
│   ├── StatusBadge.vue  # 状态标签
│   ├── ScoreBar.vue     # 分数进度条
│   ├── CircleProgress.vue  # 环形进度
│   ├── ProcessBar.vue   # 步骤进度条
│   ├── CodeBlock.vue    # 代码高亮
│   ├── RatingCard.vue   # 评级卡片
│   ├── FilterChip.vue   # 筛选标签
│   ├── TestCaseEditor.vue  # 测试用例编辑
│   └── AttachmentList.vue  # 附件列表
│
└── 页面组件
    ├── Landing.vue      # 首页引导页
    ├── Home.vue         # 题目列表
    ├── Exam.vue         # 考试/编码页
    ├── Completed.vue    # 完成结果页
    ├── Solutions.vue    # 题解浏览
    ├── Contest.vue      # 竞赛页
    ├── Leaderboard.vue  # 排行榜
    │
    └── Admin*.vue       # B 端管理页（懒加载）
        ├── AdminLogin.vue
        ├── AdminDashboard.vue
        ├── AdminArticles.vue
        ├── AdminArticleEdit.vue
        ├── AdminStudents.vue
        ├── AdminStudentDetail.vue
        ├── AdminExamSessions.vue
        ├── AdminMonitor.vue
        └── AdminGrading.vue
```

### 6.2 路由设计

| 路径 | 组件 | 说明 |
|------|------|------|
| `/` | Landing | 平台首页 |
| `/challenges` | Home | 题目列表 |
| `/exam/:filename` | Exam | 在线考试/编码 |
| `/completed/:filename` | Completed | 提交结果 |
| `/solutions` | Solutions | 题解浏览（懒加载） |
| `/contest` | Contest | 竞赛页面（懒加载） |
| `/leaderboard` | Leaderboard | 排行榜（懒加载） |
| `/admin/login` | AdminLogin | 管理员登录 |
| `/admin/*` | Admin* | 管理后台（全部懒加载） |

**导航守卫**：访问 `/admin/*` 路由时，检查 `localStorage` 中是否存在 `admin_token`，无 token 则重定向到登录页。

### 6.3 API 降级策略

前端 API 层 (`api.js`) 实现了**自动降级**机制：

```javascript
async function fetchOrMock(url, options, mockFn) {
  try {
    const res = await fetch(url, options)
    if (res.ok) return res.json()
  } catch (_) {
    // 网络错误等，静默降级
  }
  return typeof mockFn === 'function' ? mockFn() : mockFn
}
```

- 优先请求真实后端 API
- 后端不可用时自动回退到 `mockData.js` 中的本地数据
- 保证前端可独立开发、演示，不依赖后端运行状态

### 6.4 B 端独立应用 (frontend-admin/)

除嵌入在 C 端 SPA 中的 Admin 页面外，还有一个独立的 **frontend-admin** 应用（端口 3001），提供独立部署的管理后台，结构更简洁：

```
frontend-admin/src/
├── main.js / App.vue / router.js / style.css
├── components/    (Sidebar, StatCard, AttachmentList, TestCaseEditor)
└── views/         (Login, Dashboard, ArticleList, ArticleEdit, StudentList, StudentDetail)
```

### 6.5 依赖与构建

| 依赖 | 版本 | 用途 |
|------|------|------|
| vue | ^3.4.0 | 前端框架 |
| vue-router | ^4.6.4 | SPA 路由 |
| marked | ^18.0.4 | Markdown 渲染 |
| vite | ^5.0.0 | 构建工具 |
| @vitejs/plugin-vue | ^5.0.0 | Vue SFC 编译 |

---

## 七、LLM 集成架构

```
用户容器 (code-server)
      │
      ├─ 环境变量: ANTHROPIC_API_KEY, ANTHROPIC_BASE_URL, ANTHROPIC_MODEL
      │
      └─ Claude Code CLI (容器内全局安装)
              │
              ▼
      llm-pipe (:8002)
      ├── /api/v1/users/{id}/api-key     → 获取用户 API Key
      └── /api/v1/proxy/anthropic        → Anthropic API 代理
              │
              ▼
      Anthropic API (外部)
```

- 创建容器时，后端从 llm-pipe 获取用户的专属 API Key
- 将 API Key 和代理地址注入容器环境变量
- 容器内 Claude Code CLI 通过这些配置连接 AI 服务
- llm-pipe 作为中间层统一管理 API Key 和请求代理

---

## 八、评测系统

### 评测流程

```
POST /exam/submit
      │
      ▼
exec_test(container_id, article_name)
      │
      ├─ 1. 读取 backend/tests/{article}/test.py
      ├─ 2. pip install -r /workspace/requirements.txt (容器内)
      ├─ 3. base64 编码 test.py → 容器内 python3 -c exec(...)
      │
      ▼
      test.py 执行 → stdout 输出 JSON:
      {
        "score": 80,
        "max_score": 100,
        "passed": true,
        "cases": [
          {"name": "测试1", "passed": true, "message": ""},
          {"name": "测试2", "passed": false, "message": "Expected X got Y"}
        ]
      }
      │
      ▼
  解析 JSON → 返回前端 + 存储 exam_results
```

### 题目组织

每个题目是一个独立的目录，包含：
- `readme.md` — 题目描述（第一个 `# 标题` 作为题目标题）
- `test_config.json` — 评测配置（如超时时间、权重等）
- `attachments/` — 附件（测试数据文件、脚手架代码等）

对应的评测脚本位于 `backend/tests/{article-name}/test.py`。

---

## 九、部署架构

### 9.1 开发环境

```bash
# 启动后端
cd backend && uvicorn main:app --reload --port 8000

# 启动 C 端前端
cd frontend && npm run dev          # → localhost:3000

# 启动 B 端前端
cd frontend-admin && npm run dev    # → localhost:3001
```

### 9.2 Docker 环境

```bash
# 构建 AI Coach 镜像
docker compose build                # 基于 docker/Dockerfile

# 或手动构建完整版
docker build -f docker/Dockerfile.ai-coach -t ai-coach:1.0 docker/
```

### 9.3 依赖服务

| 服务 | 端口 | 必需 | 说明 |
|------|------|------|------|
| MySQL | 3306 | 是 | 数据持久化 |
| Docker Engine | - | 是 | 容器管理 |
| llm-pipe | 8002 | 否 | LLM API 代理（不可用时容器无 AI 功能） |

---

## 十、配置管理

所有配置集中在 `backend/setting.toml`：

```toml
[database]              # MySQL 连接
host / port / user / password / database / charset

[docker]                # Docker 配置
workspaces_base         # 工作目录相对路径
default_image           # 默认容器镜像名

[auth]                  # JWT 密钥
secret                  # 生产环境务必更换

[llm_pipe]              # LLM 代理服务
base_url                # llm-pipe 地址
model                   # 默认模型
```

---

## 十一、安全设计

- **密码安全**：bcrypt 哈希存储，不可逆
- **认证**：JWT HS256，7 天过期，前端 localStorage 存储
- **授权**：路由守卫 (前端) + `get_admin_user()` 依赖注入 (后端) 双重校验
- **容器隔离**：每个用户每题独立容器，随机端口映射
- **文件安全**：`os.path.basename()` 防止路径穿越攻击
- **CORS**：仅允许 localhost:3000/3001 跨域访问

---

## 十二、技术路线总结

| 维度 | 选择 | 理由 |
|------|------|------|
| 前端框架 | Vue 3 (Composition API) | 响应式、生态成熟、学习曲线平缓 |
| 后端框架 | FastAPI | 高性能异步、自动 OpenAPI 文档、类型安全 |
| 数据库 | MySQL + PyMySQL | 关系型需求明确、社区成熟、直接 SQL 无 ORM 开销 |
| 容器方案 | Docker + code-server | Web IDE 无需本地环境、隔离安全、资源可控 |
| 认证方案 | JWT + bcrypt | 无状态扩展、工业标准 |
| 评测方案 | Docker exec + base64 注入 | 简单可靠、无需额外服务 |
| 文件存储 | 本地文件系统 | 题目/附件规模小、无需对象存储 |
| Mock 降级 | fetchOrMock 策略 | 前后端解耦、可独立开发演示 |
| LLM 集成 | llm-pipe 代理 | 统一 API Key 管理、安全可控 |
