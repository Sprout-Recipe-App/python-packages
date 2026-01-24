from dataclasses import dataclass, field
from pathlib import Path
import textwrap

from .supports.image_processor import ImageProcessor

ImageData = str | list[str] | Path | list[Path]


@dataclass
class ImageMessage:
    role: str
    image_data: ImageData
    text: str | None = None
    _processed_images: list[str] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self):
        items = self.image_data if isinstance(self.image_data, list) else [self.image_data]
        self._processed_images = [ImageProcessor.to_base64(i) for i in items]

    def to_dict(self) -> dict:
        if not self._processed_images:
            return {"role": self.role, "content": self.text or ""}
        imgs = [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{i}"}}
            for i in self._processed_images
        ]
        return {"role": self.role, "content": imgs + [{"type": "text", "text": self.text or ""}]}

    def get_str_representation(self, colors: dict[str, str], width: int) -> list[str]:
        return [f"{colors['content']}[Image: Base64 encoded]{colors['reset']}"] * len(self._processed_images) + [
            f"{colors['content']}{line}{colors['reset']}"
            for para in (self.text or "").split("\n")
            for line in (textwrap.wrap(para, width=width - 4) or [""])
        ]
