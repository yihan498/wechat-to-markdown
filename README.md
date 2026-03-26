# wechat-to-markdown

从微信公众号文章链接自动提取正文，保存为 Markdown 文件到任意指定文件夹。

**核心使用流程：**
1. 在微信中打开文章，右上角 `...` → 复制链接
2. 双击 `抓取公众号文章.bat`
3. 文件自动保存到配置的目录，右下角弹出通知

---

## 功能

- 自动读取剪贴板中的公众号链接，无需手动输入
- 提取标题、发布时间、正文文字，过滤广告和推广内容
- 输出带 YAML frontmatter 的 Markdown 文件
- SQLite 去重，同一篇文章不会重复保存
- 支持多个公众号，每个对应不同的保存目录
- 操作日志记录，失败原因可追溯

## 输出格式

文件名：`YYYYMMDD文章标题.md`

```markdown
---
title: "文章标题"
source: "公众号名称"
publish_time: 2026-03-24
fetched_at: 2026-03-25 08:30:00
source_url: "https://mp.weixin.qq.com/s/..."
---

正文内容……
```

---

## 安装

**要求：** Windows + Python 3.9+

```bash
# 1. 克隆项目
git clone https://github.com/yihan498/wechat-to-markdown.git
cd wechat-to-markdown

# 2. 安装依赖
pip install -r requirements.txt
```

---

## 配置保存位置

**方式一：修改 `config/config.yaml`（永久生效）**

```yaml
accounts:
  - name: "公众号A"
    save_dir: "D:/我的笔记/公众号"   # ← 改成你想要的文件夹，不存在会自动创建
    default: true
```

第一次使用时复制示例配置：

```bash
copy config\config.example.yaml config\config.yaml
```

然后用文本编辑器打开 `config/config.yaml`，把 `save_dir` 改成你想要的任意文件夹路径即可。

**方式二：命令行临时指定（单次生效，不修改配置文件）**

```bash
python app/main.py --save-dir "D:/临时目录/公众号"
```

---

## 桌面快捷方式（含图标）

双击 `创建桌面快捷方式.bat`，会自动在桌面生成带绿色图标的快捷方式。

之后每次使用：复制文章链接 → 双击桌面快捷方式即可。

---

## 使用方式

### 方式一：双击快捷方式（推荐日常使用）

复制文章链接后，双击桌面的 `微信公众号 → Markdown` 快捷方式，自动读取剪贴板并完成保存。

### 方式二：命令行

```bash
# 剪贴板模式（先复制链接）
python app/main.py

# 指定 URL
python app/main.py --url "https://mp.weixin.qq.com/s/xxxx"

# 临时指定保存目录
python app/main.py --save-dir "D:/我的笔记"

# 指定账号（对应 config.yaml 中的 name）
python app/main.py --account "公众号B"
```

---

## 目录结构

```
wechat-to-markdown/
  app/
    main.py                  # 主入口
    config.py                # 配置加载
    extract/
      parser.py              # 获取 HTML，解析标题/时间/正文
      cleaner.py             # 清洗非正文区域
      markdown_writer.py     # HTML 转 Markdown
    storage/
      db.py                  # SQLite 去重与日志
      file_writer.py         # 写入目标目录
  assets/
    icon.ico                 # 快捷方式图标
    make_icon.py             # 图标生成脚本
  config/
    config.example.yaml      # 配置示例
    config.yaml              # 你的配置（不提交到 Git）
  data/                      # 运行时生成（不提交到 Git）
    state/app.db
    logs/
  requirements.txt
  抓取公众号文章.bat
  创建桌面快捷方式.bat
```

---

## 常见问题

**Q：如何修改保存位置？**
A：打开 `config/config.yaml`，修改 `save_dir` 字段为你想要的任意文件夹路径，保存后立即生效。也可以用 `--save-dir` 参数临时指定单次的保存路径。

**Q：提示"剪贴板中没有找到有效链接"？**
A：请确认已在微信中点击 `...` → 复制链接，再运行工具。注意复制的是文章链接（`mp.weixin.qq.com`），不是分享文字。

**Q：文件名乱码或包含非法字符？**
A：工具会自动清除 Windows 文件名非法字符（`\ / : * ? " < > |`），替换为下划线。

**Q：文章末尾有广告内容被一起抓进来了？**
A：工具会过滤常见广告区块（打赏、二维码、相关推荐等），如仍有残留，可以在保存后手动删除末尾内容。

## License

MIT
