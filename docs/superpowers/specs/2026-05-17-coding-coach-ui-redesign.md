# Coding Coach UI Redesign

## 概述
将 Mini CodeSandbox 的前端从暗色 AI 风格改造为清新毛玻璃风格的在线编码考核平台 "Coding Coach"。

## 设计目标
- 主页即为试题页，不再强制登录
- 清新毛玻璃风格，非暗色主题
- 去除 AI 感，偏向教育/考核平台定位
- 点击题目展示侧边栏简介，进入考试前做登录拦截

## 页面结构

### 1. 主页（试题列表）
- **导航栏**（毛玻璃）: 左侧 Logo + "Coding Coach"，右侧根据登录态显示"登录/注册"按钮或用户信息
- **页面标题**: "在线编码考核" + 副标题
- **试题卡片网格**: 毛玻璃卡片，圆角 16px，带 emoji 图标、标题、文件名、分类标签
- **背景**: 柔和渐变（浅蓝 → 浅紫 → 暖白）

### 2. 侧边栏（题目简介）
- 点击题目卡片 → 右侧滑出 380px 宽毛玻璃面板
- 内容: 题目图标 + 标题 + 分类标签、简介描述（从 .md 文件提取第一段描述）、核心考察点标签、可用 API / 关键信息
- 底部: "进入考试" 按钮
- 点击 ✕ 或遮罩区关闭

### 3. 登录/注册弹窗（Modal）
- 毛玻璃白色弹窗，圆角 20px
- 登录: 邮箱 + 密码，底部"去注册"切换
- 注册: 姓名 + 邮箱 + 密码，底部"去登录"切换
- 登录/注册成功后弹窗关闭，导航栏更新为用户信息

### 4. 登录拦截
- 未登录用户点击"进入考试" → 弹出"需要登录"提示弹窗，引导登录

### 5. 考试页面（Exam.vue）
- 保持现有功能逻辑（创建容器、计时器、iframe）
- 样式从暗色改为浅色毛玻璃主题
- 顶部栏: 白色毛玻璃效果，背景 `rgba(255,255,255,0.85)` + `backdrop-filter`，文字颜色改为 `#1e293b`
- 加载状态: spinner 适配新主题色
- iframe 编码环境保持不变

## 色彩体系
| 用途 | 颜色 |
|------|------|
| 页面背景渐变 | `#e8f0fe` → `#f0e8ff` → `#fffbf5` |
| 毛玻璃卡片 | `rgba(255,255,255,0.6)` + `backdrop-filter: blur(12px)` |
| 主色 | `#4a6cf7` |
| 主色渐变 | `linear-gradient(135deg, #4a6cf7, #6a3de8)` |
| 主文本 | `#1e293b` |
| 次要文本 | `#64748b` |
| 边框 | `rgba(255,255,255,0.3)` |

## 组件拆分
```
App.vue               # 主入口，管理登录态和页面切换
├── NavBar.vue        # 顶部导航栏（登录/注册按钮 or 用户信息）
├── ArticleGrid.vue   # 试题卡片网格
├── ArticleCard.vue   # 单张试题卡片
├── ArticleSidebar.vue # 右侧题目简介侧边栏
├── AuthModal.vue     # 登录/注册弹窗
├── AuthGuard.vue     # 未登录拦截弹窗
├── Login.vue         # (保留，改为嵌入 AuthModal)
└── Exam.vue          # 考试页面（样式适配）
```

## 数据流变化
1. 页面加载 → 直接调用 `GET /articles`（无认证要求，需要后端调整）
2. 点击题目 → 显示侧边栏，从预加载的 article 数据展示简介
3. 点击"进入考试" → 检查 `loggedIn` → 未登录则显示 AuthGuard → 已登录则进入 Exam
4. 登录/注册 → 通过 AuthModal 调用 `/auth/login` 或 `/auth/register`

## 后端调整
- `GET /articles` 移除 `Depends(get_current_user)` 认证依赖，允许未登录访问
- `POST /create_env` 保留认证依赖，仅登录用户可创建考试环境

## 需要修改的文件
```
frontend/index.html         # 修改标题为 "Coding Coach"
frontend/src/style.css      # 重写全局样式（浅色毛玻璃主题）
frontend/src/App.vue        # 重构主组件
frontend/src/main.js        # 不变
frontend/src/Login.vue      # 移除，功能合并到 AuthModal.vue
frontend/src/Exam.vue       # 样式适配新主题
frontend/src/ArticleCard.vue    # 新增
frontend/src/ArticleSidebar.vue # 新增
frontend/src/AuthModal.vue      # 新增
frontend/src/NavBar.vue         # 新增
backend/route/article.py    # 移除认证依赖
```
