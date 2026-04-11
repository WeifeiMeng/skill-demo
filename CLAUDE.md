# Claude Code 项目笔记

## 项目概述
Mini CodeSandbox - Docker 开发环境管理界面

## 技术栈
- 前端：Vue 3 + Vite
- 后端：FastAPI + Docker Python SDK
- 容器镜像：codesandbox-image

## 项目结构
```
frontend/
  index.html
  package.json
  vite.config.js
  src/
    main.js       # Vue 入口
    App.vue       # 主组件
    style.css     # 全局样式
backend/
  main.py        # FastAPI 应用，CORS 已配置
  docker_manager.py  # Docker 操作封装
  pyproject.toml    # Python 依赖
  uv.lock           # 锁定依赖版本
```

## 关键文件

### backend/main.py
- `POST /create_env` - 创建新 Docker 容器
- `GET /containers` - 获取所有容器列表
- CORS 配置允许 http://localhost:3000

### backend/docker_manager.py
- `create_container()` - 随机端口(20000-30000)启动 codesandbox-image
- `get_containers()` - 返回所有 Docker 容器（name, port, status, image）

### frontend/src/App.vue
- Vue 3 Composition API (script setup)
- 点击容器用 `window.open()` 新标签打开
- 5秒自动刷新容器列表

## 端口
- 后端：8000
- 前端：3000
- 容器：20000-30000 随机

## 启动命令
- 前端：`cd frontend && npm install && npm run dev`
- 后端：`cd backend && uvicorn main:app --reload --port 8000`
