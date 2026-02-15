import base64
from dataclasses import dataclass
from io import BytesIO
from math import ceil
from pathlib import Path
import time

from openai import AsyncOpenAI
from PIL import Image

from dev_pytopia import with_error_handling

from .....services.ai_performance_metrics import AIPerformanceMetrics


@dataclass
class ImageUsage:
    model: str
    size: str
    quality: str
    num_images: int
    cost_per_image: float
    total_cost: float
    input_image_tokens: int = 0
    input_image_cost: float = 0.0


@with_error_handling(
    exclude_methods={
        "__init__",
        "start_tracking",
        "_calculate_cost",
        "_calculate_image_input_tokens",
        "_calculate_image_input_cost",
        "_get_image_dimensions",
        "_prepare_image_file",
        "_finalize_result",
        "get_last_cost",
        "get_total_cost",
    }
)
class ImageAPIWrapper:
    QUALITY_MAP = {"standard": "medium", "hd": "high", "low": "low", "medium": "medium", "high": "high"}
    IMAGE_TOKEN_MULTIPLIER = 1.62

    def __init__(self, client: AsyncOpenAI, model_configurations: dict = None):
        self.client = client
        self.model_configurations = model_configurations or {}
        self.last_usage = self.total_usage = None

    def start_tracking(self):
        self.last_usage = self.total_usage = None

    def get_last_cost(self) -> float:
        return self.last_usage.total_cost if self.last_usage else 0.0

    def get_total_cost(self) -> float:
        return self.total_usage if self.total_usage is not None else 0.0

    def _calculate_cost(self, model: str, size: str, quality: str, num_images: int) -> tuple[float, float]:
        pricing = self.model_configurations.get(model, {}).get("pricing", {})
        cost_per_image = pricing.get(self.QUALITY_MAP.get(quality, "medium"), {}).get(size, 0.0)
        return cost_per_image, cost_per_image * num_images

    def _get_image_dimensions(self, image: str | bytes | Path) -> tuple[int, int]:
        if isinstance(image, (str, Path)) and Path(image).exists():
            source = image
        elif isinstance(image, bytes):
            source = BytesIO(image)
        elif isinstance(image, str):
            source = BytesIO(base64.b64decode(image))
        else:
            raise ValueError("Unable to determine image dimensions")
        with Image.open(source) as img:
            return img.size

    def _calculate_image_input_tokens(self, width: int, height: int) -> int:
        return ceil(ceil(width / 32) * ceil(height / 32) * self.IMAGE_TOKEN_MULTIPLIER)

    def _calculate_image_input_cost(self, model: str, tokens: int) -> float:
        return (tokens / 1_000_000) * self.model_configurations.get(model, {}).get("pricing", {}).get(
            "image_input", 0.0
        )

    def _prepare_image_file(self, image: str | bytes | Path, default_name: str = "image.png"):
        if isinstance(image, (str, Path)) and Path(image).exists():
            return open(image, "rb"), True
        if isinstance(image, bytes):
            file = BytesIO(image)
        elif isinstance(image, str):
            file = BytesIO(base64.b64decode(image))
        else:
            raise ValueError("Invalid image format")
        file.name = default_name
        return file, False

    def _finalize_result(
        self,
        result,
        model: str,
        size: str,
        quality: str,
        n: int,
        start_time: float,
        with_metrics: bool,
        input_tokens: int = 0,
        input_cost: float = 0.0,
    ):
        if not result.data:
            return None

        cost_per_image, output_cost = self._calculate_cost(model, size, quality, n)
        total_cost = output_cost + input_cost

        self.last_usage = ImageUsage(
            model=model,
            size=size,
            quality=quality,
            num_images=n,
            cost_per_image=cost_per_image,
            total_cost=total_cost,
            input_image_tokens=input_tokens,
            input_image_cost=input_cost,
        )
        if self.total_usage is not None:
            self.total_usage += total_cost

        images = [img.b64_json or img.url for img in result.data] or None
        if not with_metrics:
            return images
        return images, AIPerformanceMetrics(
            elapsed_time_seconds=time.time() - start_time,
            cost_dollars=total_cost,
            api_calls=1,
            model_name=model,
            provider_name="openai",
        )

    async def generate(self, model: str, prompt: str, with_metrics: bool = False, **kwargs):
        start_time = time.time()
        size, quality, n = kwargs.get("size", "1024x1024"), kwargs.get("quality", "standard"), kwargs.get("n", 1)
        result = await self.client.images.generate(model=model, prompt=prompt, **kwargs)
        return self._finalize_result(result, model, size, quality, n, start_time, with_metrics)

    async def edit(self, model: str, image: str | bytes | Path, prompt: str, with_metrics: bool = False, **kwargs):
        start_time = time.time()
        size, quality, n = kwargs.get("size", "1024x1024"), kwargs.get("quality", "standard"), kwargs.get("n", 1)

        width, height = self._get_image_dimensions(image)
        input_tokens = self._calculate_image_input_tokens(width, height)
        input_cost = self._calculate_image_input_cost(model, input_tokens)
        image_file, image_needs_close = self._prepare_image_file(image)

        mask_file, mask_needs_close = None, False
        if "mask" in kwargs:
            mask = kwargs.pop("mask")
            mask_width, mask_height = self._get_image_dimensions(mask)
            input_tokens += self._calculate_image_input_tokens(mask_width, mask_height)
            input_cost += self._calculate_image_input_cost(model, input_tokens)
            mask_file, mask_needs_close = self._prepare_image_file(mask, "mask.png")

        try:
            edit_kwargs = {"model": model, "image": image_file, "prompt": prompt, **kwargs}
            if mask_file:
                edit_kwargs["mask"] = mask_file
            result = await self.client.images.edit(**edit_kwargs)
        finally:
            if image_needs_close:
                image_file.close()
            if mask_needs_close:
                mask_file.close()

        return self._finalize_result(
            result, model, size, quality, n, start_time, with_metrics, input_tokens, input_cost
        )
