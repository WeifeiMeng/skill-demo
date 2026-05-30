from typing import Optional
from datetime import datetime
from schema.exam_session import ExamSession
from middleware.database import get_db


class ExamSessionDao:
    """考试会话数据访问层"""

    @staticmethod
    def init_table():
        """初始化考试会话表，不存在则创建"""
        sql = """
            CREATE TABLE IF NOT EXISTS exam_sessions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                article_name VARCHAR(255) NOT NULL,
                container_id VARCHAR(255),
                started_at DATETIME NOT NULL,
                ended_at DATETIME,
                status VARCHAR(20) DEFAULT 'active',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY uk_user_article (user_id, article_name)
            )
        """
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                conn.commit()

    @staticmethod
    def get_active(user_id: int, article_name: str) -> Optional[ExamSession]:
        """获取用户某个题目的活跃会话"""
        sql = """
            SELECT id, user_id, article_name, container_id,
                   started_at, ended_at, status, created_at, updated_at
            FROM exam_sessions
            WHERE user_id = %s AND article_name = %s AND status = 'active'
            LIMIT 1
        """
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (user_id, article_name))
                row = cursor.fetchone()
                if row:
                    return ExamSession(
                        id=row[0],
                        user_id=row[1],
                        article_name=row[2],
                        container_id=row[3],
                        started_at=row[4],
                        ended_at=row[5],
                        status=row[6],
                        created_at=row[7],
                        updated_at=row[8]
                    )
                return None

    @staticmethod
    def create(user_id: int, article_name: str, container_id: str) -> ExamSession:
        """创建新的考试会话（如已有历史记录则重置为活跃）"""
        now = datetime.now()
        sql = """
            INSERT INTO exam_sessions (user_id, article_name, container_id, started_at, status)
            VALUES (%s, %s, %s, %s, 'active')
            ON DUPLICATE KEY UPDATE
                container_id = VALUES(container_id),
                started_at = VALUES(started_at),
                status = 'active',
                ended_at = NULL
        """
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (user_id, article_name, container_id, now))
                conn.commit()
                return ExamSession(
                    id=cursor.lastrowid,
                    user_id=user_id,
                    article_name=article_name,
                    container_id=container_id,
                    started_at=now,
                    status="active"
                )

    @staticmethod
    def start_or_get(user_id: int, article_name: str, container_id: str) -> ExamSession:
        """获取已有活跃会话，没有则创建新会话"""
        existing = ExamSessionDao.get_active(user_id, article_name)
        if existing:
            # 更新 container_id
            if existing.container_id != container_id:
                sql = "UPDATE exam_sessions SET container_id = %s WHERE id = %s"
                with get_db() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(sql, (container_id, existing.id))
                        conn.commit()
                existing.container_id = container_id
            return existing
        # ON DUPLICATE KEY UPDATE 自动处理历史 finished 记录
        return ExamSessionDao.create(user_id, article_name, container_id)

    @staticmethod
    def delete_all_by_user(user_id: int, article_name: str) -> bool:
        """删除用户的考试会话记录"""
        sql = "DELETE FROM exam_sessions WHERE user_id = %s AND article_name = %s"
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (user_id, article_name))
                conn.commit()
                return cursor.rowcount > 0

    @staticmethod
    def finish(user_id: int, article_name: str) -> bool:
        """结束考试会话"""
        sql = "UPDATE exam_sessions SET status = 'finished', ended_at = %s WHERE user_id = %s AND article_name = %s AND status = 'active'"
        now = datetime.now()
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (now, user_id, article_name))
                conn.commit()
                return cursor.rowcount > 0


# 模块加载时自动初始化表
try:
    ExamSessionDao.init_table()
except Exception:
    pass
