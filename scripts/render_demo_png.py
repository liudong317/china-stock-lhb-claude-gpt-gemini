#!/usr/bin/env python3
"""Render terminal demo output as PNG for README (keys redacted, CJK-safe)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

SKIP_PATTERNS = (
    re.compile(r"^\s*\d+%\|"),
    re.compile(r"^INFO: HTTP Request:"),
    re.compile(r"^WARNING:"),
)

# macOS CJK-capable fonts (terminal-style readability)
FONT_CANDIDATES = (
    ("/System/Library/Fonts/PingFang.ttc", 0),
    ("/System/Library/Fonts/STHeiti Medium.ttc", 0),
    ("/Library/Fonts/Arial Unicode.ttf", None),
    ("/System/Library/Fonts/Supplemental/Songti.ttc", 0),
)


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path, index in FONT_CANDIDATES:
        p = Path(path)
        if not p.exists():
            continue
        try:
            if index is None:
                return ImageFont.truetype(str(p), size)
            return ImageFont.truetype(str(p), size, index=index)
        except OSError:
            continue
    return ImageFont.load_default()


def clean_lines(raw: str) -> list[str]:
    out: list[str] = []
    for line in raw.splitlines():
        if any(p.search(line) for p in SKIP_PATTERNS):
            continue
        line = re.sub(r"sk-[A-Za-z0-9]{20,}", "sk-****REDACTED****", line)
        if line.strip():
            out.append(line.rstrip())
    return out


def wrap_line(text: str, font: ImageFont.FreeTypeFont, max_px: int) -> list[str]:
    if not text:
        return [""]
    lines: list[str] = []
    current = ""
    for ch in text:
        trial = current + ch
        if font.getlength(trial) <= max_px:
            current = trial
        else:
            if current:
                lines.append(current)
            current = ch
    if current:
        lines.append(current)
    return lines or [""]


def render_png(lines: list[str], out_path: Path, *, title: str, max_width: int = 1180) -> None:
    font_size = 15
    font = load_font(font_size)
    title_font = load_font(font_size)

    pad_x, pad_y = 28, 32
    line_gap = 5
    usable = max_width - pad_x * 2

    wrapped: list[str] = []
    for ln in lines:
        wrapped.extend(wrap_line(ln, font, usable))

    line_h = font_size + line_gap
    height = pad_y * 2 + line_h * (len(wrapped) + 2)
    width = max_width

    img = Image.new("RGB", (width, height), (24, 26, 27))
    draw = ImageDraw.Draw(img)

    # title bar accent
    draw.rectangle((0, 0, width, 4), fill=(76, 175, 80))
    draw.text((pad_x, pad_y - 6), title, fill=(129, 199, 132), font=title_font)

    y = pad_y + line_h
    for ln in wrapped:
        color = (210, 210, 210)
        if ln.startswith("==="):
            color = (255, 213, 79)
        elif ln.startswith("$"):
            color = (129, 199, 132)
        elif ln.startswith("- 0") or ln.startswith("- 6") or ln.startswith("- 3"):
            color = (144, 202, 249)
        draw.text((pad_x, y), ln, fill=color, font=font)
        y += line_h

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, optimize=True)
    print(f"wrote {out_path} ({width}x{height})")


def main() -> int:
    demos = [
        (
            ROOT / "docs" / "demo-gitee-glm52.txt",
            ASSETS / "demo-gitee-glm52.png",
            "$ python analyze_lhb.py --lang zh --model glm-5.2",
        ),
        (
            ROOT / "docs" / "demo-github-gpt55.txt",
            ASSETS / "demo-github-gpt55.png",
            "$ python analyze_lhb.py --lang en --model gpt-5.5",
        ),
    ]
    for src, dst, title in demos:
        if not src.exists():
            print(f"missing {src}", file=sys.stderr)
            return 1
        render_png(clean_lines(src.read_text(encoding="utf-8")), dst, title=title)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
