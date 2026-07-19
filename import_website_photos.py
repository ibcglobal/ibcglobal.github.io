from __future__ import annotations

import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

from PIL import Image, ImageOps


ROOT = Path(".")
IMPORT_DIR = ROOT / "_photo_import"
OUTPUT_DIR = ROOT / "assets" / "heritage"
GALLERY_FILE = OUTPUT_DIR / "gallery.json"

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}


def clean_text(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def classify(filename: str) -> tuple[str, str, str, str]:
    name = filename.lower()

    if "thal" in name or "desert" in name:
        return (
            "hyderabad-thal",
            "Hyderabad Thal",
            "Desert landscape and local heritage from the Thal region.",
            "local",
        )

    if "bhakkar" in name or "punjab-college" in name or "punjab_college" in name:
        return (
            "bhakkar",
            "Bhakkar",
            "Education, community and local roots in District Bhakkar.",
            "local",
        )

    if "krakow" in name or "poland" in name:
        return (
            "krakow",
            "Kraków",
            "Our European presence and connection with Poland.",
            "europe",
        )

    if "europe" in name or "european" in name or "eu-" in name:
        return (
            "europe",
            "Europe",
            "International education, travel and mobility across Europe.",
            "europe",
        )

    if "pakistan" in name:
        return (
            "pakistan",
            "Pakistan",
            "Local understanding and international ambition.",
            "local",
        )

    if any(
        word in name
        for word in [
            "young",
            "youth",
            "student",
            "people",
            "group",
            "college",
            "doctor",
            "suit",
            "career",
        ]
    ):
        return (
            "youth",
            "Young People and Education",
            "Supporting students and professionals with education and career guidance.",
            "local",
        )

    return (
        "international",
        "International Opportunities",
        "Education, career and travel opportunities across international destinations.",
        "europe",
    )


def optimise_image(source: Path, destination: Path) -> None:
    with Image.open(source) as image:
        image = ImageOps.exif_transpose(image)
        image = image.convert("RGB")

        target_ratio = 16 / 10
        current_ratio = image.width / image.height

        if current_ratio > target_ratio:
            new_width = int(image.height * target_ratio)
            left = (image.width - new_width) // 2
            image = image.crop(
                (left, 0, left + new_width, image.height)
            )
        else:
            new_height = int(image.width / target_ratio)
            top = (image.height - new_height) // 2
            image = image.crop(
                (0, top, image.width, top + new_height)
            )

        image.thumbnail((1600, 1000), Image.Resampling.LANCZOS)

        canvas = Image.new("RGB", (1600, 1000), "#003399")
        x = (1600 - image.width) // 2
        y = (1000 - image.height) // 2
        canvas.paste(image, (x, y))

        destination.parent.mkdir(parents=True, exist_ok=True)

        canvas.save(
            destination,
            format="JPEG",
            quality=88,
            optimize=True,
            progressive=True,
        )


def main() -> None:
    zip_files = sorted(ROOT.glob("*.zip"))

    if not zip_files:
        raise SystemExit(
            "No ZIP file was found in the project folder."
        )

    zip_path = zip_files[0]

    if IMPORT_DIR.exists():
        shutil.rmtree(IMPORT_DIR)

    IMPORT_DIR.mkdir(parents=True)

    print(f"Extracting: {zip_path.name}")

    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(IMPORT_DIR)

    files = sorted(
        path
        for path in IMPORT_DIR.rglob("*")
        if path.is_file()
        and path.suffix.lower() in IMAGE_EXTENSIONS
        and not path.name.startswith(".")
    )

    if not files:
        raise SystemExit("No supported image files were found.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    gallery_items = []
    counters: dict[str, int] = {}

    for source in files:
        category, title, subtitle, group = classify(source.name)

        counters[category] = counters.get(category, 0) + 1
        number = counters[category]

        output_name = f"{category}-{number:02d}.jpg"
        destination = OUTPUT_DIR / output_name

        try:
            optimise_image(source, destination)
        except Exception as error:
            print(f"Skipped {source.name}: {error}")
            continue

        label_map = {
            "hyderabad-thal": "Hyderabad Thal",
            "bhakkar": "District Bhakkar",
            "krakow": "Kraków and Poland",
            "europe": "European reach",
            "pakistan": "Pakistan",
            "youth": "Youth and education",
            "international": "International opportunity",
        }

        gallery_items.append(
            {
                "title": title,
                "subtitle": subtitle,
                "image": f"assets/heritage/{output_name}",
                "alt": f"{title} photograph",
                "group": group,
                "label": label_map[category],
            }
        )

        print(
            f"{source.name} -> {output_name}"
        )

    GALLERY_FILE.write_text(
        json.dumps(
            gallery_items,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    print()
    print(f"Imported {len(gallery_items)} images.")
    print(f"Gallery updated: {GALLERY_FILE}")


if __name__ == "__main__":
    main()
