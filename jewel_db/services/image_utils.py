"""
Lightweight helpers for normalising uploaded images.

Keeps everything in-memory, uses Pillow only.
"""

from __future__ import annotations

from io import BytesIO
from typing import Literal

from PIL import Image

MAX_DIM = 1600  # px – longest side
JPEG_QUALITY = 85  # %
AllowedType = Literal["image/jpeg", "image/png", "image/webp"]


def normalise_image(data: bytes, mime: AllowedType) -> tuple[bytes, str]:
    """
    Down-scale / recompress *data* so the longest side ≤ MAX_DIM
    and return *(bytes, extension)*.

    • PNG keeps alpha & stays PNG
    • JPEG / WebP → RGB JPEG
    """
    img = Image.open(BytesIO(data))
    if max(img.size) > MAX_DIM:
        img.thumbnail((MAX_DIM, MAX_DIM), Image.LANCZOS)

    buf = BytesIO()
    ext: str
    match mime:
        case "image/png":
            img.save(buf, format="PNG", optimize=True)
            ext = ".png"
        case "image/webp":
            # convert to JPEG – broadest browser support
            img = img.convert("RGB")
            img.save(buf, format="JPEG", quality=JPEG_QUALITY, optimize=True)
            ext = ".jpg"
        case _:
            # default / image/jpeg
            img = img.convert("RGB")
            img.save(buf, format="JPEG", quality=JPEG_QUALITY, optimize=True)
            ext = ".jpg"

    return buf.getvalue(), ext
