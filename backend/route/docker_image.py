from fastapi import APIRouter, Depends
from service.docker_manager import get_images
from schema.user import User
from route.dependencies import get_current_user

router = APIRouter(prefix="/images", tags=["docker"])


@router.get("")
def list_images(user: User = Depends(get_current_user)):
    """获取所有 Docker 镜像"""
    return get_images()
