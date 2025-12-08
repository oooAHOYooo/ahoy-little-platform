import json
import re
import pathlib
import sys

def slugify(text):
    """
    Convert text to a slug: lowercase, remove non-alphanumeric chars (except hyphens), replace spaces/underscores with hyphens.
    """
    text = text.lower()
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'[^a-z0-9-]', '', text)
    text = text.strip('-')
    return text

def build_merch_json():
    # Define paths
    base_dir = pathlib.Path(__file__).parent.parent
    images_dir = base_dir / "static" / "merch" / "images"
    metadata_file = base_dir / "static" / "merch" / "merch_metadata.json"
    output_file = base_dir / "static" / "data" / "merch_products.json"

    print(f"Scanning images in: {images_dir}")

    if not images_dir.exists():
        print(f"Error: Images directory not found: {images_dir}")
        return

    # Load metadata if it exists
    metadata = {}
    if metadata_file.exists():
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            print(f"Loaded metadata for {len(metadata)} items.")
        except Exception as e:
            print(f"Warning: Could not read metadata file: {e}")
    else:
        print("No metadata file found, proceeding without it.")

    products = []
    
    # Extensions to scan
    extensions = {'.jpg', '.jpeg', '.png', '.webp'}

    # Scan for images
    image_files = [f for f in images_dir.iterdir() if f.suffix.lower() in extensions]
    
    for img_path in sorted(image_files):
        filename = img_path.name
        stem = img_path.stem  # filename without extension
        
        # Look up metadata
        meta = metadata.get(stem, {})
        
        # Determine ID
        if "slug" in meta:
            product_id = slugify(meta["slug"])
        else:
            product_id = slugify(stem)
            
        # Determine Name
        if "name" in meta:
            name = meta["name"]
        else:
            # Replace underscores with spaces and title case
            name = stem.replace("_", " ").title()
            
        # Build product object
        product = {
            "id": product_id,
            "name": name,
            "description": meta.get("description", ""),
            "price_cents": meta.get("price_cents", 2500),
            "currency": meta.get("currency", "USD"),
            "artist": meta.get("artist", "Ahoy Indie Media"),
            "tags": meta.get("tags", []),
            "image": f"static/merch/images/{filename}",
            "square_checkout_url": meta.get("square_checkout_url", ""),
            "inventory": meta.get("inventory", "in_stock")
        }
        
        products.append(product)

    # Write output
    try:
        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(products, f, indent=2)
            
        print(f"Successfully wrote {len(products)} products to {output_file}")
    except Exception as e:
        print(f"Error writing output file: {e}")

if __name__ == "__main__":
    build_merch_json()

