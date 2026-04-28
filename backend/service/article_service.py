import os

ARTICLES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "articles")

# 文件名到中文题目的映射
NAME_MAP = {
    "deep-face-search.md": "深度人脸搜索",
    "advanced-face-search.md": "高性能短链接",
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


def _default_title(filename: str) -> str:
    """文件名转可读标题"""
    name = filename.replace(".md", "")
    # 驼峰/中划线 → 空格分隔 + 首字母大写
    return name.replace("-", " ").replace("_", " ").title()


def list_articles():
    """列出所有文章"""
    result = []
    if not os.path.exists(ARTICLES_DIR):
        return result

    for fname in sorted(os.listdir(ARTICLES_DIR)):
        if not fname.endswith(".md"):
            continue

        filepath = os.path.join(ARTICLES_DIR, fname)

        # 优先用映射表，其次从 markdown 标题提取，最后用文件名
        title = NAME_MAP.get(fname)
        if not title:
            title = _extract_title_from_md(filepath)
        if not title:
            title = _default_title(fname)

        result.append({
            "filename": fname,
            "title": title,
        })

    return result
