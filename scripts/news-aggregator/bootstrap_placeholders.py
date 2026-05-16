"""Generate basic placeholder hero images for Genetic Current.

These are minimal gradient + label images, intended as scaffolding so the
renderer has something to substitute when a source's image isn't reusable.
Replace them with proper editorial photography or commissioned illustrations
when you're ready (same filenames, same WebP format, 1200x675 or similar 16:9).

Run once: python scripts/news-aggregator/bootstrap_placeholders.py
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT_DIR = Path(__file__).resolve().parent.parent.parent / "news" / "images" / "placeholders"
WIDTH = 1200
HEIGHT = 675

# (slug, top hex, bottom hex, label)
CATEGORIES = [
    ("crispr", "#1e3a5f", "#3b6fb5", "Gene editing"),
    ("oncology", "#7a1d28", "#c8102e", "Oncology"),
    ("rare-disease", "#264a7a", "#8aaddf", "Rare disease"),
    ("public-health", "#1e5e3e", "#16a34a", "Public health"),
    ("paediatric", "#5a447a", "#9a85d4", "Paediatric"),
    ("pharmacogenomics", "#7a3e1e", "#d4824a", "Pharmacogenomics"),
    ("ancestry", "#3b5e7a", "#7eabd4", "Ancestry"),
    ("inheritance", "#264a7a", "#5e8fd2", "Inheritance"),
    ("polygenic", "#2c4258", "#4ea0d4", "Polygenic"),
    ("methods", "#1a2e44", "#5e8fd2", "Methods"),
    ("ethics", "#3a3a3a", "#7a7a7a", "Ethics & policy"),
    ("generic", "#152a45", "#3b6fb5", "Genomics"),
]


def _hex_to_rgb(hex_value: str) -> tuple[int, int, int]:
    h = hex_value.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def _make_gradient(top: tuple[int, int, int], bot: tuple[int, int, int]) -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT))
    for y in range(HEIGHT):
        f = y / (HEIGHT - 1)
        color = tuple(int(top[i] + (bot[i] - top[i]) * f) for i in range(3))
        img.paste(color, (0, y, WIDTH, y + 1))
    return img


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in ("Inter-Bold.ttf", "arial.ttf", "Arial.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def make(slug: str, top_hex: str, bot_hex: str, label: str) -> Path:
    top = _hex_to_rgb(top_hex)
    bot = _hex_to_rgb(bot_hex)
    img = _make_gradient(top, bot)
    draw = ImageDraw.Draw(img)

    label_text = label.upper()
    label_font = _load_font(60)
    sub_font = _load_font(22)

    bbox = draw.textbbox((0, 0), label_text, font=label_font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (WIDTH - tw) / 2
    y = (HEIGHT - th) / 2 - 20
    draw.text((x, y), label_text, fill=(255, 255, 255), font=label_font)

    sub = "GENETIC CURRENT · EVAGENE"
    sub_bbox = draw.textbbox((0, 0), sub, font=sub_font)
    sw = sub_bbox[2] - sub_bbox[0]
    draw.text(((WIDTH - sw) / 2, y + th + 18), sub, fill=(255, 255, 255, 200), font=sub_font)

    out_path = OUT_DIR / f"{slug}.webp"
    img.save(out_path, format="WEBP", quality=82, method=6)
    return out_path


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for slug, top, bot, label in CATEGORIES:
        path = make(slug, top, bot, label)
        print(f"  {path.relative_to(OUT_DIR.parent.parent.parent)}")
    print(f"\nWrote {len(CATEGORIES)} placeholder images to {OUT_DIR}")
    print("Replace with proper imagery any time — same filenames, same WebP format.")


if __name__ == "__main__":
    main()
