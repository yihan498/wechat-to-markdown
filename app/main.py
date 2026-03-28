"""
公众号文章抓取工具
用法：
    # 剪贴板模式（推荐）：先在微信复制文章链接，然后双击桌面快捷方式
    # 若 config.yaml 中配置了多个目录，会弹窗让你选择保存位置
    python app/main.py

    # 指定 URL
    python app/main.py --url "https://mp.weixin.qq.com/s/xxxx"

    # 指定账号（对应 config.yaml 中的 accounts[].name），跳过弹窗直接保存
    python app/main.py --account "公众号A"

    # 临时指定保存目录（优先级最高，跳过弹窗）
    python app/main.py --save-dir "C:/我的笔记/公众号"

    # 同时指定 URL 和账号
    python app/main.py --url "https://mp.weixin.qq.com/s/xxxx" --account "公众号A"
"""
import argparse
import logging
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import load_config, get_account, list_accounts
from app.extract.parser import fetch_html, parse_article
from app.extract.cleaner import clean_html
from app.extract.markdown_writer import html_to_markdown, build_markdown
from app.storage.db import init_db, compute_hash, is_duplicate, save_article, log_run
from app.storage.file_writer import build_filename, write_markdown


def setup_logging(cfg: dict):
    log_dir = cfg["logging"]["log_dir"]
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    level = getattr(logging, cfg["logging"]["level"].upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(
                Path(log_dir) / "app.log", encoding="utf-8"
            ),
        ],
    )


def notify_toast(title: str, message: str, success: bool = True):
    """PowerShell Toast 通知（Windows 10+，无阻塞，不需要第三方库）"""
    try:
        import subprocess, textwrap
        # 转义单引号，防止 PS 脚本出错
        t = title.replace("'", "`'")
        m = message.replace("'", "`'").replace("\n", " ")
        ps_script = textwrap.dedent(f"""
            [Windows.UI.Notifications.ToastNotificationManager,
             Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            $xml = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent(
                [Windows.UI.Notifications.ToastTemplateType]::ToastText02)
            $xml.GetElementsByTagName('text')[0].AppendChild(
                $xml.CreateTextNode('{t}')) | Out-Null
            $xml.GetElementsByTagName('text')[1].AppendChild(
                $xml.CreateTextNode('{m}')) | Out-Null
            $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
            [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier(
                'wechat_to_markdown').Show($toast)
        """)
        subprocess.run(
            ["powershell", "-WindowStyle", "Hidden", "-Command", ps_script],
            capture_output=True, timeout=5,
        )
    except Exception:
        pass  # 通知失败不影响主流程


def get_url_from_clipboard() -> str:
    try:
        import pyperclip
        text = pyperclip.paste().strip()
        if text.startswith("http"):
            return text
    except Exception:
        pass
    return ""


def choose_account_dialog(accounts: list) -> dict | None:
    """
    用 PowerShell Out-GridView 弹出目录选择框。
    accounts: [{"name": ..., "save_dir": ...}, ...]
    返回用户选中的 account dict，取消则返回 None。
    """
    # 构造显示列表：每行 "名称  →  路径"
    items = [f"{a['name']}  →  {a['save_dir']}" for a in accounts]
    items_ps = "\n".join(f"    '{line}'" for line in items)

    ps_script = f"""
$items = @(
{items_ps}
)
$selected = $items | Out-GridView -Title '选择保存到哪个目录' -OutputMode Single
Write-Output $selected
"""
    try:
        result = subprocess.run(
            ["powershell", "-WindowStyle", "Hidden", "-Command", ps_script],
            capture_output=True, text=True, encoding="utf-8", timeout=60,
        )
        chosen = result.stdout.strip()
        if not chosen:
            return None  # 用户点了取消
        # 反查对应 account
        for a in accounts:
            label = f"{a['name']}  →  {a['save_dir']}"
            if label == chosen:
                return a
    except Exception:
        pass
    return None


