import docker
import random
import re

client = docker.from_env()

def get_next_env_name():
    """获取下一个 env-xxx 格式的容器名称"""
    try:
        all_containers = client.containers.list(all=True)
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

def create_container():
    port = random.randint(20000, 30000)
    env_name = get_next_env_name()

    container = client.containers.run(
        "codesandbox-image-new",
        detach=True,
        ports={"8080/tcp": port},
        tty=True,
        name=env_name
    )

    return {
        "container_id": container.id,
        "port": port
    }

def get_containers():
    """获取所有 Docker 容器信息"""
    result = []
    try:
        all_containers = client.containers.list(all=True)
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

            result.append({
                "container_id": container.id,  # 使用完整 id
                "short_id": container.id[:12],
                "name": container.name,
                "port": port,
                "status": container.status,
                "image": container.image.tags[0] if container.image.tags else container.image.short_id
            })
    except Exception as e:
        print(f"Error getting containers: {e}")
    return result

def stop_container(container_id: str):
    """停止指定容器"""
    try:
        container = client.containers.get(container_id)
        container.stop()
        return {"success": True, "status": "stopped"}
    except docker.errors.NotFound:
        return {"success": False, "error": "Container not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def start_container(container_id: str):
    """启动指定容器"""
    try:
        container = client.containers.get(container_id)
        container.start()
        return {"success": True, "status": "running"}
    except docker.errors.NotFound:
        return {"success": False, "error": "Container not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def remove_container(container_id: str):
    """删除指定容器"""
    try:
        container = client.containers.get(container_id)
        container.remove(force=True)
        return {"success": True, "status": "removed"}
    except docker.errors.NotFound:
        return {"success": False, "error": "Container not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}