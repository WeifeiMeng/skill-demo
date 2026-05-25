import docker
import random
import re
import shutil
import toml
import os

# 读取配置文件，workspaces_base 相对于 backend 目录
_config = toml.load(os.path.join(os.path.dirname(__file__), "..", "setting.toml"))
backend_dir = os.path.dirname(os.path.dirname(__file__))
WORKSPACES_BASE = os.path.join(backend_dir, _config["docker"]["workspaces_base"])

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


def create_container(username: str, image: str, article_name: str | None = None):
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

    # 从宿主环境透传 AI 相关环境变量到容器
    ai_env = {
        k: v for k, v in {
            "ANTHROPIC_BASE_URL": os.environ.get("ANTHROPIC_BASE_URL"),
            "ANTHROPIC_API_KEY": os.environ.get("ANTHROPIC_API_KEY"),
            "ANTHROPIC_MODEL": os.environ.get("ANTHROPIC_MODEL"),
        }.items() if v is not None
    }

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

    # 将 ANTHROPIC 环境变量写入容器 ~/.bashrc，方便用户终端使用
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
