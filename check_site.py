from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(".")
HTML_FILES = sorted(ROOT.glob("*.html"))

errors: list[str] = []
warnings: list[str] = []


class SiteParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.references: list[tuple[str, str]] = []
        self.ids: list[str] = []
        self.images_without_alt = 0

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        attributes = dict(attrs)

        element_id = attributes.get("id")

        if element_id:
            self.ids.append(element_id)

        if tag == "a":
            href = attributes.get("href")

            if href:
                self.references.append(("href", href))

        if tag in {
            "img",
            "script",
            "link",
            "source",
        }:
            reference = (
                attributes.get("src")
                or attributes.get("href")
            )

            if reference:
                self.references.append(("asset", reference))

        if tag == "img" and "alt" not in attributes:
            self.images_without_alt += 1


def local_path(reference: str) -> Path | None:
    reference = reference.strip()

    ignored_prefixes = (
        "http://",
        "https://",
        "mailto:",
        "tel:",
        "javascript:",
        "data:",
        "#",
    )

    if reference.startswith(ignored_prefixes):
        return None

    parsed = urlsplit(reference)
    clean_path = unquote(parsed.path)

    if not clean_path:
        return None

    if clean_path.startswith("/"):
        candidate = ROOT / clean_path.lstrip("/")
    else:
        candidate = ROOT / clean_path

    if clean_path.endswith("/"):
        candidate = candidate / "index.html"

    return candidate


for html_file in HTML_FILES:
    parser = SiteParser()

    text = html_file.read_text(
        encoding="utf-8"
    )

    parser.feed(text)

    duplicate_ids = {
        value
        for value in parser.ids
        if parser.ids.count(value) > 1
    }

    for duplicate_id in sorted(duplicate_ids):
        errors.append(
            f"{html_file}: duplicate id '{duplicate_id}'"
        )

    if parser.images_without_alt:
        warnings.append(
            f"{html_file}: "
            f"{parser.images_without_alt} image(s) without alt text"
        )

    for reference_type, reference in parser.references:
        path = local_path(reference)

        if path is None:
            continue

        if path.exists():
            continue

        errors.append(
            f"{html_file}: missing {reference_type} target "
            f"'{reference}'"
        )


for path in ROOT.rglob("*"):
    if not path.is_file():
        continue

    if ".git" in path.parts:
        continue

    if path.suffix.lower() not in {
        ".html",
        ".css",
        ".js",
        ".json",
        ".xml",
        ".txt",
    }:
        continue

    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue

    if "international-13" in text.lower():
        errors.append(
            f"{path}: still references international-13"
        )

    prohibited_phrases = [
        "registration in progress",
        "business registration is currently",
        "registration status",
    ]

    for phrase in prohibited_phrases:
        if phrase in text.lower():
            errors.append(
                f"{path}: contains removed wording '{phrase}'"
            )


contact_path = ROOT / "contact.html"

if contact_path.exists():
    contact_text = contact_path.read_text(
        encoding="utf-8"
    )

    if (
        "https://formsubmit.co/"
        "dradilnwaz@gmail.com"
    ) not in contact_text:
        errors.append(
            "contact.html: FormSubmit recipient is missing"
        )

    if 'id="service"' not in contact_text:
        errors.append(
            "contact.html: service field is missing"
        )


print("IndusBaltic production check")
print("=" * 34)

if warnings:
    print("\nWarnings:")

    for warning in warnings:
        print(f"  - {warning}")

if errors:
    print("\nErrors:")

    for error in errors:
        print(f"  - {error}")

    print(
        f"\nCheck failed with {len(errors)} error(s)."
    )

    sys.exit(1)

print(
    f"\nPassed: checked {len(HTML_FILES)} HTML files."
)
