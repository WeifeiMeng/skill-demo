import docker
import random
import re
import shutil
import sys
import toml
import os
import urllib.request
import json as json_mod

# 读取配置文件，workspaces_base 相对于 backend 目录
_config = toml.load(os.path.join(os.path.dirname(__file__), "..", "setting.toml"))
backend_dir = os.path.dirname(os.path.dirname(__file__))
WORKSPACES_BASE = os.path.join(backend_dir, _config["docker"]["workspaces_base"])
LLM_PIPE_BASE_URL = _config["llm_pipe"]["base_url"]
LLM_PIPE_MODEL = _config["llm_pipe"]["model"]

def _get_client():
    """延迟初始化 Docker 客户端"""
    return docker.from_env()

def get_next_env_name():
    """获取下一个 env-xxx 格式的容器名称"""
    try:
        all_containers = _get_client().containers.list(all=True)
        max_num = 0
        for container in all_containers:
            match = re.match(r'env-(\d+)', container.name)
            if match:
                num = int(match.group(1))
                if num > max_num:
                    max_num = num
        return f"env-{max_num + 1:03d}"
    except Exception:
        return "env-001"

def find_container_by_article(username: str, article_name: str):
    """查找用户是否已有该题目的容器"""
    try:
        client = _get_client()
        filters = {"label": [f"user={username}", f"article={article_name}"]}
        containers = client.containers.list(all=True, filters=filters)
        if containers:
            c = containers[0]
            # 提取端口
            port = None
            ports = c.ports
            if ports and "8080/tcp" in ports and len(ports["8080/tcp"]) > 0:
                port = ports["8080/tcp"][0].get("HostPort")
            if port is None:
                try:
                    attrs = c.attrs
                    ports_config = attrs.get('HostConfig', {}).get('PortBindings', {})
                    if '8080/tcp' in ports_config:
                        port = ports_config['8080/tcp'][0]['HostPort']
                except Exception:
                    pass
            return {
                "container_id": c.id,
                "port": port,
                "status": c.status
            }
    except Exception as e:
        print(f"Error finding container: {e}")
    return None


def create_container(username: str, image: str, user_id: int, article_name: str | None = None):
    port = random.randint(20000, 30000)
    env_name = get_next_env_name()

    # 工作目录: workspaces/username/article_name
    article_slug = article_name or env_name
    workspace_dir = os.path.join(WORKSPACES_BASE, username, article_slug)
    os.makedirs(workspace_dir, exist_ok=True)

    # 复制对应的 markdown 题目到工作目录
    if article_name:
        articles_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "articles")
        article_dir = os.path.join(articles_dir, article_name)
        if os.path.isdir(article_dir):
            shutil.copytree(article_dir, workspace_dir, dirs_exist_ok=True)

    labels = {}
    if article_name:
        labels["user"] = username
        labels["article"] = article_name

    # 从 llm-pipe 获取用户的 API key
    api_key = None
    try:
        url = f"{LLM_PIPE_BASE_URL}/api/v1/users/{user_id}/api-key"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json_mod.loads(resp.read().decode("utf-8"))
            api_key = data.get("api_key")
    except Exception as e:
        print(f"Warning: failed to fetch API key from llm-pipe: {e}")

    # 构建 Claude 环境变量（api_key 动态获取，其余从配置读取）
    # 容器内 localhost 指向容器自己，需替换为 host.docker.internal 访问宿主机服务
    base_url_for_container = LLM_PIPE_BASE_URL.replace("localhost", "host.docker.internal")
    ai_env = {}
    if api_key:
        ai_env["ANTHROPIC_API_KEY"] = api_key
        ai_env["ANTHROPIC_BASE_URL"] = f"{base_url_for_container}/api/v1/proxy/anthropic"
        ai_env["ANTHROPIC_MODEL"] = LLM_PIPE_MODEL

    container = _get_client().containers.run(
        image,
        detach=True,
        ports={"8080/tcp": port},
        tty=True,
        name=env_name,
        volumes={workspace_dir: {"bind": "/workspace", "mode": "rw"}},
        working_dir="/workspace",
        labels=labels,
        environment=ai_env,
        extra_hosts={"host.docker.internal": "host-gateway"}
    )

    # 将 Claude 环境变量写入容器 ~/.bashrc，方便用户终端使用
    if ai_env:
        lines = "".join(f'export {k}="{v}"\n' for k, v in ai_env.items())
        cmd = ["bash", "-c", f"cat >> ~/.bashrc <<'ENVEOF'\n{lines}ENVEOF"]
        try:
            container.exec_run(cmd, user="root")
        except Exception as e:
            print(f"Warning: failed to write env to .bashrc: {e}")

    return {
        "container_id": container.id,
        "port": port,
        "workspace": workspace_dir
    }

