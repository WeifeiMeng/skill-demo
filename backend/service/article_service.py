import os

ARTICLES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "articles")

# 文件名到中文题目的映射（手动覆盖 markdown 标题）
NAME_MAP = {
    "deep-face-search": "深度人脸搜索",
    "advanced-short-url": "高性能短链接",
    "vibe-coding-challenge": "Vibe Coding: 新品冷启动流量配额系统",
    "logistics-delivery": "同城末端配送路径规划",
}


def _extract_title_from_md(filepath: str) -> str | None:
    """从 markdown 的第一个 # 一级标题提取中文名"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("# "):
                    return line[2:].strip()
    except Exception:
        pass
    return None


def _read_readme(filepath: str) -> str:
    """读取 readme.md 全部内容"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


def _default_title(filename: str) -> str:
    """文件名转可读标题"""
    return filename.replace("-", " ").replace("_", " ").title()


def list_articles():
    """列出所有文章（每个文件夹是一个题目，内含 readme.md）"""
    result = []
    if not os.path.exists(ARTICLES_DIR):
        return result

    for fname in sorted(os.listdir(ARTICLES_DIR)):
        dirpath = os.path.join(ARTICLES_DIR, fname)
        if not os.path.isdir(dirpath):
            continue
        readme_file = os.path.join(dirpath, "readme.md")
        if not os.path.exists(readme_file):
            continue

        # 优先用映射表，其次从 markdown 标题提取，最后用文件名
        title = NAME_MAP.get(fname)
        if not title:
            title = _extract_title_from_md(readme_file)
        if not title:
            title = _default_title(fname)

        result.append({
            "filename": fname,
            "title": title,
            "description": _read_readme(readme_file),
        })

    return result
