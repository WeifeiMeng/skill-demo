from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from service.auth_service import decode_token
from schema.user import User
from dao.user_dao import UserDao

security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取当前登录用户"""
    token = credentials.credentials
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = int(payload.get("sub"))
    user = UserDao.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user
