"""将清洗后的 HTML 转换为带 YAML frontmatter 的 Markdown"""
from datetime import datetime
import markdownify


_END_MARKER = "（完）"


def html_to_markdown(clean_html: str) -> str:
    md = markdownify.markdownify(
        clean_html,
        heading_style=markdownify.ATX,
        bullets="-",
        strip=["img"],          # Phase 1 不保留图片
    ).strip()
    # 截断广告/推广区：保留正文到"（完）"为止
    idx = md.find(_END_MARKER)
    if idx != -1:
        md = md[: idx + len(_END_MARKER)].strip()
    return md


def build_markdown(title: str, source: str, publish_date: str,
                   source_url: str, body_markdown: str) -> str:
    fetched_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    frontmatter = f"""---
title: "{title}"
source: "{source}"
publish_time: {publish_date}
fetched_at: {fetched_at}
source_url: "{source_url}"
---

"""
    return frontmatter + body_markdown
