from dataclasses import dataclass
import textwrap
from typing import Any


@dataclass
class TextMessage:
    role: str
    text: str

    def to_dict(self) -> dict[str, Any]:
        return {"role": self.role, "content": self.text or ""}

    def get_str_representation(self, colors: dict[str, str], width: int) -> list[str]:
        return [
            f"{colors['content']}{w}{colors['reset']}"
            for line in (self.text or "").split("\n")
            for w in textwrap.wrap(line, width - 4) or [""]
        ]
