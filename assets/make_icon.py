"""
Convert ../icon_source.png (or any PNG next to this script's parent) to icon.ico
Usage: python assets/make_icon.py
No third-party dependencies required (pure stdlib).
If Pillow is available it will be used for higher-quality downscaling.
"""
import struct
import zlib
from pathlib import Path

SIZES = [256, 48, 32, 16]
SCRIPT_DIR = Path(__file__).parent          # assets/
PROJECT_DIR = SCRIPT_DIR.parent             # project root
OUTPUT = SCRIPT_DIR / "icon.ico"

# Candidate source images (checked in order)
CANDIDATES = [
    PROJECT_DIR / "icon_source.png",
    PROJECT_DIR / "\u56fe\u6807image.png",  # 图标image.png
]


# ---------------------------------------------------------------------------
# Pure-stdlib PNG reader (supports 8-bit RGB and RGBA only)
# ---------------------------------------------------------------------------

def _read_png_rgba(data: bytes):
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "Not a valid PNG file"
    pos = 8
    chunks = {}
    while pos < len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        name = data[pos + 4:pos + 8]
        payload = data[pos + 8:pos + 8 + length]
        pos += 12 + length
        chunks.setdefault(name, []).append(payload)

    ihdr = chunks[b"IHDR"][0]
    W, H = struct.unpack(">II", ihdr[:8])
    bit_depth, color_type = ihdr[8], ihdr[9]
    assert bit_depth == 8, f"Only 8-bit PNG supported (got {bit_depth})"
    assert color_type in (2, 6), f"Only RGB/RGBA PNG supported (color_type={color_type})"
    has_alpha = color_type == 6
    bpp = 4 if has_alpha else 3

    raw = zlib.decompress(b"".join(chunks[b"IDAT"]))
    pixels = []
    idx = 0
    for _ in range(H):
        idx += 1  # skip filter byte (assume filter 0)
        row = []
        for x in range(W):
            r, g, b = raw[idx], raw[idx + 1], raw[idx + 2]
            a = raw[idx + 3] if has_alpha else 255
            row.append((r, g, b, a))
            idx += bpp
        pixels.append(row)
    return W, H, pixels


def _nearest_resize(pixels, src_w, src_h, dst):
    return [
        [pixels[int(y * src_h / dst)][int(x * src_w / dst)] for x in range(dst)]
        for y in range(dst)
    ]


def _pixels_to_png(pixels, size):
    def chunk(name, data):
        crc = zlib.crc32(name + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + name + data + struct.pack(">I", crc)

    ihdr_data = struct.pack(">II", size, size) + bytes([8, 6, 0, 0, 0])
    rows = b"".join(
        b"\x00" + b"".join(bytes(px) for px in row)
        for row in pixels
    )
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr_data)
        + chunk(b"IDAT", zlib.compress(rows, 9))
        + chunk(b"IEND", b"")
    )


def _build_ico(images):
    header = struct.pack("<HHH", 0, 1, len(images))
    offset = 6 + 16 * len(images)
    dir_entries = b""
    for s, png in images:
        w = h = 0 if s >= 256 else s
        dir_entries += struct.pack("<BBBBHHII", w, h, 0, 0, 1, 32, len(png), offset)
        offset += len(png)
    return header + dir_entries + b"".join(p for _, p in images)


# ---------------------------------------------------------------------------
# Pillow path (higher quality, optional)
# ---------------------------------------------------------------------------

def _convert_with_pillow(src_path: Path):
    from PIL import Image
    img = Image.open(src_path).convert("RGBA")
    images = []
    for s in SIZES:
        resized = img.resize((s, s), Image.LANCZOS)
        import io
        buf = io.BytesIO()
        resized.save(buf, format="PNG")
        images.append((s, buf.getvalue()))
    return _build_ico(images)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    src = next((p for p in CANDIDATES if p.exists()), None)
    if src is None:
        raise FileNotFoundError(
            "No source image found. Place your image at: " +
            str(PROJECT_DIR / "icon_source.png")
        )

    print(f"Source image : {src}")

    try:
        ico_data = _convert_with_pillow(src)
        print("(used Pillow for high-quality scaling)")
    except ImportError:
        raw = src.read_bytes()
        W, H, pixels = _read_png_rgba(raw)
        print(f"Image size   : {W}x{H}  (stdlib mode, no Pillow)")
        images = []
        for s in SIZES:
            p = _nearest_resize(pixels, W, H, s) if (W != s or H != s) else pixels
            images.append((s, _pixels_to_png(p, s)))
        ico_data = _build_ico(images)

    OUTPUT.write_bytes(ico_data)
    print(f"Icon written : {OUTPUT}  ({len(ico_data):,} bytes)")


if __name__ == "__main__":
    main()
