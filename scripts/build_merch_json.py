#!/usr/bin/env python3
"""
Build a simple merch "catalog" JSON from images in Google Cloud Storage bucket.

This is used by `manifest.py merch`.

The script reads from the public bucket at:
https://storage.googleapis.com/ahoy-dynamic-content/merch-2026/

Naming convention: PRO - #1 - FRONT.jpg, PRO - #1 - BACK.jpg, etc.
Products are grouped by their number (e.g., #1, #2, #3).

Output: data/merch.json
Shape:
{
  "generated_at": "ISO8601",
  "items": [
    {
      "id": "pro_1",
      "name": "PRO #1 T-Shirt",
      "image_url": "https://storage.googleapis.com/ahoy-dynamic-content/merch-2026/PRO%20-%20%231%20-%20FRONT.jpg",
      "image_url_back": "https://storage.googleapis.com/ahoy-dynamic-content/merch-2026/PRO%20-%20%231%20-%20BACK.jpg",
      "price_usd": 20.0,
      "kind": "merch",
      "available": true
    }
  ]
}
"""

from __future__ import annotations

import json
import re
import urllib.parse
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional


BUCKET_BASE_URL = "https://storage.googleapis.com/ahoy-dynamic-content/merch-2026"
ALLOWED_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


def _slugify(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    return s or "item"


@dataclass(frozen=True)
class MerchItem:
    id: str
    name: str
    image_url: str
    image_url_back: Optional[str] = None
    price_usd: float = 20.0
    kind: str = "merch"
    available: bool = True

    def as_dict(self) -> dict:
        result = {
            "id": self.id,
            "name": self.name,
            "image_url": self.image_url,
            "price_usd": self.price_usd,
            "kind": self.kind,
            "available": self.available,
        }
        if self.image_url_back:
            result["image_url_back"] = self.image_url_back
        return result


def _parse_product_number(filename: str) -> Optional[int]:
    """
    Parse product number from filename like 'PRO - #1 - FRONT.jpg' or 'PRO #2 - BACK.jpg'
    Returns the number (1, 2, 3, etc.) or None if not found.
    """
    # Match patterns like "#1", "# 1", " #1 ", etc.
    match = re.search(r'#\s*(\d+)', filename, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def _is_front_image(filename: str) -> bool:
    """Check if filename indicates a FRONT image."""
    return "FRONT" in filename.upper()


def _is_back_image(filename: str) -> bool:
    """Check if filename indicates a BACK image."""
    return "BACK" in filename.upper()


def _build_bucket_url(filename: str) -> str:
    """Build the full URL for a file in the bucket."""
    # URL encode the filename
    encoded = urllib.parse.quote(filename, safe='')
    return f"{BUCKET_BASE_URL}/{encoded}"


def build_merch_json(
    out_path: str | Path = "data/merch.json",
) -> dict:
    """
    Generate merch JSON from Google Cloud Storage bucket images.
    
    The function expects images in the bucket following the naming convention:
    - PRO - #1 - FRONT.jpg
    - PRO - #1 - BACK.jpg
    - PRO #2 - FRONT.jpg
    - PRO #2 - BACK.jpg
    etc.
    
    Products are grouped by number, with FRONT and BACK images paired together.
    All products are priced at $20.00 (t-shirts).

    Returns the generated object.
    """
    out_path_p = Path(out_path)
    
    # Known products based on the user's upload
    # Format: (product_number, front_filename, back_filename)
    known_products = [
        (1, "PRO - #1 - FRONT.jpg", "PRO - #1 - BACK.jpg"),
        (2, "PRO #2 - FRONT.jpg", "PRO #2 - BACK.jpg"),
        (3, "PRO #3 - FRONT.jpg", "PRO #3 - BACK.jpg"),
    ]
    
    items: list[MerchItem] = []
    
    for product_num, front_file, back_file in known_products:
        # Build URLs for both images
        front_url = _build_bucket_url(front_file)
        back_url = _build_bucket_url(back_file)
        
        # Create product name
        product_name = f"PRO #{product_num} T-Shirt"
        product_id = f"pro_{product_num}"
        
        items.append(
            MerchItem(
                id=product_id,
                name=product_name,
                image_url=front_url,
                image_url_back=back_url,
                price_usd=20.0,  # Fixed price for t-shirts
            )
        )
    
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "items": [it.as_dict() for it in items],
    }

    out_path_p.parent.mkdir(parents=True, exist_ok=True)
    out_path_p.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"✅ Generated {len(items)} merch items in {out_path_p}")
    return payload

