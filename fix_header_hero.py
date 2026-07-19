from pathlib import Path
import re


ROOT = Path(".")
ASSETS = ROOT / "assets"


UTILITY_BAR = '''
<div class="utility-bar">
  <div class="container utility-inner">
    <span>
      Education, career, visa and worldwide travel guidance
    </span>

    <a class="utility-contact" href="/contact.html">
      Contact our team
    </a>
  </div>
</div>

<header class="site-header">
'''


FIXES_CSS = r'''
/* FINAL HEADER AND HERO PANEL REPAIRS */

.utility-bar {
  color: #466174 !important;
  background: #f5f9fc !important;
  border-bottom: 1px solid #dce6ed;
}

.utility-inner {
  min-height: 38px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
  gap: 20px !important;
}

.utility-contact {
  flex: 0 0 auto;
  color: #24558d;
  font-size: 0.76rem;
  font-weight: 800;
}

.utility-contact:hover {
  color: #275f46;
  text-decoration: underline;
}

/*
  Prevent the hero background or route illustration
  from showing through the destination panel.
*/

.hero-panel {
  position: relative;
  isolation: isolate;
  overflow: hidden;
  color: #243d50 !important;
  border: 1px solid rgba(53, 105, 168, 0.18) !important;
  background: #ffffff !important;
  box-shadow: 0 18px 45px rgba(28, 61, 94, 0.15) !important;
  backdrop-filter: none !important;
}

.hero-panel::before,
.hero-panel::after {
  display: none !important;
  content: none !important;
}

.hero-panel h2 {
  color: #163d6a !important;
}

.hero-panel > p {
  color: #64798a !important;
}

.flag-grid {
  position: relative;
  z-index: 2;
  display: grid !important;
  grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
  gap: 10px !important;
}

.flag-item {
  min-width: 0 !important;
  min-height: 74px !important;
  padding: 12px !important;
  display: flex !important;
  align-items: center !important;
  gap: 10px !important;
  overflow: hidden !important;
  border: 1px solid rgba(53, 105, 168, 0.11) !important;
  border-radius: 12px !important;
  background: #f7fbff !important;
}

.flag-item img {
  width: 44px !important;
  min-width: 44px !important;
  max-width: 44px !important;
  height: 30px !important;
  min-height: 30px !important;
  max-height: 30px !important;
  flex: 0 0 44px !important;
  object-fit: contain !important;
  object-position: center !important;
  border-radius: 3px !important;
  background: #ffffff !important;
  transform: none !important;
}

.flag-item > div {
  min-width: 0 !important;
}

.flag-item strong {
  display: block !important;
  overflow-wrap: anywhere;
  color: #163d6a !important;
  font-size: 0.82rem !important;
  line-height: 1.25 !important;
}

.flag-item small {
  display: block !important;
  margin-top: 3px !important;
  overflow-wrap: anywhere;
  color: #64798a !important;
  font-size: 0.67rem !important;
  line-height: 1.3 !important;
}

.globe-symbol {
  width: 44px !important;
  min-width: 44px !important;
  max-width: 44px !important;
  flex: 0 0 44px !important;
  font-size: 1.65rem !important;
  text-align: center !important;
}

/* Numbers should remain useful even before JavaScript animation. */

.trust-item strong {
  min-height: 25px;
}

/* Prevent oversized decorative images inside the hero. */

.hero-panel img {
  transform: none !important;
}

@media (max-width: 680px) {
  .utility-inner {
    justify-content: center !important;
    text-align: center;
  }

  .utility-inner > span {
    display: none;
  }

  .flag-grid {
    grid-template-columns: 1fr !important;
  }
}
'''


def replace_utility_bar(text: str) -> str:
    pattern = re.compile(
        r'<div class="utility-bar">.*?'
        r'<header class="site-header">',
        flags=re.DOTALL,
    )

    return pattern.sub(
        UTILITY_BAR.strip(),
        text,
        count=1,
    )


