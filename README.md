# wechat-to-markdown

从微信公众号文章链接自动提取正文，保存为 Markdown 文件到任意指定文件夹。

**核心使用流程：**
1. 在微信中打开文章，右上角 `···` → 复制链接
2. 双击桌面快捷方式 `wechat-to-markdown`
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

## 安装（首次使用）

**要求：** Windows + Python 3.9+

```bash
git clone https://github.com/yihan498/wechat-to-markdown.git
cd wechat-to-markdown
```

然后双击 **`setup.bat`**，它会自动完成：
1. 安装所有依赖
2. 从示例生成 `config/config.yaml`
3. 生成快捷方式图标
4. 在桌面创建 `wechat-to-markdown` 快捷方式

---

## 配置保存位置

打开 `config/config.yaml`，修改 `save_dir` 为你的 Obsidian 或任意文件夹路径：

```yaml
accounts:
  - name: "公众号A"
    save_dir: "D:/我的笔记/公众号"   # ← 改成你想要的文件夹，不存在会自动创建
    default: true
```

支持多个公众号，每个对应不同目录：

```yaml
accounts:
  - name: "公众号A"
    save_dir: "D:/笔记/公众号A"
    default: true
  - name: "公众号B"
    save_dir: "D:/笔记/公众号B"
```

---

## 使用方式

### 方式一：桌面快捷方式（推荐）

复制文章链接 → 双击桌面的 `wechat-to-markdown` 快捷方式。

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
    make_icon.py             # 图标生成脚本（读取 icon_source.png）
  config/
    config.example.yaml      # 配置示例
    config.yaml              # 你的配置（不提交到 Git）
  data/                      # 运行时生成（不提交到 Git）
    state/app.db
    logs/
  icon_source.png            # 自定义快捷方式图标源图
  setup.bat                  # 首次安装脚本（一键完成所有初始化）
  run_wechat_to_markdown.bat # 主启动脚本
  创建桌面快捷方式.bat         # 单独重建桌面快捷方式
  requirements.txt
```

---

## 常见问题

**Q：如何修改保存位置？**
A：打开 `config/config.yaml`，修改 `save_dir` 字段，保存后立即生效。也可以用 `--save-dir` 参数临时指定单次的保存路径。

**Q：提示"剪贴板中没有找到有效链接"？**
A：请确认已在微信中点击 `···` → 复制链接，再运行工具。注意复制的是文章链接（`mp.weixin.qq.com`），不是分享文字。

**Q：文章末尾有广告内容被一起抓进来了？**
A：工具会过滤常见广告区块（打赏、二维码、相关推荐等），如仍有残留，可以在保存后手动删除末尾内容。

## License

MIT
