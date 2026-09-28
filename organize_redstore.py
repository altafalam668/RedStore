#!/usr/bin/env python3
from pathlib import Path
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parent
IMAGE_DIR = ROOT / "images"

IMAGE_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".avif", ".ico"
}

# Files that are not part of the website and should not be moved.
IGNORE_FILES = {
    ".DS_Store",
}

def replace_image_references(path: Path, image_names):
    text = path.read_text(encoding="utf-8", errors="ignore")

    # Longest names first, so names containing another image name are handled safely.
    for name in sorted(image_names, key=len, reverse=True):
        escaped = re.escape(name)

        # HTML attributes: src="file", src='file', href="file" for image assets.
        text = re.sub(
            rf'(?P<prefix>\b(?:src|href)\s*=\s*["\']){escaped}(?P<suffix>["\'])',
            rf'\g<prefix>images/{name}\g<suffix>',
            text,
            flags=re.IGNORECASE,
        )

        # CSS/HTML url(file), url("file"), url('file')
        text = re.sub(
            rf'(?P<prefix>\burl\(\s*["\']?){escaped}(?P<suffix>["\']?\s*\))',
            rf'\g<prefix>images/{name}\g<suffix>',
            text,
            flags=re.IGNORECASE,
        )

    path.write_text(text, encoding="utf-8")

def main():
    print("RedStore image organizer")
    print("------------------------")
    print(f"Project folder: {ROOT}")

    IMAGE_DIR.mkdir(exist_ok=True)

    # 1. Move image files from the project root into images/
    moved = []
    already = []

    for path in sorted(ROOT.iterdir()):
        if not path.is_file():
            continue
        if path.name in IGNORE_FILES:
            continue
        if path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue

        destination = IMAGE_DIR / path.name

        if destination.exists():
            # Do not overwrite an existing image.
            print(f"SKIP (already exists): {path.name}")
            already.append(path.name)
            continue

        shutil.move(str(path), str(destination))
        moved.append(path.name)

    # 2. Update image references in all HTML/CSS files.
    image_names = moved + already
    code_files = list(ROOT.glob("*.html")) + list(ROOT.glob("*.css"))

    for path in code_files:
        replace_image_references(path, image_names)

    # 3. Remove macOS metadata file from the repository if present.
    ds_store = ROOT / ".DS_Store"
    if ds_store.exists():
        ds_store.unlink()
        print("REMOVED: .DS_Store")

    print()
    print(f"Moved {len(moved)} image file(s) into images/.")
    print(f"Updated {len(code_files)} HTML/CSS file(s).")
    print()
    print("New structure:")
    print("  RedStore/")
    print("  ├── index.html")
    print("  ├── product.html")
    print("  ├── product-detail.html")
    print("  ├── account.html")
    print("  ├── cart.html")
    print("  ├── style.css")
    print("  ├── README.md")
    print("  └── images/")
    print()
    print("IMPORTANT: Open the website locally and check every page before pushing.")
    print("Then run:")
    print("  git add .")
    print('  git commit -m "Organize website images"')
    print("  git push")
    print()

if __name__ == "__main__":
    main()