def add_fixes_stylesheet(text: str) -> str:
    stylesheet = (
        '<link rel="stylesheet" href="/assets/fixes.css">'
    )

    if stylesheet in text:
        return text

    patterns = [
        r'(<link\s+rel="stylesheet"\s+href="/assets/styles\.css"\s*>)',
        r'(<link\s+href="/assets/styles\.css"\s+rel="stylesheet"\s*>)',
    ]

    for pattern in patterns:
        updated, count = re.subn(
            pattern,
            r'\1' + "\n    " + stylesheet,
            text,
            count=1,
            flags=re.DOTALL,
        )

        if count:
            return updated

    raise RuntimeError(
        "Could not find the main stylesheet link."
    )


def remove_svg_hero_images(text: str) -> str:
    pattern = re.compile(
        r'(data-hero-images=")([^"]*)(")'
    )

    def clean(match: re.Match[str]) -> str:
        images = [
            item.strip()
            for item in match.group(2).split("|")
            if item.strip()
        ]

        filtered = [
            item
            for item in images
            if not item.lower().endswith(".svg")
        ]

        if not filtered:
            filtered = images[:1]

        return (
            match.group(1)
            + "|".join(filtered)
            + match.group(3)
        )

    return pattern.sub(clean, text, count=1)


def set_counter_fallback(
    text: str,
    counter: str,
    visible_value: str,
) -> str:
    pattern = re.compile(
        rf'(<strong\b'
        rf'(?=[^>]*data-counter="{re.escape(counter)}")'
        rf'[^>]*>).*?(</strong>)',
        flags=re.DOTALL,
    )

    return pattern.sub(
        lambda match: (
            match.group(1)
            + visible_value
            + match.group(2)
        ),
        text,
        count=1,
    )


# Update all generated HTML pages.

for path in ROOT.glob("*.html"):
    text = path.read_text(encoding="utf-8")

    text = replace_utility_bar(text)
    text = add_fixes_stylesheet(text)

    if path.name == "index.html":
        text = remove_svg_hero_images(text)

        text = set_counter_fallback(
            text,
            "14",
            "14 years",
        )

        text = set_counter_fallback(
            text,
            "3",
            "3 locations",
        )

        text = set_counter_fallback(
            text,
            "5",
            "5+ regions",
        )

    path.write_text(text, encoding="utf-8")
    print(f"Updated {path}")


# Create a final override stylesheet loaded after styles.css.

(ASSETS / "fixes.css").write_text(
    FIXES_CSS.strip() + "\n",
    encoding="utf-8",
)

print("Created assets/fixes.css")


# Prevent SVG route illustrations from entering the hero rotation.

script_path = ASSETS / "script.js"

if script_path.exists():
    script = script_path.read_text(encoding="utf-8")

    old_filter = ".filter(Boolean);"

    new_filter = (
        ".filter(Boolean)\n"
        '      .filter((source) => '
        '!source.toLowerCase().endsWith(".svg"));'
    )

    if old_filter in script and new_filter not in script:
        script = script.replace(
            old_filter,
            new_filter,
            1,
        )

    script_path.write_text(
        script,
        encoding="utf-8",
    )

    print("Updated assets/script.js")


# Also patch the rebuild script so future rebuilds keep these changes.

builder_path = ROOT / "production_rebuild.py"

if builder_path.exists():
    builder = builder_path.read_text(encoding="utf-8")

    builder = replace_utility_bar(builder)

    if "/assets/fixes.css" not in builder:
        builder = re.sub(
            r'(<link\s+rel="stylesheet"\s+'
            r'href="/assets/styles\.css"\s*>)',
            (
                r'\1'
                '\n\n    <link'
                '\n      rel="stylesheet"'
                '\n      href="/assets/fixes.css"'
                '\n    >'
            ),
            builder,
            count=1,
            flags=re.DOTALL,
        )

    if old_filter in builder and new_filter not in builder:
        builder = builder.replace(
            old_filter,
            new_filter,
            1,
        )

    builder_path.write_text(
        builder,
        encoding="utf-8",
    )

    print("Updated production_rebuild.py")


print()
print("Header and hero panel repairs completed.")
