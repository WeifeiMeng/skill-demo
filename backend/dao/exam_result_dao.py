from typing import Optional, List
from datetime import datetime
from schema.exam_result import ExamResult
from middleware.database import get_db


class ExamResultDao:
    """考试结果数据访问层"""

    @staticmethod
    def init_table():
        """初始化考试结果表，不存在则创建"""
        sql = """
            CREATE TABLE IF NOT EXISTS exam_results (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                article_name VARCHAR(255) NOT NULL,
                score INT DEFAULT 0,
                max_score INT DEFAULT 100,
                passed BOOLEAN DEFAULT FALSE,
                cases_json TEXT,
                submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                conn.commit()

    @staticmethod
    def create(result: ExamResult) -> int:
        """创建考试结果记录，返回新记录ID"""
        sql = """
            INSERT INTO exam_results (user_id, article_name, score, max_score, passed, cases_json, submitted_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        now = result.submitted_at or datetime.now()
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (
                    result.user_id,
                    result.article_name,
                    result.score,
                    result.max_score,
                    result.passed,
                    result.cases_json,
                    now
                ))
                conn.commit()
                return cursor.lastrowid

    @staticmethod
    def get_by_user(user_id: int) -> List[ExamResult]:
        """获取用户的所有考试结果，按提交时间倒序"""
        sql = """
            SELECT id, user_id, article_name, score, max_score, passed, cases_json, submitted_at
            FROM exam_results
            WHERE user_id = %s
            ORDER BY submitted_at DESC
        """
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (user_id,))
                rows = cursor.fetchall()
                return [
                    ExamResult(
                        id=row[0],
                        user_id=row[1],
                        article_name=row[2],
                        score=row[3],
                        max_score=row[4],
                        passed=row[5],
                        cases_json=row[6],
                        submitted_at=row[7]
                    )
                    for row in rows
                ]

    @staticmethod
    def get_user_article_best(user_id: int, article_name: str) -> Optional[ExamResult]:
        """获取用户在某题目的最佳成绩"""
        sql = """
            SELECT id, user_id, article_name, score, max_score, passed, cases_json, submitted_at
            FROM exam_results
            WHERE user_id = %s AND article_name = %s
            ORDER BY score DESC
            LIMIT 1
        """
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (user_id, article_name))
                row = cursor.fetchone()
                if row:
                    return ExamResult(
                        id=row[0],
                        user_id=row[1],
                        article_name=row[2],
                        score=row[3],
                        max_score=row[4],
                        passed=row[5],
                        cases_json=row[6],
                        submitted_at=row[7]
                    )
                return None

    @staticmethod
    def get_submission_count(user_id: int, article_name: str) -> int:
        """获取用户在某题目的提交次数"""
        sql = """
            SELECT COUNT(*)
            FROM exam_results
            WHERE user_id = %s AND article_name = %s
        """
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (user_id, article_name))
                row = cursor.fetchone()
                return row[0] if row else 0

    @staticmethod
    def get_all_users_stats() -> List[dict]:
        """获取所有用户的考试统计数据"""
        sql = """
            SELECT u.id, u.name, u.email, er.article_name,
                   MAX(er.score) as best_score, er.max_score,
                   MAX(er.passed) as ever_passed, COUNT(*) as submission_count,
                   MAX(er.submitted_at) as last_submitted
            FROM users u
            LEFT JOIN exam_results er ON u.id = er.user_id
            WHERE u.role = 'user'
            GROUP BY u.id, er.article_name
            ORDER BY u.id, er.article_name
        """
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                rows = cursor.fetchall()
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in rows]

    @staticmethod
    def get_overall_stats() -> dict:
        """获取整体统计数据"""
        sql = """
            SELECT
                (SELECT COUNT(*) FROM users WHERE role = 'user') as total_users,
                (SELECT COUNT(*) FROM exam_results) as total_submissions,
                (SELECT COUNT(DISTINCT user_id) FROM exam_results WHERE passed = TRUE) as passed_users
        """
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                row = cursor.fetchone()
                total_users = row[0] or 0
                total_submissions = row[1] or 0
                passed_users = row[2] or 0
                pass_rate = round(passed_users / total_users * 100) if total_users > 0 else 0
                return {
                    "total_users": total_users,
                    "total_submissions": total_submissions,
                    "passed_users": passed_users,
                    "pass_rate": pass_rate
                }


# 模块加载时自动初始化表
try:
    ExamResultDao.init_table()
except Exception:
    pass
