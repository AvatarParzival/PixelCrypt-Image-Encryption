"""Reversible pixel transformation used by PixelCrypt.

This module applies a key-derived XOR stream to the red, green, and blue
channels of an image. The alpha channel is preserved. Output should be saved
as PNG because lossy formats such as JPEG cannot be decrypted exactly.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Iterator

from PIL import Image


BLOCK_SIZE = 32


def _key_stream(key: str, length: int) -> Iterator[int]:
    """Yield *length* deterministic bytes derived from *key*."""
    if not key:
        raise ValueError("A non-empty key is required.")

    seed = hashlib.sha256(key.encode("utf-8")).digest()
    produced = 0
    counter = 0

    while produced < length:
        block = hashlib.sha256(seed + counter.to_bytes(8, "big")).digest()
        for value in block:
            if produced >= length:
                return
            yield value
            produced += 1
        counter += 1


def transform_image(image: Image.Image, key: str) -> Image.Image:
    """Return an RGBA image transformed with a reversible XOR operation."""
    rgba = image.convert("RGBA")
    raw = bytearray(rgba.tobytes())
    stream = _key_stream(key, (len(raw) // 4) * 3)

    for index in range(0, len(raw), 4):
        raw[index] ^= next(stream)       # Red
        raw[index + 1] ^= next(stream)   # Green
        raw[index + 2] ^= next(stream)   # Blue
        # Alpha is intentionally unchanged.

    return Image.frombytes("RGBA", rgba.size, bytes(raw))


def process_image(input_path: str | Path, output_path: str | Path, key: str) -> Path:
    """Transform an image and save the reversible result as a PNG file."""
    source = Path(input_path)
    destination = Path(output_path)

    if not source.is_file():
        raise FileNotFoundError(f"Image not found: {source}")
    if not key:
        raise ValueError("A non-empty key is required.")
    if destination.suffix.lower() != ".png":
        raise ValueError("The output file must use the .png extension.")

    with Image.open(source) as image:
        transformed = transform_image(image, key)
        destination.parent.mkdir(parents=True, exist_ok=True)
        transformed.save(destination, format="PNG")

    return destination
