import pymysql
import toml
from contextlib import contextmanager
import os

# 读取配置文件
_config = toml.load(os.path.join(os.path.dirname(os.path.dirname(__file__)), "setting.toml"))
DB_CONFIG = _config["database"]

@contextmanager
def get_db():
    """获取数据库连接的上下文管理器"""
    conn = pymysql.connect(**DB_CONFIG)
    try:
        yield conn
    finally:
        conn.close()