def run(url: str = None, account_name: str = None, save_dir_override: str = None):
    cfg = load_config()
    setup_logging(cfg)
    logger = logging.getLogger("main")

    db_path = cfg["database"]["path"]
    init_db(db_path)

    # --save-dir 优先级最高，直接用，无需弹窗
    if save_dir_override:
        source_name = "手动指定"
        save_dir = save_dir_override
        logger.info(f"使用指定目录: {save_dir}")
    elif account_name:
        # 明确指定了账号，直接查找，无需弹窗
        try:
            account = get_account(cfg, account_name)
        except ValueError as e:
            logger.error(str(e))
            notify_toast("配置错误", str(e), success=False)
            return
        source_name = account["name"]
        save_dir = account["save_dir"]
        logger.info(f"账号: {source_name} -> {save_dir}")
    else:
        # 自动模式：单账号直接用，多账号弹窗选择
        accounts = list_accounts(cfg)
        if len(accounts) == 1:
            account = accounts[0]
        else:
            account = choose_account_dialog(accounts)
            if account is None:
                msg = "已取消，未选择保存目录"
                logger.info(msg)
                return
        source_name = account["name"]
        save_dir = account["save_dir"]
        logger.info(f"账号: {source_name} -> {save_dir}")

    # 未指定 URL 时自动读剪贴板
    if not url:
        url = get_url_from_clipboard()
        if not url:
            msg = "剪贴板中没有找到有效链接，请先在微信中复制文章链接"
            logger.error(msg)
            notify_toast("抓取失败", msg, success=False)
            log_run(db_path, "error", msg)
            return
        logger.info(f"从剪贴板读取链接: {url}")

    # 简单校验是否公众号链接
    if "mp.weixin.qq.com" not in url:
        msg = f"不是公众号链接，已跳过: {url}"
        logger.warning(msg)
        notify_toast("链接无效", msg, success=False)
        return

    logger.info(f"开始抓取: {url}")

    # 1. 获取 HTML
    try:
        html = fetch_html(
            url,
            user_agent=cfg["fetch"]["user_agent"],
            timeout=cfg["fetch"]["timeout"],
        )
    except Exception as e:
        msg = f"网络请求失败: {e}"
        logger.error(msg)
        notify_toast("抓取失败", msg, success=False)
        log_run(db_path, "error", msg)
        return

    # 2. 解析文章
    try:
        article = parse_article(html, url)
    except Exception as e:
        msg = f"文章解析失败: {e}"
        logger.error(msg)
        notify_toast("抓取失败", msg, success=False)
        log_run(db_path, "error", msg)
        return

    logger.info(f"标题: {article['title']}")
    logger.info(f"发布时间: {article['publish_date']}")

    # 3. 清洗正文
    cleaned = clean_html(article["body_html"])

    # 4. 转换 Markdown
    body_md = html_to_markdown(cleaned)
    full_md = build_markdown(
        title=article["title"],
        source=source_name,
        publish_date=article["publish_date"],
        source_url=article["source_url"],
        body_markdown=body_md,
    )

    # 5. 去重
    content_hash = compute_hash(body_md)
    if is_duplicate(db_path, content_hash):
        msg = f"已存在，跳过: {article['title']}"
        logger.info(msg)
        notify_toast("已跳过", msg, success=True)
        log_run(db_path, "skipped", msg)
        return

    # 6. 写入文件
    filename = build_filename(
        article["title"],
        article["publish_date"],
    )

    try:
        saved_path = write_markdown(save_dir, filename, full_md)
    except Exception as e:
        msg = f"写入文件失败: {e}"
        logger.error(msg)
        notify_toast("保存失败", msg, success=False)
        log_run(db_path, "error", msg)
        return

    # 7. 记录状态
    article_id = save_article(
        db_path,
        title=article["title"],
        publish_date=article["publish_date"],
        source_url=url,
        content_hash=content_hash,
        saved_path=saved_path,
    )
    log_run(db_path, "success", f"已保存: {saved_path}", article_id)
    logger.info(f"成功保存到: {saved_path}")

    notify_toast(
        "保存成功 ✓",
        f"{article['title']}\n→ {Path(saved_path).name}",
        success=True,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="公众号文章抓取工具")
    parser.add_argument("--url", default=None, help="文章链接（不填则自动读剪贴板）")
    parser.add_argument("--account", default=None, help="账号名称，对应 config.yaml 中的 accounts[].name（不填则使用 default）")
    parser.add_argument("--save-dir", default=None, dest="save_dir",
                        help="临时指定保存目录，优先级高于 config.yaml（例：D:/我的笔记/公众号）")
    args = parser.parse_args()
    run(args.url, args.account, args.save_dir)
