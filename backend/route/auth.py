from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from service.auth_service import verify_password, hash_password, create_token, decode_token
from schema.user import User
from dao.user_dao import UserDao
from route.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

# 请求模型
class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/register")
def register(req: RegisterRequest):
    """用户注册"""
    existing = UserDao.get_by_email(req.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        name=req.name,
        email=req.email,
        password=hash_password(req.password)
    )
    user.id = UserDao.create(user)

    token = create_token(user.id, user.email, user.role or "user")
    return {
        "success": True,
        "token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role or "user",
            "avatar": user.avatar
        }
    }


@router.post("/login")
def login(req: LoginRequest):
    """用户登录"""
    user = UserDao.get_by_email(req.email)
    if not user or not verify_password(req.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_token(user.id, user.email, user.role or "user")
    return {
        "success": True,
        "token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role or "user",
            "avatar": user.avatar
        }
    }


@router.get("/me")
def get_me(user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role or "user",
        "avatar": user.avatar
    }
