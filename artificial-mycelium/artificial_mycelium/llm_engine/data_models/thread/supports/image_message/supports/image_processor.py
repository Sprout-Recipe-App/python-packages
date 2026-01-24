import base64
from io import BytesIO
from pathlib import Path
import re

from PIL import Image


class ImageProcessor:
    _cache = {}

    @staticmethod
    def is_base64_string(s: str) -> bool:
        return (
            isinstance(s, str)
            and len(s) >= 100
            and len(s) % 4 == 0
            and bool(re.fullmatch(r"[A-Za-z0-9+/]*={0,2}", s))
        )

    @staticmethod
    def to_base64(data: str | Path) -> str:
        if isinstance(data, str) and ImageProcessor.is_base64_string(data):
            return data
        key = str(data)
        if key in ImageProcessor._cache:
            return ImageProcessor._cache[key]

        img = Image.open(data)
        if "A" in img.getbands():
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img.convert("RGB"), mask=img.getchannel("A"))
            img = bg
        elif img.mode != "RGB":
            img = img.convert("RGB")

        buf = BytesIO()
        img.save(buf, "JPEG", quality=100)
        res = base64.b64encode(buf.getvalue()).decode()
        ImageProcessor._cache[key] = res
        return res
