"""Generate responsive WebP variants for the large JPEGs in dist/assets.

Idempotent: a variant is generated only if missing. File mtimes are unreliable
after a git checkout, and re-encoding can differ across libwebp versions, so
delete a stem's *.webp files by hand after replacing its source JPEG.
Originals stay in place as the <img> fallback. Never upscales.
"""

from pathlib import Path
from PIL import Image

ASSETS = Path(__file__).parent / "dist" / "assets"
SOURCES = ["road", "packing", "transport", "moving", "auto-detail"]
SOURCES += ['guide-auto','guide-moving','guide-storage','guide-buy-sell','guide-open-enclosed','guide-pricing','guide-luggage','guide-student','team-loading','service-moving','service-storage']
TARGET_WIDTHS = (480, 960, 1600)
QUALITY = 78


def widths_for(src_width):
    """Target widths capped at the source width (the largest variant is native size)."""
    out = []
    for w in TARGET_WIDTHS:
        if w >= src_width:
            out.append(src_width)
            break
        out.append(w)
    return out


def variants(stem):
    """[(width, filename)] for an asset stem, or [] if the source is missing."""
    src = ASSETS / f"{stem}.jpg"
    if not src.exists():
        return []
    with Image.open(src) as im:
        return [(w, f"{stem}-{w}.webp") for w in widths_for(im.width)]


def optimize():
    made = 0
    for stem in SOURCES:
        src = ASSETS / f"{stem}.jpg"
        if not src.exists():
            continue
        with Image.open(src) as im:
            im.load()
            for w in widths_for(im.width):
                out = ASSETS / f"{stem}-{w}.webp"
                if out.exists():
                    continue
                img = im.convert("RGB")
                if w != im.width:
                    img = img.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
                img.save(out, "WEBP", quality=QUALITY, method=6)
                made += 1
    return made


if __name__ == "__main__":
    print(f"generated {optimize()} webp variants")
