"""清洗正文 HTML：去除非正文区域，保留段落/列表/引用结构"""
from bs4 import BeautifulSoup, Comment

# 要整体删除的标签
_DROP_TAGS = {
    "script", "style", "iframe", "svg", "canvas",
    "form", "input", "button", "select", "textarea",
}

# 要删除的常见非正文 class / id 关键词
_DROP_CLASS_KEYWORDS = [
    "reward",        # 赞赏
    "qr_code",       # 二维码
    "profile",       # 作者信息
    "bottom_bar",    # 底部工具栏
    "related",       # 相关阅读
    "recommend",     # 推荐阅读
    "advertisement", # 广告
    "ad-",
    "footer",
    "copyright",
]


def _has_noise_class(tag) -> bool:
    if not hasattr(tag, "attrs") or tag.attrs is None:
        return False
    classes = tag.get("class", [])
    tag_id = tag.get("id", "")
    combined = " ".join(classes) + " " + tag_id
    return any(kw in combined for kw in _DROP_CLASS_KEYWORDS)


def clean_html(body_html: str) -> str:
    soup = BeautifulSoup(body_html, "html.parser")

    # 删除 HTML 注释
    for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
        comment.extract()

    # 删除噪声标签
    for tag in soup.find_all(_DROP_TAGS):
        tag.decompose()

    # 删除非正文区域（按 class/id 关键词）
    for tag in soup.find_all(True):
        if _has_noise_class(tag):
            tag.decompose()

    return str(soup)
