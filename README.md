# wechat-to-obsidian

从微信公众号文章链接自动提取正文，保存为 Markdown 文件到 Obsidian 仓库。

**核心使用流程：**
1. 在微信中打开文章，右上角 `...` → 复制链接
2. 双击 `抓取公众号文章.bat`
3. 文件自动保存到 Obsidian 指定目录，右下角弹出通知

## 功能

- 自动读取剪贴板中的公众号链接，无需手动输入
- 提取标题、发布时间、正文文字，过滤广告和推广内容
- 输出带 YAML frontmatter 的 Markdown 文件
- SQLite 去重，同一篇文章不会重复保存
- 支持多个公众号，每个对应不同的 Obsidian 保存目录
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

## 安装

**要求：** Windows + Python 3.9+

```bash
# 1. 克隆项目
git clone https://github.com/你的用户名/wechat-to-obsidian.git
cd wechat-to-obsidian

# 2. 安装依赖（网络慢可加 -i https://pypi.tuna.tsinghua.edu.cn/simple）
pip install -r requirements.txt

# 3. 复制配置文件并填写
copy config\config.example.yaml config\config.yaml
```

然后编辑 `config/config.yaml`，填写公众号名称和 Obsidian 保存路径。

## 配置

`config/config.yaml` 示例：

```yaml
accounts:
  - name: "公众号A"
    save_dir: "D:/Obsidian/公众号/公众号A"
    default: true      # 默认账号，不带 --account 参数时使用

  - name: "公众号B"
    save_dir: "D:/Obsidian/公众号/公众号B"
```

`save_dir` 填写 Obsidian 仓库中的目标文件夹绝对路径，不存在会自动创建。

## 使用方式

### 方式一：双击快捷方式（推荐日常使用）

复制文章链接后，双击 `抓取公众号文章.bat`，自动读取剪贴板并完成保存。

如需固定到桌面：右键 `.bat` 文件 → 创建快捷方式 → 拖到桌面。

### 方式二：命令行

```bash
# 剪贴板模式（先复制链接）
python app/main.py

# 指定 URL
python app/main.py --url "https://mp.weixin.qq.com/s/xxxx"

# 指定账号（对应 config.yaml 中的 name）
python app/main.py --account "公众号B"

# 同时指定
python app/main.py --url "https://mp.weixin.qq.com/s/xxxx" --account "公众号B"
```

## 目录结构

```
wechat-to-obsidian/
  app/
    main.py                  # 主入口
    config.py                # 配置加载
    extract/
      parser.py              # 获取 HTML，解析标题/时间/正文
      cleaner.py             # 清洗非正文区域
      markdown_writer.py     # HTML 转 Markdown
    storage/
      db.py                  # SQLite 去重与日志
      obsidian_writer.py     # 写入 Obsidian 目录
  config/
    config.example.yaml      # 配置示例
    config.yaml              # 你的配置（不提交到 Git）
  data/                      # 运行时生成（不提交到 Git）
    state/app.db
    logs/
  requirements.txt
  抓取公众号文章.bat
```

## 常见问题

**Q：文章末尾有广告内容被一起抓进来了？**
A：工具会在正文中检测到 `（完）` 标记时自动截断。如果你订阅的公众号没有这个标记，可以修改 `app/extract/markdown_writer.py` 中的 `_END_MARKER` 变量为其他结尾标志，或设置为空字符串禁用截断。

**Q：提示"剪贴板中没有找到有效链接"？**
A：请确认已在微信中点击 `...` → 复制链接，再运行工具。注意复制的是文章链接（`mp.weixin.qq.com`），不是分享文字。

**Q：文件名乱码或包含非法字符？**
A：工具会自动清除 Windows 文件名非法字符（`\ / : * ? " < > |`），替换为下划线。

## License

MIT
