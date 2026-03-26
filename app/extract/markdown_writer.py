"""将清洗后的 HTML 转换为带 YAML frontmatter 的 Markdown"""
from datetime import datetime
import markdownify


def html_to_markdown(clean_html: str) -> str:
    md = markdownify.markdownify(
        clean_html,
        heading_style=markdownify.ATX,
        bullets="-",
        strip=["img"],
    ).strip()
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
