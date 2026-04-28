from fastapi import APIRouter, Depends
from service.article_service import list_articles
from schema.user import User
from route.dependencies import get_current_user

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("")
def get_articles(user: User = Depends(get_current_user)):
    """获取所有文章（题目）列表"""
    return list_articles()
