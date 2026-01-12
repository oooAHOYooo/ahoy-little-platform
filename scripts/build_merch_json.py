#!/usr/bin/env python3
"""
Build a simple merch "catalog" JSON from images in static/merch/images.

This is used by `manifest.py merch`.

Output: data/merch.json
Shape:
{
  "generated_at": "ISO8601",
  "items": [
    {
      "id": "ahoy_logo_tshirt_black",
      "name": "Ahoy Logo Tshirt Black",
      "image_url": "/static/merch/images/ahoy_logo_tshirt_black.png",
      "price_usd": 25.0,
      "kind": "merch",
      "available": true
    }
  ]
}
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


ALLOWED_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


def _slugify(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    return s or "item"


def _titleize_from_slug(slug: str) -> str:
    words = [w for w in re.split(r"[_\-]+", slug) if w]
    # Keep "ahoy" uppercase for a nicer display
    out = []
    for w in words:
        if w.lower() == "ahoy":
            out.append("Ahoy")
        else:
            out.append(w[:1].upper() + w[1:])
    return " ".join(out) or "Item"


def _guess_price_usd(slug: str) -> float:
    s = slug.lower()
    if any(k in s for k in ["sticker", "decal"]):
        return 3.0
    if any(k in s for k in ["poster", "print"]):
        return 15.0
    if any(k in s for k in ["tshirt", "tee", "shirt", "hoodie"]):
        return 25.0
    return 20.0


@dataclass(frozen=True)
class MerchItem:
    id: str
    name: str
    image_url: str
    price_usd: float
    kind: str = "merch"
    available: bool = True

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "image_url": self.image_url,
            "price_usd": self.price_usd,
            "kind": self.kind,
            "available": self.available,
        }


def _iter_image_files(images_dir: Path) -> Iterable[Path]:
    if not images_dir.exists():
        return []
    files = [p for p in images_dir.iterdir() if p.is_file() and p.suffix.lower() in ALLOWED_EXTS]
    files.sort(key=lambda p: p.name.lower())
    return files


def build_merch_json(
    images_dir: str | Path = "static/merch/images",
    out_path: str | Path = "data/merch.json",
) -> dict:
    """
    Generate merch JSON from images and write it to disk.

    Returns the generated object.
    """
    images_dir_p = Path(images_dir)
    out_path_p = Path(out_path)

    items: list[MerchItem] = []
    for img in _iter_image_files(images_dir_p):
        slug = _slugify(img.stem)
        items.append(
            MerchItem(
                id=slug,
                name=_titleize_from_slug(slug),
                image_url=f"/static/merch/images/{img.name}",
                price_usd=_guess_price_usd(slug),
            )
        )

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "items": [it.as_dict() for it in items],
    }

    out_path_p.parent.mkdir(parents=True, exist_ok=True)
    out_path_p.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload

