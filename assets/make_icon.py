"""
生成 icon.ico 文件（微信绿色风格）
运行：python assets/make_icon.py
需要：pip install pillow
"""
import struct
import zlib
from pathlib import Path

OUTPUT = Path(__file__).parent / "icon.ico"
SIZES = [16, 32, 48, 256]


def make_png_bytes(size: int) -> bytes:
    """用纯 Python 生成一张 size×size 的绿色圆形 W 图标（PNG 格式）"""
    # RGBA 像素数组
    bg = (7, 193, 96, 255)      # 微信绿
    fg = (255, 255, 255, 255)   # 白色

    pixels = []
    cx = cy = size / 2
    r = size / 2 - 1

    for y in range(size):
        row = []
        for x in range(size):
            # 圆形边界
            if (x - cx) ** 2 + (y - cy) ** 2 > r ** 2:
                row.append((0, 0, 0, 0))  # 透明
            else:
                row.append(bg)
        pixels.append(row)

    # 在圆内画一个简单的 "W" 字母
    # 字母区域：垂直占圆直径约 40%–85%，水平均分 5 列
    t = int(size * 0.22)   # 字母顶部
    b = int(size * 0.80)   # 字母底部
    stroke = max(1, size // 16)

    def draw_line(x0, y0, x1, y1):
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(steps + 1):
            xi = int(x0 + (x1 - x0) * i / steps)
            yi = int(y0 + (y1 - y0) * i / steps)
            for dx in range(-stroke, stroke + 1):
                for dy in range(-stroke, stroke + 1):
                    nx, ny = xi + dx, yi + dy
                    if 0 <= nx < size and 0 <= ny < size:
                        if pixels[ny][nx][3] != 0:  # 只在圆内画
                            pixels[ny][nx] = fg

    # W 由四条斜线组成
    m = size // 2
    left  = int(size * 0.20)
    ml    = int(size * 0.38)
    mr    = int(size * 0.62)
    right = int(size * 0.80)
    mid_b = int(size * 0.60)

    draw_line(left,  t, ml,    b)
    draw_line(ml,    b, m,     mid_b)
    draw_line(m,     mid_b, mr, b)
    draw_line(mr,    b, right, t)

    # 将 pixels 编码为 PNG
    def png_chunk(name: bytes, data: bytes) -> bytes:
        c = zlib.crc32(name + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + name + data + struct.pack(">I", c)

    signature = b"\x89PNG\r\n\x1a\n"
    ihdr_data = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)  # 8-bit RGB... wait RGBA needs color type 6
    ihdr_data = struct.pack(">II", size, size) + bytes([8, 6, 0, 0, 0])  # RGBA
    ihdr = png_chunk(b"IHDR", ihdr_data)

    raw_rows = []
    for row in pixels:
        raw = b"\x00"  # filter type None
        for (r2, g2, b2, a2) in row:
            raw += bytes([r2, g2, b2, a2])
        raw_rows.append(raw)
    compressed = zlib.compress(b"".join(raw_rows), 9)
    idat = png_chunk(b"IDAT", compressed)
    iend = png_chunk(b"IEND", b"")

    return signature + ihdr + idat + iend


def build_ico(sizes):
    png_images = [(s, make_png_bytes(s)) for s in sizes]

    # ICO 头
    header = struct.pack("<HHH", 0, 1, len(png_images))  # reserved, type=1(ICO), count

    # 目录项：每项 16 字节
    offset = 6 + 16 * len(png_images)
    dir_entries = b""
    for s, png in png_images:
        w = h = 0 if s >= 256 else s  # 256+ 用 0 表示
        size_bytes = len(png)
        dir_entries += struct.pack("<BBBBHHII", w, h, 0, 0, 1, 32, size_bytes, offset)
        offset += size_bytes

    image_data = b"".join(png for _, png in png_images)
    return header + dir_entries + image_data


def main():
    ico_data = build_ico(SIZES)
    OUTPUT.write_bytes(ico_data)
    print(f"图标已生成：{OUTPUT}")


if __name__ == "__main__":
    main()
