import os

ARTICLES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "articles")

# 文件名到中文题目的映射
NAME_MAP = {
    "deep-face-search": "深度人脸搜索",
    "advanced-short-url": "高性能短链接",
}

# 文件名到简介的映射
DESCRIPTION_MAP = {
    "deep-face-search": "给定一张模糊的人脸图片，通过多轮搜索与用户反馈确认，最终定位到具体人员档案。考察函数调用策略、搜索流程设计与 Top1 限制的解决方案。",
    "advanced-short-url": "用 Python 实现一个高性能短链接后端服务，支持长 URL 转短码、302 重定向跳转，以及基于滑动窗口算法的用户级限流。",
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
    # 驼峰/中划线 → 空格分隔 + 首字母大写
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
        readme = os.path.join(dirpath, "readme.md")
        if not os.path.exists(readme):
            continue

        filepath = readme

        # 优先用映射表，其次从 markdown 标题提取，最后用文件名
        title = NAME_MAP.get(fname)
        if not title:
            title = _extract_title_from_md(filepath)
        if not title:
            title = _default_title(fname)

        result.append({
            "filename": fname,
            "title": title,
            "description": DESCRIPTION_MAP.get(fname, ""),
        })

    return result
