from fastapi import APIRouter
from service.article_service import list_articles

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("")
def get_articles():
    """获取所有文章（题目）列表，无需登录"""
    return list_articles()


# 兼容前端 /challenges 路径
challenges_router = APIRouter(prefix="/challenges", tags=["challenges"])

@challenges_router.get("")
def get_challenges():
    """获取所有挑战列表（前端兼容），无需登录"""
    return list_articles()
