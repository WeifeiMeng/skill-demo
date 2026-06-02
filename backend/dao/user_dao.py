from typing import Optional, List
from datetime import datetime
from schema.user import User
from middleware.database import get_db


class UserDao:
    """用户数据访问层"""

    @staticmethod
    def init_table():
        """初始化用户表，不存在则创建"""
        sql = """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(20) DEFAULT 'user',
                avatar VARCHAR(500),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                conn.commit()

        # Migration: add role column for existing databases
        try:
            with get_db() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user' AFTER password")
                    conn.commit()
        except Exception:
            pass

    @staticmethod
    def create(user: User) -> int:
        """创建用户，返回新用户ID"""
        sql = """
            INSERT INTO users (name, email, password, role, avatar, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        now = datetime.now()
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (
                    user.name,
                    user.email,
                    user.password,
                    user.role,
                    user.avatar,
                    now,
                    now
                ))
                conn.commit()
                return cursor.lastrowid

    @staticmethod
    def get_by_id(user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        sql = "SELECT id, name, email, password, role, avatar, created_at, updated_at FROM users WHERE id = %s"
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (user_id,))
                row = cursor.fetchone()
                if row:
                    return User(
                        id=row[0],
                        name=row[1],
                        email=row[2],
                        password=row[3],
                        role=row[4],
                        avatar=row[5],
                        created_at=row[6],
                        updated_at=row[7]
                    )
                return None

    @staticmethod
    def get_by_email(email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        sql = "SELECT id, name, email, password, role, avatar, created_at, updated_at FROM users WHERE email = %s"
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (email,))
                row = cursor.fetchone()
                if row:
                    return User(
                        id=row[0],
                        name=row[1],
                        email=row[2],
                        password=row[3],
                        role=row[4],
                        avatar=row[5],
                        created_at=row[6],
                        updated_at=row[7]
                    )
                return None

    @staticmethod
    def get_all() -> List[User]:
        """获取所有用户"""
        sql = "SELECT id, name, email, password, role, avatar, created_at, updated_at FROM users"
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                rows = cursor.fetchall()
                return [
                    User(
                        id=row[0],
                        name=row[1],
                        email=row[2],
                        password=row[3],
                        role=row[4],
                        avatar=row[5],
                        created_at=row[6],
                        updated_at=row[7]
                    )
                    for row in rows
                ]

    @staticmethod
    def update(user: User) -> bool:
        """更新用户信息"""
        sql = """
            UPDATE users
            SET name = %s, email = %s, password = %s, role = %s, avatar = %s, updated_at = %s
            WHERE id = %s
        """
        now = datetime.now()
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (
                    user.name,
                    user.email,
                    user.password,
                    user.role,
                    user.avatar,
                    now,
                    user.id
                ))
                conn.commit()
                return cursor.rowcount > 0

    @staticmethod
    def delete(user_id: int) -> bool:
        """删除用户"""
        sql = "DELETE FROM users WHERE id = %s"
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (user_id,))
                conn.commit()
                return cursor.rowcount > 0

    @staticmethod
    def update_avatar(user_id: int, avatar: str) -> bool:
        """更新用户头像"""
        sql = "UPDATE users SET avatar = %s, updated_at = %s WHERE id = %s"
        now = datetime.now()
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (avatar, now, user_id))
                conn.commit()
                return cursor.rowcount > 0

    @staticmethod
    def update_password(user_id: int, password: str) -> bool:
        """更新用户密码"""
        sql = "UPDATE users SET password = %s, updated_at = %s WHERE id = %s"
        now = datetime.now()
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (password, now, user_id))
                conn.commit()
                return cursor.rowcount > 0


# 模块加载时自动初始化表
try:
    UserDao.init_table()
except Exception:
    pass
