"""Generate on-brand placeholder artwork for demo products (no external assets)."""
from __future__ import annotations

import hashlib
from io import BytesIO

from PIL import Image, ImageDraw, ImageFilter


def _blend(c1: tuple[int, int, int], c2: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )


def _accent_for_gemstone(gemstone: str) -> tuple[int, int, int]:
    g = gemstone.lower()
    if "sapphire" in g or "blue" in g:
        return (45, 95, 190)
    if "emerald" in g or "green" in g:
        return (34, 160, 110)
    if "diamond" in g or "white" in g:
        return (220, 230, 240)
    if "mixed" in g:
        return (160, 90, 200)
    return (201, 169, 98)


def build_product_placeholder(slug: str, gemstone: str) -> Image.Image:
    w, h = 960, 720
    rng = int(hashlib.sha256(slug.encode()).hexdigest()[:8], 16)
    deep = (8, 28, 20)
    mid = (18, 58, 42)
    edge = (12, 36, 28)
    accent = _accent_for_gemstone(gemstone)

    img = Image.new("RGB", (w, h), deep)
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(h - 1, 1)
        base = _blend(deep, mid, t * 0.85 + (rng % 97) / 500)
        draw.line([(0, y), (w, y)], fill=base)

    # soft vignette / corner light
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    cx, cy = int(w * 0.28 + (rng % 40)), int(h * 0.22 + (rng % 30))
    for r in range(380, 40, -18):
        a = max(0, min(90, 140 - r // 4))
        gd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(accent[0], accent[1], accent[2], a))
    img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")

    draw = ImageDraw.Draw(img)
    # gold rim arcs (jewelry case feel)
    gold = (201, 169, 98)
    draw.arc([w * 0.08, h * 0.12, w * 0.92, h * 0.88], start=200 + (rng % 40), end=340, fill=gold, width=4)
    draw.arc([w * 0.12, h * 0.18, w * 0.88, h * 0.82], start=30, end=160, fill=_blend(gold, edge, 0.35), width=2)

    # central “stone”
    sx, sy = w // 2, int(h * 0.48)
    rh = int(min(w, h) * 0.14 + (rng % 18))
    rw = int(rh * 1.35)
    shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse([sx - rw - 6, sy - rh + 10, sx + rw - 6, sy + rh + 10], fill=(0, 0, 0, 110))
    shadow = shadow.filter(ImageFilter.GaussianBlur(12))
    img = Image.alpha_composite(img.convert("RGBA"), shadow).convert("RGB")
    draw = ImageDraw.Draw(img)
    draw.ellipse([sx - rw, sy - rh, sx + rw, sy + rh], outline=gold, width=5)
    inner = _blend(accent, (255, 255, 255), 0.15)
    draw.ellipse([sx - rw + 10, sy - rh + 8, sx + rw - 10, sy + rh - 8], fill=inner)
    hi = _blend(inner, (255, 255, 255), 0.35)
    draw.ellipse([sx - rw // 3, sy - rh, sx + rw // 5, sy - rh // 2], fill=hi)

    return img


def image_to_jpeg_bytes(img: Image.Image, quality: int = 90) -> bytes:
    buf = BytesIO()
    img.convert("RGB").save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue()
