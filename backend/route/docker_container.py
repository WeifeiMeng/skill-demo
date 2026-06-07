import toml
import os
from fastapi import APIRouter, Request, Depends
from service.docker_manager import create_container, find_container_by_article, get_containers, stop_container, remove_container, start_container
from schema.user import User
from route.dependencies import get_current_user

# 读取配置中的默认镜像名
_config = toml.load(os.path.join(os.path.dirname(os.path.dirname(__file__)), "setting.toml"))
DEFAULT_IMAGE = _config["docker"].get("default_image", "codesandbox-image-new")

router = APIRouter(tags=["docker"])


@router.post("/create_env")
async def create_env(request: Request, user: User = Depends(get_current_user)):
    """创建开发环境（同一题目复用已有容器）"""
    body = await request.json()
    image = body.get("image", DEFAULT_IMAGE)
    article = body.get("article")

    # 查找是否已有该题目的容器
    if article:
        existing = find_container_by_article(user.name, article)
        if existing:
            # 如果容器已停止，尝试启动
            if existing["status"] != "running":
                start_container(existing["container_id"])
            return existing

    # 没有则新建
    result = create_container(user.name, image, user.id, article_name=article)
    return result


@router.get("/containers")
async def list_containers(user: User = Depends(get_current_user)):
    """获取所有容器"""
    return get_containers()


@router.post("/containers/{container_id}/stop")
async def stop_container_api(container_id: str, user: User = Depends(get_current_user)):
    """停止容器"""
    return stop_container(container_id)


@router.post("/containers/{container_id}/start")
async def start_container_api(container_id: str, user: User = Depends(get_current_user)):
    """启动容器"""
    return start_container(container_id)


@router.post("/containers/{container_id}/remove")
async def remove_container_api(container_id: str, user: User = Depends(get_current_user)):
    """删除容器"""
    return remove_container(container_id)
