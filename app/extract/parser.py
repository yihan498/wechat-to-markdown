"""从公众号文章 URL 获取并解析 HTML"""
import re
import logging
import urllib.request
from datetime import datetime

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# 公众号文章正文容器的 CSS 选择器（按优先级排列）
_CONTENT_SELECTORS = [
    "#js_content",          # 标准公众号文章正文 div
    ".rich_media_content",  # 备选
]

# 标题选择器
_TITLE_SELECTORS = [
    "#activity-name",
    ".rich_media_title",
    "h1.title",
]

# 发布时间选择器
_TIME_SELECTORS = [
    "#publish_time",
    "em#publish_time",
    ".rich_media_meta_primary",
]


def fetch_html(url: str, user_agent: str, timeout: int = 30) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": user_agent})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
    # 尝试从 HTTP 头或 meta 标签获取编码
    charset = resp.headers.get_content_charset() or "utf-8"
    return raw.decode(charset, errors="replace")


def _select_first(soup: BeautifulSoup, selectors: list) -> str:
    for sel in selectors:
        el = soup.select_one(sel)
        if el:
            return el.get_text(strip=True)
    return ""


def _extract_publish_time(soup: BeautifulSoup) -> str:
    """先尝试 HTML 元素，再从脚本变量中提取"""
    text = _select_first(soup, _TIME_SELECTORS)
    if text:
        return text

    # 从内嵌 JS 中找 publish_time 变量
    for script in soup.find_all("script"):
        m = re.search(r'publish_time\s*=\s*"([^"]+)"', script.string or "")
        if m:
            return m.group(1)
        # 有时是时间戳
        m = re.search(r'create_time\s*=\s*"(\d+)"', script.string or "")
        if m:
            ts = int(m.group(1))
            return datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
    return ""


def parse_article(html: str, url: str) -> dict:
    """
    返回:
        title        str
        publish_date str  (YYYY-MM-DD)
        body_html    str  (正文 HTML，待清洗)
        source_url   str
    """
    soup = BeautifulSoup(html, "html.parser")

    title = _select_first(soup, _TITLE_SELECTORS)
    if not title:
        title = soup.title.get_text(strip=True) if soup.title else "未知标题"

    raw_time = _extract_publish_time(soup)
    publish_date = _normalize_date(raw_time)

    body_html = ""
    for sel in _CONTENT_SELECTORS:
        el = soup.select_one(sel)
        if el:
            body_html = str(el)
            break

    if not body_html:
        logger.warning("未找到正文容器，将使用 <body> 全文")
        body_html = str(soup.body) if soup.body else html

    return {
        "title": title,
        "publish_date": publish_date,
        "body_html": body_html,
        "source_url": url,
    }


def _normalize_date(raw: str) -> str:
    """将各种日期格式统一为 YYYY-MM-DD"""
    if not raw:
        return datetime.now().strftime("%Y-%m-%d")
    # 已是标准格式
    m = re.search(r"(\d{4}[-/]\d{1,2}[-/]\d{1,2})", raw)
    if m:
        return m.group(1).replace("/", "-")
    # 中文格式：2026年3月25日
    m = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日", raw)
    if m:
        return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    return datetime.now().strftime("%Y-%m-%d")
