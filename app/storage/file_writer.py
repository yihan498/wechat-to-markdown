"""将 Markdown 内容写入指定目录"""
import re
import hashlib
from pathlib import Path


_ILLEGAL_CHARS = re.compile(r'[\\/:*?"<>|]')


def _sanitize(name: str) -> str:
    """去除文件名非法字符"""
    return _ILLEGAL_CHARS.sub("_", name).strip()


def build_filename(title: str, publish_date: str) -> str:
    """生成文件名：YYYYMMDD标题.md"""
    safe_title = _sanitize(title)
    if len(safe_title) > 60:
        safe_title = safe_title[:60]
    if publish_date:
        compact_date = publish_date.replace("-", "")
        return f"{compact_date}{safe_title}.md"
    return f"{safe_title}.md"


def write_markdown(save_dir: str, filename: str, content: str) -> str:
    """写入文件；若同名冲突则追加短哈希。返回实际写入路径。"""
    Path(save_dir).mkdir(parents=True, exist_ok=True)
    target = Path(save_dir) / filename

    if target.exists():
        short_hash = hashlib.md5(content.encode()).hexdigest()[:6]
        stem = target.stem
        target = target.with_name(f"{stem}-{short_hash}.md")

    target.write_text(content, encoding="utf-8")
    return str(target)