def get_containers():
    """获取所有 Docker 容器信息"""
    result = []
    try:
        all_containers = _get_client().containers.list(all=True)
        for container in all_containers:
            # 优先从 ports 获取端口，如果为空则从容器配置中获取
            port = None
            ports = container.ports
            if ports and "8080/tcp" in ports and len(ports["8080/tcp"]) > 0:
                port = ports["8080/tcp"][0].get("HostPort")

            # 如果 ports 为空，尝试从容器配置中获取
            if port is None:
                try:
                    attrs = container.attrs
                    ports_config = attrs.get('HostConfig', {}).get('PortBindings', {})
                    if '8080/tcp' in ports_config:
                        port = ports_config['8080/tcp'][0]['HostPort']
                except Exception:
                    pass

            # 获取 workspace 挂载路径
            workspace = None
            try:
                attrs = container.attrs
                mounts = attrs.get('Mounts', [])
                for mount in mounts:
                    if mount.get('Destination') == '/workspace':
                        workspace = mount.get('Source')
                        break
            except Exception:
                pass

            result.append({
                "container_id": container.id,  # 使用完整 id
                "short_id": container.id[:12],
                "name": container.name,
                "port": port,
                "status": container.status,
                "image": container.image.tags[0] if container.image.tags else container.image.short_id,
                "workspace": workspace
            })
    except Exception as e:
        print(f"Error getting containers: {e}")
    return result

def stop_container(container_id: str):
    """停止指定容器"""
    try:
        container = _get_client().containers.get(container_id)
        container.stop()
        return {"success": True, "status": "stopped"}
    except docker.errors.NotFound:
        return {"success": False, "error": "Container not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def start_container(container_id: str):
    """启动指定容器"""
    try:
        container = _get_client().containers.get(container_id)
        container.start()
        return {"success": True, "status": "running"}
    except docker.errors.NotFound:
        return {"success": False, "error": "Container not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def remove_container(container_id: str):
    """删除指定容器"""
    try:
        container = _get_client().containers.get(container_id)
        container.remove(force=True)
        return {"success": True, "status": "removed"}
    except docker.errors.NotFound:
        return {"success": False, "error": "Container not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_images():
    """获取所有 Docker 镜像"""
    result = []
    try:
        images = _get_client().images.list()
        for img in images:
            result.append({
                "id": img.id,
                "short_id": img.short_id,
                "tags": img.tags if img.tags else [],
                "size": img.attrs.get('Size', 0),
                "created": img.attrs.get('Created', '')
            })
    except Exception as e:
        print(f"Error getting images: {e}")
    return result


def exec_test(container_id: str, article_name: str):
    """在容器中执行测试脚本，返回 JSON 结果"""
    import base64
    import json as json_mod

    tests_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tests")
    test_file = os.path.join(tests_dir, article_name, "test.py")

    if not os.path.exists(test_file):
        return {"error": f"Test not found for article: {article_name}"}

    try:
        with open(test_file, "r", encoding="utf-8") as f:
            test_code = f.read()
    except Exception as e:
        return {"error": f"Failed to read test file: {e}"}

    try:
        container = _get_client().containers.get(container_id)

        # 自动安装依赖
        install_cmd = "if [ -f /workspace/requirements.txt ]; then pip3 install --break-system-packages --root-user-action=ignore -r /workspace/requirements.txt -q 2>&1; else echo 'no requirements.txt'; fi"
        install_result = container.exec_run(["bash", "-c", install_cmd], user="root")
        print(f"[exec_test] pip install: {install_result.output.decode('utf-8', errors='replace')[:500]}", file=sys.stderr)

        # Base64 编码后通过 exec_run 注入容器执行
        b64 = base64.b64encode(test_code.encode("utf-8")).decode("ascii")
        cmd = f'python3 -c "import base64; exec(base64.b64decode(\'{b64}\'))"'
        result = container.exec_run(cmd, user="root")
    except docker.errors.NotFound:
        return {"error": "Container not found"}
    except Exception as e:
        return {"error": f"Exec failed: {e}"}

    output = result.output.decode("utf-8", errors="replace") if isinstance(result.output, bytes) else str(result.output)

    # 从 stdout 中提取最后一段 JSON
    try:
        # 找到最后一个完整 JSON 对象
        lines = output.strip().split("\n")
        for line in reversed(lines):
            line = line.strip()
            if line.startswith("{") and line.endswith("}"):
                return json_mod.loads(line)
        return {"error": "No JSON result found in test output", "raw": output[-1000:]}
    except json_mod.JSONDecodeError as e:
        return {"error": f"JSON parse error: {e}", "raw": output[-1000:]}
