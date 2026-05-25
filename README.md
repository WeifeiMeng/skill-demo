# Mini CodeSandbox

一个用于管理 Docker 开发环境的 Web 界面。

## 技术栈

- **前端**：Vue 3 + Vite
- **后端**：FastAPI + Docker Python SDK
- **容器**：codesandbox-image

## 启动命令

### 前端
```bash
cd frontend
npm install
npm run dev
```

### 后端
```bash
cd backend
uv sync
uvicorn main:app --port 8000
```

## 使用方法

1. 启动前端服务（端口 3000）
2. 启动后端服务（端口 8000）
3. 打开浏览器访问 http://localhost:3000
4. 点击 **Create Dev Environment** 创建新的开发环境容器，新标签页会自动打开
5. 在左侧边栏可以看到所有 Docker 容器列表，点击任意容器可直接在新标签页打开

## API

| 端点 | 方法 | 描述 |
|------|------|------|
| `/create_env` | POST | 创建新容器，返回 `{container_id, port}` |
| `/containers` | GET | 获取所有容器列表 |


export ANTHROPIC_BASE_URL="https://你的提供商地址/v1"


# 设置代理地址和 API Key
export ANTHROPIC_BASE_URL="https://api.deepseek.com/anthropic" curl http://host.docker.internal:8002
export ANTHROPIC_API_KEY="sk-600ec4e4855c4fd5a3cbf76ac26dd1ef"
export ANTHROPIC_MODEL="deepseek-v4-flash"

# 设置代理地址和 API Key
export ANTHROPIC_BASE_URL="http://host.docker.internal:8002/api/v1/proxy/anthropic"  
export ANTHROPIC_API_KEY="sk-ed8e5934118b45fa8c3b1257e395d1dd"
export ANTHROPIC_MODEL="deepseek-v4-flash"


postman request POST 'http://host.docker.internal:8002/api/v1/proxy' \
  --header 'Authorization: Bearer sk-ed8e5934118b45fa8c3b1257e395d1dd' \
  --header 'Content-Type: application/json' \
  --body '{
    "model": "deepseek-v4-flash",
    "messages": [
        {
            "role": "user",
            "content": "你好"
        }
    ]
}'

curl --location 'http://host.docker.internal:8002/api/v1/proxy' \
--header 'Authorization: Bearer sk-ed8e5934118b45fa8c3b1257e395d1dd' \
--header 'Content-Type: application/json' \
--data '{
    "model": "deepseek-v4-flash",
    "messages": [
        {
            "role": "user",
            "content": "你好"
        }
    ]
}'