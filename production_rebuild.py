from __future__ import annotations

import json
import shutil
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(".")
ASSETS = ROOT / "assets"
IMAGES = ASSETS / "images"
HERITAGE = ASSETS / "heritage"
FLAGS = ASSETS / "flags"

DOMAIN = "https://ibcglobal.github.io"
EMAIL = "dradilnwaz@gmail.com"

PAKISTAN_PHONE = "+92 333 8057708"
PAKISTAN_PHONE_LINK = "+923338057708"

POLAND_PHONE = "+48 729 296 351"
POLAND_PHONE_LINK = "+48729296351"

IMAGES.mkdir(parents=True, exist_ok=True)
HERITAGE.mkdir(parents=True, exist_ok=True)
FLAGS.mkdir(parents=True, exist_ok=True)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")
    print(f"Wrote: {path}")


def remove_old_files() -> None:
    files_to_remove = [
        ROOT / "registration-status.html",
        ROOT / "contact-backup.html",
        ASSETS / "styles-backup.css",
        ASSETS / "script-backup.js",
        HERITAGE / "international-13.jpg",
        HERITAGE / "international-13.jpeg",
        HERITAGE / "international-13.png",
        HERITAGE / "international-13.webp",
    ]

    for path in files_to_remove:
        if path.exists():
            path.unlink()
            print(f"Removed: {path}")


def optimise_images() -> None:
    for folder in [IMAGES, HERITAGE]:
        if not folder.exists():
            continue

        for source in folder.iterdir():
            if not source.is_file():
                continue

            if source.suffix.lower() not in {
                ".jpg",
                ".jpeg",
                ".png",
            }:
                continue

            if source.stem == "international-13":
                source.unlink(missing_ok=True)
                continue

            destination = source.with_suffix(".webp")

            try:
                with Image.open(source) as image:
                    image = ImageOps.exif_transpose(image)
                    image = image.convert("RGB")
                    image.thumbnail(
                        (1920, 1280),
                        Image.Resampling.LANCZOS,
                    )

                    image.save(
                        destination,
                        format="WEBP",
                        quality=84,
                        method=6,
                    )

                print(
                    f"Optimised: {source.name} -> {destination.name}"
                )

            except Exception as error:
                print(f"Could not optimise {source}: {error}")


def create_social_card() -> None:
    destination = IMAGES / "social-card.jpg"

    width = 1200
    height = 630

    image = Image.new("RGB", (width, height), "#eef5ff")
    draw = ImageDraw.Draw(image)

    for y in range(height):
        ratio = y / max(height - 1, 1)

        start = (247, 251, 255)
        end = (226, 242, 235)

        colour = tuple(
            round(
                start[channel] * (1 - ratio)
                + end[channel] * ratio
            )
            for channel in range(3)
        )

        draw.line((0, y, width, y), fill=colour)

    draw.ellipse(
        (820, -160, 1350, 370),
        fill=(0, 51, 153, 18),
        outline=(0, 51, 153, 28),
        width=3,
    )

    draw.ellipse(
        (-210, 410, 490, 1110),
        fill=(1, 65, 28, 14),
        outline=(1, 65, 28, 22),
        width=3,
    )

    try:
        title_font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            70,
        )

        subtitle_font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            29,
        )

        mark_font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            39,
        )

    except OSError:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        mark_font = ImageFont.load_default()

    draw.rounded_rectangle(
        (78, 70, 188, 180),
        radius=24,
        fill=(0, 51, 153),
    )

    draw.text(
        (98, 95),
        "IBC",
        font=mark_font,
        fill=(255, 255, 255),
    )

    draw.text(
        (78, 250),
        "IndusBaltic",
        font=title_font,
        fill=(0, 38, 84),
    )

    draw.text(
        (78, 350),
        "Education, careers, visas and worldwide travel",
        font=subtitle_font,
        fill=(53, 80, 101),
    )

    draw.text(
        (78, 415),
        "Pakistan · Poland · Europe · International",
        font=subtitle_font,
        fill=(1, 65, 28),
    )

    image.save(
        destination,
        quality=91,
        optimize=True,
    )

    print(f"Created: {destination}")


def relative_web_path(path: Path) -> str:
    return "/" + path.relative_to(ROOT).as_posix()


def find_image(*candidates: str) -> str:
    for candidate in candidates:
        base = ROOT / candidate.lstrip("/")
        stem = base.with_suffix("")

        for suffix in [
            ".webp",
            ".jpg",
            ".jpeg",
            ".png",
            ".svg",
        ]:
            possible = stem.with_suffix(suffix)

            if possible.exists():
                return relative_web_path(possible)

    return "/assets/images/social-card.jpg"


def clean_gallery() -> None:
    gallery_file = HERITAGE / "gallery.json"

    items: list[dict] = []

    if gallery_file.exists():
        try:
            loaded = json.loads(
                gallery_file.read_text(encoding="utf-8")
            )

            if isinstance(loaded, list):
                items = loaded

        except json.JSONDecodeError:
            items = []

    cleaned: list[dict] = []

    for item in items:
        image_value = str(
            item.get("image", "")
        ).lstrip("/")

        if not image_value:
            continue

        image_path = ROOT / image_value

        if image_path.stem == "international-13":
            continue

        webp_path = image_path.with_suffix(".webp")

        if webp_path.exists():
            image_path = webp_path

        if not image_path.exists():
            continue

        filename = image_path.stem.lower()

        title = str(
            item.get("title", "")
        ).strip()

        subtitle = str(
            item.get("subtitle", "")
        ).strip()

        label = str(
            item.get("label", "")
        ).strip()

        group = str(
            item.get("group", "local")
        ).strip()

        if not title:
            title = image_path.stem.replace("-", " ").title()

        if filename.startswith("international-"):
            title = "International education and travel"

            subtitle = (
                "A wider view of the places, institutions and "
                "opportunities our clients ask about."
            )

            label = "International"

            group = "international"

        elif "krakow" in filename or "poland" in filename:
            title = "Kraków and Poland"

            subtitle = (
                "Our European contact point and a practical base "
                "for education and travel enquiries."
            )

            label = "Poland"

            group = "europe"

        elif "bhakkar" in filename:
            title = "Bhakkar"

            subtitle = (
                "A local contact point for students, families "
                "and travellers in District Bhakkar."
            )

            label = "Pakistan"

            group = "local"

        elif "thal" in filename:
            title = "The Thal region"

            subtitle = (
                "The local communities, landscapes and young people "
                "connected with our work."
            )

            label = "Local community"

            group = "local"

        elif "youth" in filename or "student" in filename:
            title = "Students and young people"

            subtitle = (
                "Supporting people as they consider education, "
                "career and international opportunities."
            )

            label = "Education"

            group = "local"

        elif "europe" in filename:
            title = "Europe"

            subtitle = (
                "Study, travel and mobility opportunities across "
                "a wide range of European destinations."
            )

            label = "Europe"

            group = "europe"

        elif "pakistan" in filename:
            title = "Pakistan"

            subtitle = (
                "Local understanding and direct support for "
                "students, families and travellers."
            )

            label = "Pakistan"

            group = "local"

        cleaned.append(
            {
                "title": title,
                "subtitle": subtitle,
                "image": relative_web_path(image_path),
                "alt": str(
                    item.get(
                        "alt",
                        f"{title} photograph",
                    )
                ),
                "group": group,
                "label": label or "IndusBaltic",
            }
        )

    if not cleaned:
        for image_path in sorted(HERITAGE.glob("*")):
            if image_path.suffix.lower() not in {
                ".webp",
                ".jpg",
                ".jpeg",
                ".png",
            }:
                continue

            if image_path.stem == "international-13":
                continue

            filename = image_path.stem.lower()

            if "krakow" in filename or "europe" in filename:
                group = "europe"
            elif "international" in filename:
                group = "international"
            else:
                group = "local"

            title = image_path.stem.replace("-", " ").title()

            cleaned.append(
                {
                    "title": title,
                    "subtitle": (
                        "A selected image connected with "
                        "IndusBaltic's work and services."
                    ),
                    "image": relative_web_path(image_path),
                    "alt": f"{title} photograph",
                    "group": group,
                    "label": "IndusBaltic",
                }
            )

    write(
        gallery_file,
        json.dumps(
            cleaned,
            indent=2,
            ensure_ascii=False,
        ),
    )


remove_old_files()
optimise_images()
create_social_card()
clean_gallery()


students_image = find_image(
    "assets/images/students-campus.jpg",
    "assets/heritage/youth-01.jpg",
    "assets/heritage/thal-youth.jpg",
    "assets/heritage/international-02.jpg",
)

university_image = find_image(
    "assets/images/university-building.jpg",
    "assets/heritage/international-02.jpg",
    "assets/heritage/international-03.jpg",
)

youth_image = find_image(
    "assets/images/youth-guidance.jpg",
    "assets/heritage/youth-01.jpg",
    "assets/heritage/youth-03.jpg",
)

travel_image = find_image(
    "assets/images/global-travel.jpg",
    "assets/images/world-air-routes.svg",
    "assets/heritage/international-02.jpg",
)

world_image = find_image(
    "assets/images/world-air-routes.svg",
    "assets/images/global-travel.jpg",
)

social_image = (
    f"{DOMAIN}/assets/images/social-card.jpg"
)


def canonical(slug: str) -> str:
    if not slug:
        return f"{DOMAIN}/"

    return f"{DOMAIN}/{slug}"


def nav_link(
    label: str,
    href: str,
    active: str,
    key: str,
) -> str:
    if active == key:
        return (
            f'<a class="active" href="{href}">'
            f"{label}</a>"
        )

    return f'<a href="{href}">{label}</a>'


def header(active: str = "") -> str:
    return f"""
    <div class="utility-bar">
      <div class="container utility-inner">
        <span>
          Education, career, visa and worldwide travel guidance
        </span>

        <div class="utility-links">
          <a href="mailto:{EMAIL}">{EMAIL}</a>
          <a href="tel:{PAKISTAN_PHONE_LINK}">
            {PAKISTAN_PHONE}
          </a>
        </div>
      </div>
    </div>

    <header class="site-header">
      <nav
        class="navbar container"
        aria-label="Main navigation"
      >
        <a
          class="brand"
          href="/"
          aria-label="IndusBaltic Consultancy home"
        >
          <span class="brand-mark">IBC</span>

          <span class="brand-copy">
            IndusBaltic
            <small>
              Education & Travel Consultancy
            </small>
          </span>
        </a>

        <button
          class="menu-button"
          type="button"
          aria-label="Open navigation menu"
          aria-expanded="false"
        >
          ☰
        </button>

        <div class="nav-links">
          {nav_link("Home", "/", active, "home")}
          {nav_link(
              "Education",
              "/education.html",
              active,
              "education",
          )}
          {nav_link(
              "Careers",
              "/career.html",
              active,
              "career",
          )}
          {nav_link(
              "Visas",
              "/visas.html",
              active,
              "visas",
          )}
          {nav_link(
              "Travel",
              "/travel.html",
              active,
              "travel",
          )}
          {nav_link(
              "About",
              "/about.html",
              active,
              "about",
          )}

          <a
            class="nav-cta {"active" if active == "contact" else ""}"
            href="/contact.html"
          >
            Contact
          </a>
        </div>
      </nav>
    </header>
    """


def footer() -> str:
    return f"""
    <a
      class="floating-whatsapp"
      href="https://wa.me/{PAKISTAN_PHONE_LINK.lstrip('+')}"
      target="_blank"
      rel="noopener noreferrer"
      aria-label="Contact IndusBaltic on WhatsApp"
    >
      <span aria-hidden="true">💬</span>
      <strong>WhatsApp</strong>
    </a>

    <footer class="site-footer">
      <div class="container footer-grid">
        <div class="footer-brand">
          <a class="brand" href="/">
            <span class="brand-mark">IBC</span>

            <span class="brand-copy footer-brand-copy">
              IndusBaltic
              <small>
                Education & Travel Consultancy
              </small>
            </span>
          </a>

          <p>
            Practical guidance for international education,
            careers, visit visas and worldwide travel.
          </p>
        </div>

        <div>
          <div class="footer-heading">Services</div>

          <div class="footer-links">
            <a href="/education.html">
              Education counselling
            </a>

            <a href="/career.html">
              Career counselling
            </a>

            <a href="/visas.html">
              Visit visa guidance
            </a>

            <a href="/travel.html">
              Worldwide travel
            </a>
          </div>
        </div>

        <div>
          <div class="footer-heading">
            Information
          </div>

          <div class="footer-links">
            <a href="/privacy.html">
              Privacy policy
            </a>

            <a href="/terms.html">
              Terms of service
            </a>

            <a href="/disclaimer.html">
              Service disclaimer
            </a>

            <a href="/refund-policy.html">
              Refund policy
            </a>
          </div>
        </div>

        <div>
          <div class="footer-heading">Contact</div>

          <div class="footer-links">
            <a href="mailto:{EMAIL}">
              {EMAIL}
            </a>

            <a href="tel:{PAKISTAN_PHONE_LINK}">
              {PAKISTAN_PHONE}
            </a>

            <a href="tel:{POLAND_PHONE_LINK}">
              {POLAND_PHONE}
            </a>

            <a href="/contact.html">
              Office locations
            </a>
          </div>
        </div>
      </div>

      <div class="container footer-bottom">
        <span>
          © <span data-year></span>
          IndusBaltic Consultancy.
        </span>

        <span>
          Services are subject to applicable rules
          and third-party conditions.
        </span>
      </div>
    </footer>
    """


def head(
    title: str,
    description: str,
    slug: str,
    structured_data: dict | None = None,
    robots: str = "index, follow",
) -> str:
    canonical_url = canonical(slug)

    json_ld = ""

    if structured_data:
        json_ld = (
            '<script type="application/ld+json">'
            + json.dumps(
                structured_data,
                ensure_ascii=False,
            )
            + "</script>"
        )

    return f"""
    <meta charset="UTF-8">

    <meta
      name="viewport"
      content="width=device-width, initial-scale=1.0"
    >

    <title>{title}</title>

    <meta
      name="description"
      content="{description}"
    >

    <meta name="robots" content="{robots}">
    <meta name="theme-color" content="#f7fbff">

    <link
      rel="canonical"
      href="{canonical_url}"
    >

    <link
      rel="icon"
      href="/assets/favicon.svg"
      type="image/svg+xml"
    >

    <link
      rel="manifest"
      href="/site.webmanifest"
    >

    <meta property="og:type" content="website">

    <meta
      property="og:site_name"
      content="IndusBaltic Consultancy"
    >

    <meta
      property="og:title"
      content="{title}"
    >

    <meta
      property="og:description"
      content="{description}"
    >

    <meta
      property="og:url"
      content="{canonical_url}"
    >

    <meta
      property="og:image"
      content="{social_image}"
    >

    <meta
      name="twitter:card"
      content="summary_large_image"
    >

    <meta
      name="twitter:title"
      content="{title}"
    >

    <meta
      name="twitter:description"
      content="{description}"
    >

    <meta
      name="twitter:image"
      content="{social_image}"
    >

    <link
      rel="stylesheet"
      href="/assets/styles.css"
    >

    <script
      src="/assets/script.js"
      defer
    ></script>

    {json_ld}
    """


def page(
    title: str,
    description: str,
    slug: str,
    active: str,
    content: str,
    structured_data: dict | None = None,
    robots: str = "index, follow",
) -> str:
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      {head(
          title,
          description,
          slug,
          structured_data,
          robots,
      )}
    </head>

    <body>
      {header(active)}

      <main>
        {content}
      </main>

      {footer()}
    </body>
    </html>
    """


def page_hero(
    breadcrumb: str,
    title: str,
    text: str,
    image: str,
) -> str:
    return f"""
    <section
      class="page-hero"
      style="--page-image: url('{image}');"
    >
      <div class="container page-hero-inner">
        <div class="page-hero-card">
          <div class="breadcrumb">
            {breadcrumb}
          </div>

          <h1>{title}</h1>

          <p>{text}</p>
        </div>
      </div>
    </section>
    """


organization_schema = {
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": "IndusBaltic Consultancy",
    "url": f"{DOMAIN}/",
    "email": EMAIL,
    "telephone": PAKISTAN_PHONE_LINK,
    "description": (
        "Education, career, visit visa and worldwide "
        "travel consultancy."
    ),
    "areaServed": [
        "Pakistan",
        "Poland",
        "Europe",
        "United Kingdom",
        "United States",
        "Middle East",
    ],
    "contactPoint": [
        {
            "@type": "ContactPoint",
            "telephone": PAKISTAN_PHONE_LINK,
            "contactType": "customer service",
            "areaServed": "PK",
        },
        {
            "@type": "ContactPoint",
            "telephone": POLAND_PHONE_LINK,
            "contactType": "customer service",
            "areaServed": "PL",
        },
    ],
}


service_cards = """
<div class="service-grid">
  <a
    class="service-card"
    href="/education.html"
  >
    <div class="service-icon">🎓</div>

    <h3>Education counselling</h3>

    <p>
      Compare courses, institutions and destinations
      with clear guidance on documents and next steps.
    </p>

    <span class="card-link">
      Education services
    </span>
  </a>

  <a
    class="service-card"
    href="/career.html"
  >
    <div class="service-icon">🧭</div>

    <h3>Career counselling</h3>

    <p>
      Review your interests, experience and education
      choices before deciding what to do next.
    </p>

    <span class="card-link">
      Career guidance
    </span>
  </a>

  <a
    class="service-card"
    href="/visas.html"
  >
    <div class="service-icon">🛂</div>

    <h3>Visit visa guidance</h3>

    <p>
      Organise travel plans and supporting documents
      with a realistic understanding of the process.
    </p>

    <span class="card-link">
      Visa guidance
    </span>
  </a>

  <a
    class="service-card"
    href="/travel.html"
  >
    <div class="service-icon">✈️</div>

    <h3>Worldwide airline tickets</h3>

    <p>
      Review routes, connections, baggage conditions
      and available ticket options worldwide.
    </p>

    <span class="card-link">
      Travel services
    </span>
  </a>
</div>
"""


home_content = f"""
<section
  class="hero"
  data-hero-images="{students_image}|{university_image}|{youth_image}|{travel_image}"
  style="--hero-image: url('{students_image}');"
>
  <div class="container hero-grid">
    <div class="hero-copy-card">
      <div class="kicker">
        Education · Careers · Visas · Travel
      </div>

      <h1>
        Practical guidance for
        <span>international plans.</span>
      </h1>

      <p class="hero-text">
        IndusBaltic helps students, professionals,
        families and travellers understand their
        options and prepare with confidence.
      </p>

      <div class="actions">
        <a
          class="button button-primary"
          href="/contact.html"
        >
          Book a consultation
        </a>

        <a
          class="button button-secondary"
          href="https://wa.me/{PAKISTAN_PHONE_LINK.lstrip('+')}"
          target="_blank"
          rel="noopener noreferrer"
        >
          WhatsApp
        </a>
      </div>

      <p class="hero-note">
        14 years of relevant experience across
        education, career, visa and travel services.
      </p>
    </div>

    <aside class="hero-panel">
      <h2>International destination focus</h2>

      <p>
        Support shaped around your plans,
        preferred country and personal circumstances.
      </p>

      <div class="flag-grid">
        <div class="flag-item">
          <img
            src="/assets/flags/pk.svg"
            alt="Pakistan flag"
          >

          <div>
            <strong>Pakistan</strong>
            <small>Local consultations</small>
          </div>
        </div>

        <div class="flag-item">
          <img
            src="/assets/flags/pl.svg"
            alt="Poland flag"
          >

          <div>
            <strong>Poland</strong>
            <small>Kraków contact point</small>
          </div>
        </div>

        <div class="flag-item">
          <img
            src="/assets/flags/eu.svg"
            alt="European Union flag"
          >

          <div>
            <strong>Europe</strong>
            <small>Education and travel</small>
          </div>
        </div>

        <div class="flag-item">
          <img
            src="/assets/flags/gb.svg"
            alt="United Kingdom flag"
          >

          <div>
            <strong>United Kingdom</strong>
            <small>Study guidance</small>
          </div>
        </div>

        <div class="flag-item">
          <img
            src="/assets/flags/us.svg"
            alt="United States flag"
          >

          <div>
            <strong>United States</strong>
            <small>Institution guidance</small>
          </div>
        </div>

        <div class="flag-item">
          <span
            class="globe-symbol"
            aria-hidden="true"
          >
            🌍
          </span>

          <div>
            <strong>Worldwide</strong>
            <small>Airline tickets</small>
          </div>
        </div>
      </div>
    </aside>
  </div>
</section>

<div class="trust-strip">
  <div class="container trust-grid">
    <div class="trust-item">
      <strong
        data-counter="14"
        data-suffix=" years"
      >
        0
      </strong>

      <span>Relevant experience</span>
    </div>

    <div class="trust-item">
      <strong
        data-counter="3"
        data-suffix=" locations"
      >
        0
      </strong>

      <span>Listed contact points</span>
    </div>

    <div class="trust-item">
      <strong
        data-counter="5"
        data-suffix="+ regions"
      >
        0
      </strong>

      <span>Destination coverage</span>
    </div>

    <div class="trust-item">
      <strong>Worldwide</strong>
      <span>Airline ticket support</span>
    </div>
  </div>
</div>

<section id="services">
  <div class="container">
    <div class="section-heading">
      <div class="section-label">
        Our services
      </div>

      <h2>
        Straightforward help with important decisions
      </h2>

      <p>
        Each service page explains what we can help
        with, what information is needed and where
        third-party decisions apply.
      </p>
    </div>

    {service_cards}
  </div>
</section>

<section class="section-soft">
  <div class="container split-grid">
    <div class="photo-panel">
      <img
        src="{students_image}"
        alt="Students discussing education options"
        loading="lazy"
      >

      <div class="experience-badge">
        <strong>14 years</strong>

        <span>
          Relevant experience in education,
          career, visa and travel services
        </span>
      </div>
    </div>

    <div class="content-copy">
      <div class="section-label">
        About IndusBaltic
      </div>

      <h2>
        A clear answer is better than a bold promise
      </h2>

      <p>
        International education and travel can feel
        complicated. Our role is to make the process
        easier to understand and help clients prepare
        carefully.
      </p>

      <p>
        We focus on useful information, realistic
        expectations and direct communication.
      </p>

      <div class="check-list">
        <div class="check-item">
          <span class="check">✓</span>

          <span>
            Advice based on individual circumstances
          </span>
        </div>

        <div class="check-item">
          <span class="check">✓</span>

          <span>
            Clear explanations of requirements and risks
          </span>
        </div>

        <div class="check-item">
          <span class="check">✓</span>

          <span>
            Direct contact through Pakistan and Poland
          </span>
        </div>
      </div>

      <div class="actions top-space">
        <a
          class="button button-primary"
          href="/about.html"
        >
          About our work
        </a>
      </div>
    </div>
  </div>
</section>

<section class="destinations-section">
  <div class="container">
    <div class="section-heading">
      <div class="section-label">
        Destination coverage
      </div>

      <h2>
        Guidance for study and travel across major regions
      </h2>

      <p>
        Country requirements differ. We help clients
        compare the practical details before making
        commitments.
      </p>
    </div>

    <div class="destination-grid">
      <article
        class="destination-card"
        style="--flag: url('/assets/flags/pk.svg');"
      >
        <span>Pakistan</span>
        <h3>Local consultation support</h3>
        <p>
          Direct contact for students, families
          and travellers.
        </p>
      </article>

      <article
        class="destination-card"
        style="--flag: url('/assets/flags/pl.svg');"
      >
        <span>Poland</span>
        <h3>Education and travel enquiries</h3>
        <p>
          Support connected with our Kraków contact point.
        </p>
      </article>

      <article
        class="destination-card"
        style="--flag: url('/assets/flags/eu.svg');"
      >
        <span>European Union</span>
        <h3>European study and travel</h3>
        <p>
          Destination research, tours and travel planning.
        </p>
      </article>

      <article
        class="destination-card"
        style="--flag: url('/assets/flags/gb.svg');"
      >
        <span>United Kingdom</span>
        <h3>Study pathway guidance</h3>
        <p>
          Courses, institutions and application preparation.
        </p>
      </article>

      <article
        class="destination-card"
        style="--flag: url('/assets/flags/us.svg');"
      >
        <span>United States</span>
        <h3>Institution guidance</h3>
        <p>
          General course and institution research support.
        </p>
      </article>

      <article class="destination-card world-card">
        <span>Worldwide</span>
        <h3>International airline tickets</h3>
        <p>
          Flight options for destinations around the world.
        </p>
      </article>
    </div>
  </div>
</section>

<section class="section-soft">
  <div class="container global-grid">
    <div class="world-visual">
      <img
        src="{world_image}"
        alt="Worldwide airline route network"
        loading="lazy"
      >
    </div>

    <div class="content-copy">
      <div class="section-label">
        Worldwide airline tickets
      </div>

      <h2>
        Flight options for international destinations
      </h2>

      <p>
        We help clients compare routes, connections,
        baggage conditions and available itineraries
        across Europe, Asia, Africa, the Middle East,
        the Americas and Oceania.
      </p>

      <div class="region-pills">
        <span>Europe</span>
        <span>Middle East</span>
        <span>Asia</span>
        <span>Africa</span>
        <span>North America</span>
        <span>South America</span>
        <span>Oceania</span>
      </div>

      <p class="small-note">
        Routes, fares and schedules remain subject
        to airline availability and applicable
        travel requirements.
      </p>

      <a
        class="button button-primary"
        href="/travel.html"
      >
        View travel services
      </a>
    </div>
  </div>
</section>

<section
  class="heritage-section"
  id="gallery"
>
  <div class="container">
    <div class="gallery-heading">
      <div>
        <div class="section-label">
          People and places
        </div>

        <h2>
          A closer look at the communities and destinations
          connected with our work
        </h2>

        <p>
          Selected photographs from Pakistan, Poland,
          Europe and international education and travel.
        </p>
      </div>

      <div
        class="gallery-filters"
        aria-label="Filter gallery"
      >
        <button
          class="active"
          type="button"
          data-gallery-filter="all"
          aria-pressed="true"
        >
          All
        </button>

        <button
          type="button"
          data-gallery-filter="local"
          aria-pressed="false"
        >
          Pakistan
        </button>

        <button
          type="button"
          data-gallery-filter="europe"
          aria-pressed="false"
        >
          Poland and Europe
        </button>

        <button
          type="button"
          data-gallery-filter="international"
          aria-pressed="false"
        >
          International
        </button>
      </div>
    </div>

    <div
      class="heritage-gallery"
      id="heritageGallery"
      aria-live="polite"
    ></div>
  </div>
</section>

<section class="section-mint">
  <div class="container">
    <div class="section-heading">
      <div class="section-label">
        How it works
      </div>

      <h2>
        A simple consultation process
      </h2>
    </div>

    <div class="steps-grid">
      <article class="step-card">
        <div class="step-number">01</div>
        <h3>Initial discussion</h3>

        <p>
          Tell us what you are planning,
          your background and preferred destination.
        </p>
      </article>

      <article class="step-card">
        <div class="step-number">02</div>
        <h3>Option review</h3>

        <p>
          We review relevant routes, institutions,
          services and practical requirements.
        </p>
      </article>

      <article class="step-card">
        <div class="step-number">03</div>
        <h3>Preparation</h3>

        <p>
          We explain the documents, bookings
          and next steps involved.
        </p>
      </article>

      <article class="step-card">
        <div class="step-number">04</div>
        <h3>Ongoing support</h3>

        <p>
          We remain available as your application
          or travel plan develops.
        </p>
      </article>
    </div>
  </div>
</section>

<section>
  <div class="container">
    <div class="section-heading">
      <div class="section-label">
        Contact points
      </div>

      <h2>
        Speak with our team in Pakistan or Poland
      </h2>
    </div>

    <div class="office-grid">
      <article class="office-card">
        <img
          src="/assets/flags/pl.svg"
          alt="Poland flag"
        >

        <h3>Kraków, Poland</h3>

        <p>
          Radzikowskiego Street,
          Kraków, Poland
        </p>
      </article>

      <article class="office-card">
        <img
          src="/assets/flags/pk.svg"
          alt="Pakistan flag"
        >

        <h3>Bhakkar, Pakistan</h3>

        <p>
          Darya Khan Road,
          Bhakkar, Punjab, Pakistan
        </p>
      </article>

      <article class="office-card">
        <img
          src="/assets/flags/pk.svg"
          alt="Pakistan flag"
        >

        <h3>Hyderabad Thal, Pakistan</h3>

        <p>
          Main Street, People Wali,
          Hyderabad Thal, District Bhakkar,
          Punjab, Pakistan
        </p>
      </article>
    </div>
  </div>
</section>

<section class="cta-band">
  <div class="container cta-grid">
    <div>
      <h2>
        Tell us what you are planning
      </h2>

      <p>
        Start with a direct conversation
        about your study or travel requirements.
      </p>
    </div>

    <a
      class="button button-light"
      href="/contact.html"
    >
      Contact IndusBaltic
    </a>
  </div>
</section>

<div class="notice">
  <div class="container">
    <strong>Important:</strong>
    Admission, visa, employment and travel decisions
    are made by the relevant institutions, authorities
    and service providers. Outcomes cannot be guaranteed.
  </div>
</div>
"""


write(
    ROOT / "index.html",
    page(
        (
            "IndusBaltic Consultancy | "
            "Education, Careers, Visas and Travel"
        ),
        (
            "Education counselling, career guidance, "
            "visit visa support, worldwide airline tickets, "
            "hotel bookings and European travel services."
        ),
        "",
        "home",
        home_content,
        organization_schema,
    ),
)


education_content = f"""
{page_hero(
    "Home / Education",
    "Make a better-informed study decision",
    (
        "Compare courses, institutions and destinations "
        "with practical guidance on requirements, "
        "documents and next steps."
    ),
    university_image,
)}

<section>
  <div class="container content-grid">
    <article class="prose">
      <h2>
        International education counselling
      </h2>

      <p>
        Choosing where and what to study involves more
        than selecting a country. Course content, entry
        requirements, language, finances, location and
        career plans all matter.
      </p>

      <p>
        We help students and families organise these
        questions before making important decisions.
      </p>

      <h3>Our guidance may include</h3>

      <ul>
        <li>
          Student profile and goals review
        </li>

        <li>
          Country and destination comparison
        </li>

        <li>
          Course and institution research
        </li>

        <li>
          General entry requirement review
        </li>

        <li>
          Application document guidance
        </li>

        <li>
          Personal statement preparation guidance
        </li>

        <li>
          General pre-departure planning
        </li>
      </ul>

      <h3>Destination focus</h3>

      <p>
        Our current destination focus includes Poland,
        wider Europe, the United Kingdom, the United
        States and the Middle East.
      </p>

      <div class="info-box">
        <strong>Admission decisions:</strong>
        Educational institutions decide whether an
        applicant is accepted. Admission and scholarship
        outcomes cannot be guaranteed.
      </div>
    </article>

    <aside class="sidebar-card">
      <h3>Discuss your study plans</h3>

      <p>
        Share your education background,
        preferred subject and intended country.
      </p>

      <a
        class="button button-primary"
        href="/contact.html"
      >
        Request education counselling
      </a>
    </aside>
  </div>
</section>

<section class="section-mint">
  <div class="container">
    <div class="section-heading">
      <div class="section-label">
        Student journey
      </div>

      <h2>
        Four practical stages
      </h2>
    </div>

    <div class="steps-grid">
      <article class="step-card">
        <div class="step-number">01</div>
        <h3>Profile review</h3>

        <p>
          Discuss your education,
          interests and intended outcome.
        </p>
      </article>

      <article class="step-card">
        <div class="step-number">02</div>
        <h3>Option research</h3>

        <p>
          Compare relevant destinations,
          institutions and programmes.
        </p>
      </article>

      <article class="step-card">
        <div class="step-number">03</div>
        <h3>Preparation</h3>

        <p>
          Organise the information and documents
          usually required.
        </p>
      </article>

      <article class="step-card">
        <div class="step-number">04</div>
        <h3>Next-step support</h3>

        <p>
          Receive guidance as the application
          process develops.
        </p>
      </article>
    </div>
  </div>
</section>
"""


write(
    ROOT / "education.html",
    page(
        (
            "Education Counselling | "
            "IndusBaltic Consultancy"
        ),
        (
            "Education counselling for Poland, Europe, "
            "the United Kingdom, the United States "
            "and the Middle East."
        ),
        "education.html",
        "education",
        education_content,
    ),
)


career_content = f"""
{page_hero(
    "Home / Careers",
    "Bring more direction to your next step",
    (
        "Career discussions for students, graduates "
        "and professionals considering education, "
        "skills and future opportunities."
    ),
    youth_image,
)}

<section>
  <div class="container content-grid">
    <article class="prose">
      <h2>
        Career guidance with an international perspective
      </h2>

      <p>
        Career planning often involves education choices,
        skills, language, finances, location and personal
        circumstances.
      </p>

      <p>
        We help clients organise these factors and
        identify practical next steps.
      </p>

      <h3>
        Career counselling may cover
      </h3>

      <ul>
        <li>
          Education and experience review
        </li>

        <li>
          Career direction and interests
        </li>

        <li>
          Skills-gap identification
        </li>

        <li>
          Study choices connected to career goals
        </li>

        <li>
          CV and professional profile guidance
        </li>

        <li>
          General interview preparation
        </li>
      </ul>

      <div class="info-box">
        <strong>Career outcomes:</strong>
        Career counselling does not guarantee
        employment, work permits, professional
        licensing or a particular salary.
      </div>
    </article>

    <aside class="sidebar-card">
      <h3>
        Request career counselling
      </h3>

      <p>
        Share your education, work experience
        and intended direction.
      </p>

      <a
        class="button button-primary"
        href="/contact.html"
      >
        Discuss your career
      </a>
    </aside>
  </div>
</section>
"""


write(
    ROOT / "career.html",
    page(
        (
            "Career Counselling | "
            "IndusBaltic Consultancy"
        ),
        (
            "Career counselling for students and "
            "professionals exploring education, "
            "skills and international pathways."
        ),
        "career.html",
        "career",
        career_content,
    ),
)


visas_content = f"""
{page_hero(
    "Home / Visit visas",
    "Prepare your visit visa application carefully",
    (
        "General guidance on documents, application "
        "organisation and travel planning."
    ),
    travel_image,
)}

<section>
  <div class="container content-grid">
    <article class="prose">
      <h2>
        Visit visa preparation support
      </h2>

      <p>
        Visit visa applications may involve identity
        documents, financial evidence, accommodation,
        travel plans and proof of the purpose of travel.
      </p>

      <p>
        Requirements differ by country and may change.
      </p>

      <h3>
        Our general guidance may include
      </h3>

      <ul>
        <li>
          Application requirement review
        </li>

        <li>
          Document checklist guidance
        </li>

        <li>
          Travel itinerary planning
        </li>

        <li>
          Hotel and flight coordination
        </li>

        <li>
          Supporting-document guidance
        </li>

        <li>
          Application-readiness review
        </li>
      </ul>

      <div class="info-box">
        <strong>No visa guarantee:</strong>
        Visa decisions are made by the relevant
        embassy, consulate or immigration authority.
      </div>

      <p>
        Applicants remain responsible for providing
        truthful, complete and authentic information.
        This service is general consultancy support,
        not legal representation.
      </p>
    </article>

    <aside class="sidebar-card">
      <h3>
        Discuss a visit visa plan
      </h3>

      <p>
        Tell us your nationality, destination,
        purpose of travel and intended dates.
      </p>

      <a
        class="button button-primary"
        href="/contact.html"
      >
        Request visa guidance
      </a>
    </aside>
  </div>
</section>
"""


write(
    ROOT / "visas.html",
    page(
        (
            "Visit Visa Guidance | "
            "IndusBaltic Consultancy"
        ),
        (
            "General visit visa documentation "
            "and application preparation guidance."
        ),
        "visas.html",
        "visas",
        visas_content,
    ),
)


travel_content = f"""
{page_hero(
    "Home / Travel",
    "Worldwide airline tickets and travel planning",
    (
        "Flight options, hotel bookings and European "
        "tour planning for individuals, families "
        "and groups."
    ),
    travel_image,
)}

<section>
  <div class="container">
    <div class="section-heading">
      <div class="section-label">
        Travel services
      </div>

      <h2>
        Practical help with international journeys
      </h2>
    </div>

    <div class="service-grid">
      <article class="service-card">
        <div class="service-icon">✈️</div>

        <h3>Worldwide airline tickets</h3>

        <p>
          Compare routes, airlines, connections,
          baggage conditions and available ticket options.
        </p>
      </article>

      <article class="service-card">
        <div class="service-icon">🏨</div>

        <h3>Hotel booking support</h3>

        <p>
          Review accommodation according to destination,
          dates, preferred location and budget.
        </p>
      </article>

      <article class="service-card">
        <div class="service-icon">🚌</div>

        <h3>European tour planning</h3>

        <p>
          Plan practical European itineraries for
          individuals, families and organised groups.
        </p>
      </article>

      <article class="service-card">
        <div class="service-icon">🗺️</div>

        <h3>Custom itineraries</h3>

        <p>
          Organise multi-city and multi-country journeys
          around available time and travel preferences.
        </p>
      </article>
    </div>
  </div>
</section>

<section class="section-soft">
  <div class="container global-grid">
    <div class="world-visual">
      <img
        src="{world_image}"
        alt="Worldwide airline route network"
        loading="lazy"
      >
    </div>

    <div class="content-copy">
      <div class="section-label">
        Global coverage
      </div>

      <h2>
        Travel assistance across every major region
      </h2>

      <p>
        Support is available for routes across Europe,
        Asia, Africa, the Middle East, North America,
        South America and Oceania.
      </p>

      <div class="region-pills">
        <span>Europe</span>
        <span>Middle East</span>
        <span>Asia</span>
        <span>Africa</span>
        <span>Americas</span>
        <span>Oceania</span>
      </div>

      <div class="info-box">
        <strong>Booking conditions:</strong>
        Fares, schedules, baggage allowances,
        cancellation rules and availability are
        controlled by the relevant provider.
      </div>

      <a
        class="button button-primary"
        href="/contact.html"
      >
        Request a travel quote
      </a>
    </div>
  </div>
</section>
"""


write(
    ROOT / "travel.html",
    page(
        (
            "Worldwide Airline Tickets and Travel | "
            "IndusBaltic Consultancy"
        ),
        (
            "Worldwide airline ticket assistance, "
            "hotel bookings and European travel planning."
        ),
        "travel.html",
        "travel",
        travel_content,
    ),
)


about_content = f"""
{page_hero(
    "Home / About",
    "Clear communication and practical support",
    (
        "IndusBaltic provides education, career, "
        "visit visa and travel guidance through "
        "contacts in Pakistan and Poland."
    ),
    students_image,
)}

<section>
  <div class="container split-grid">
    <div class="photo-panel">
      <img
        src="{students_image}"
        alt="Students discussing international opportunities"
        loading="lazy"
      >

      <div class="experience-badge">
        <strong>14 years</strong>

        <span>
          Relevant experience across education,
          career, visa and travel services
        </span>
      </div>
    </div>

    <div class="content-copy">
      <div class="section-label">
        About our work
      </div>

      <h2>
        Helping people make sense of complicated options
      </h2>

      <p>
        International education and travel can involve
        unfamiliar requirements, changing rules and
        important financial decisions.
      </p>

      <p>
        Our aim is to explain the process clearly,
        identify practical options and help clients
        prepare carefully.
      </p>

      <h3>Our working principles</h3>

      <div class="check-list">
        <div class="check-item">
          <span class="check">✓</span>

          <span>
            Direct and respectful communication
          </span>
        </div>

        <div class="check-item">
          <span class="check">✓</span>

          <span>
            Guidance based on individual circumstances
          </span>
        </div>

        <div class="check-item">
          <span class="check">✓</span>

          <span>
            Honest explanations instead of guarantees
          </span>
        </div>

        <div class="check-item">
          <span class="check">✓</span>

          <span>
            Careful handling of client information
          </span>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="section-soft">
  <div class="container">
    <div class="section-heading">
      <div class="section-label">
        Contact points
      </div>

      <h2>
        Pakistan and Poland
      </h2>
    </div>

    <div class="office-grid">
      <article class="office-card">
        <img
          src="/assets/flags/pl.svg"
          alt="Poland flag"
        >

        <h3>Kraków</h3>

        <p>
          Radzikowskiego Street,
          Kraków, Poland
        </p>
      </article>

      <article class="office-card">
        <img
          src="/assets/flags/pk.svg"
          alt="Pakistan flag"
        >

        <h3>Bhakkar</h3>

        <p>
          Darya Khan Road,
          Bhakkar, Punjab, Pakistan
        </p>
      </article>

      <article class="office-card">
        <img
          src="/assets/flags/pk.svg"
          alt="Pakistan flag"
        >

        <h3>Hyderabad Thal</h3>

        <p>
          Main Street, People Wali,
          Hyderabad Thal, District Bhakkar,
          Punjab, Pakistan
        </p>
      </article>
    </div>
  </div>
</section>
"""


write(
    ROOT / "about.html",
    page(
        (
            "About IndusBaltic Consultancy"
        ),
        (
            "Learn about IndusBaltic Consultancy, "
            "its Pakistan and Poland contact points "
            "and 14 years of relevant experience."
        ),
        "about.html",
        "about",
        about_content,
    ),
)


contact_content = f"""
{page_hero(
    "Home / Contact",
    "Speak directly with our team",
    (
        "Send an education, career, visit visa "
        "or travel enquiry by form, email, "
        "telephone or WhatsApp."
    ),
    youth_image,
)}

<section>
  <div class="container contact-grid">
    <aside class="contact-panel">
      <h2>Contact details</h2>

      <p>
        Include your preferred service, intended
        destination and approximate timeframe.
      </p>

      <div class="contact-item">
        <small>Email</small>

        <a href="mailto:{EMAIL}">
          {EMAIL}
        </a>
      </div>

      <div class="contact-item">
        <small>Pakistan telephone</small>

        <a href="tel:{PAKISTAN_PHONE_LINK}">
          {PAKISTAN_PHONE}
        </a>
      </div>

      <div class="contact-item">
        <small>Poland telephone</small>

        <a href="tel:{POLAND_PHONE_LINK}">
          {POLAND_PHONE}
        </a>
      </div>

      <div class="actions top-space">
        <a
          class="button button-primary"
          href="https://wa.me/{PAKISTAN_PHONE_LINK.lstrip('+')}"
          target="_blank"
          rel="noopener noreferrer"
        >
          WhatsApp Pakistan
        </a>

        <a
          class="button button-light"
          href="https://wa.me/{POLAND_PHONE_LINK.lstrip('+')}"
          target="_blank"
          rel="noopener noreferrer"
        >
          WhatsApp Poland
        </a>
      </div>
    </aside>

    <div class="form-card">
      <h2>Send an enquiry</h2>

      <p>
        Completed submissions are sent to
        {EMAIL}.
      </p>

      <form
        action="https://formsubmit.co/{EMAIL}"
        method="POST"
      >
        <input
          type="hidden"
          name="_subject"
          value="New IndusBaltic website enquiry"
        >

        <input
          type="hidden"
          name="_next"
          value="{DOMAIN}/thank-you.html"
        >

        <input
          type="hidden"
          name="_template"
          value="table"
        >

        <input
          class="honeypot"
          type="text"
          name="_honey"
          tabindex="-1"
          autocomplete="off"
        >

        <div class="form-grid">
          <div class="field">
            <label for="name">
              Full name
            </label>

            <input
              id="name"
              name="Full name"
              type="text"
              autocomplete="name"
              required
            >
          </div>

          <div class="field">
            <label for="email">
              Email address
            </label>

            <input
              id="email"
              name="email"
              type="email"
              autocomplete="email"
              required
            >
          </div>

          <div class="field">
            <label for="phone">
              Telephone or WhatsApp
            </label>

            <input
              id="phone"
              name="Telephone or WhatsApp"
              type="tel"
              autocomplete="tel"
              required
            >
          </div>

          <div class="field">
            <label for="country">
              Current country
            </label>

            <input
              id="country"
              name="Current country"
              type="text"
              autocomplete="country-name"
            >
          </div>

          <div class="field">
            <label for="service">
              Service required
            </label>

            <select
              id="service"
              name="Service required"
              required
            >
              <option value="">
                Choose a service
              </option>

              <option>
                Education counselling
              </option>

              <option>
                Career counselling
              </option>

              <option>
                Visit visa guidance
              </option>

              <option>
                Worldwide airline tickets
              </option>

              <option>
                Hotel booking
              </option>

              <option>
                European tour planning
              </option>

              <option>
                Other enquiry
              </option>
            </select>
          </div>

          <div class="field">
            <label for="contact-method">
              Preferred contact method
            </label>

            <select
              id="contact-method"
              name="Preferred contact method"
              required
            >
              <option value="">
                Choose a method
              </option>

              <option>Email</option>
              <option>WhatsApp</option>
              <option>Telephone</option>
            </select>
          </div>

          <div class="field">
            <label for="destination">
              Preferred destination
            </label>

            <input
              id="destination"
              name="Preferred destination"
              type="text"
              placeholder="Country or city"
            >
          </div>

          <div class="field">
            <label for="date">
              Intended study or travel date
            </label>

            <input
              id="date"
              name="Intended date"
              type="month"
            >
          </div>

          <div class="field full">
            <label for="budget">
              Approximate budget range
            </label>

            <select
              id="budget"
              name="Approximate budget range"
            >
              <option value="">
                Prefer not to say
              </option>

              <option>
                Budget not decided
              </option>

              <option>
                Economy or cost-conscious options
              </option>

              <option>
                Mid-range options
              </option>

              <option>
                Flexible budget
              </option>
            </select>
          </div>

          <div class="field full">
            <label for="message">
              Your enquiry
            </label>

            <textarea
              id="message"
              name="Enquiry message"
              placeholder="Tell us about your background, destination and requirements."
              required
            ></textarea>
          </div>

          <div class="field full">
            <label class="consent-label">
              <input
                type="checkbox"
                name="Consent confirmed"
                value="Yes"
                required
              >

              <span>
                I agree that IndusBaltic may use
                these details to respond to my enquiry.
                I have read the
                <a href="/privacy.html">
                  privacy policy
                </a>.
              </span>
            </label>
          </div>

          <div class="field full">
            <button
              class="button button-primary"
              type="submit"
            >
              Send enquiry
            </button>
          </div>
        </div>
      </form>
    </div>
  </div>
</section>

<section class="section-soft">
  <div class="container">
    <div class="section-heading">
      <div class="section-label">
        Contact points
      </div>

      <h2>
        Pakistan and Poland
      </h2>
    </div>

    <div class="office-grid">
      <article class="office-card">
        <img
          src="/assets/flags/pl.svg"
          alt="Poland flag"
        >

        <h3>Kraków, Poland</h3>

        <p>
          Radzikowskiego Street,
          Kraków, Poland
        </p>
      </article>

      <article class="office-card">
        <img
          src="/assets/flags/pk.svg"
          alt="Pakistan flag"
        >

        <h3>Bhakkar, Pakistan</h3>

        <p>
          Darya Khan Road,
          Bhakkar, Punjab, Pakistan
        </p>
      </article>

      <article class="office-card">
        <img
          src="/assets/flags/pk.svg"
          alt="Pakistan flag"
        >

        <h3>Hyderabad Thal, Pakistan</h3>

        <p>
          Main Street, People Wali,
          Hyderabad Thal, District Bhakkar,
          Punjab, Pakistan
        </p>
      </article>
    </div>
  </div>
</section>
"""


write(
    ROOT / "contact.html",
    page(
        (
            "Contact IndusBaltic Consultancy"
        ),
        (
            "Contact IndusBaltic Consultancy in "
            "Pakistan or Poland for education, "
            "career, visa and travel enquiries."
        ),
        "contact.html",
        "contact",
        contact_content,
    ),
)


def legal_content(
    breadcrumb: str,
    heading: str,
    introduction: str,
    sections: list[tuple[str, str]],
) -> str:
    section_html = "\n".join(
        f"""
        <h2>{title}</h2>
        <p>{body}</p>
        """
        for title, body in sections
    )

    return f"""
    {page_hero(
        breadcrumb,
        heading,
        introduction,
        students_image,
    )}

    <section>
      <div class="container legal-layout">
        <article class="legal-card">
          <p class="legal-updated">
            Last updated:
            {date.today().isoformat()}
          </p>

          {section_html}
        </article>
      </div>
    </section>
    """


privacy_content = legal_content(
    "Home / Privacy",
    "Privacy policy",
    (
        "How information submitted through this "
        "website is used and handled."
    ),
    [
        (
            "Information we receive",
            (
                "We may receive information that you "
                "voluntarily submit through the enquiry "
                "form, email, telephone or WhatsApp. "
                "This may include your name, contact "
                "details, destination and enquiry."
            ),
        ),
        (
            "How information is used",
            (
                "Information is used to review and "
                "respond to enquiries, coordinate "
                "requested services and maintain "
                "necessary records."
            ),
        ),
        (
            "Contact form processing",
            (
                "The website form uses FormSubmit to "
                f"transmit enquiries to {EMAIL}. "
                "Form information may therefore be "
                "processed by that service."
            ),
        ),
        (
            "Sensitive information",
            (
                "Do not send passwords, banking "
                "credentials, complete passport scans "
                "or highly sensitive information through "
                "the public website form."
            ),
        ),
        (
            "Contact",
            (
                f"Privacy enquiries may be sent to {EMAIL}."
            ),
        ),
    ],
)


write(
    ROOT / "privacy.html",
    page(
        (
            "Privacy Policy | "
            "IndusBaltic Consultancy"
        ),
        (
            "Privacy information for users of the "
            "IndusBaltic Consultancy website."
        ),
        "privacy.html",
        "",
        privacy_content,
    ),
)


terms_content = legal_content(
    "Home / Terms",
    "Terms of service",
    (
        "General conditions for using this website "
        "and requesting consultancy or travel services."
    ),
    [
        (
            "Website information",
            (
                "Website content is provided for general "
                "information and may change. Current rules, "
                "prices and availability should be verified "
                "before decisions or payments are made."
            ),
        ),
        (
            "Client responsibilities",
            (
                "Clients must provide truthful, complete "
                "and authentic information and remain "
                "responsible for reviewing documents "
                "and meeting official deadlines."
            ),
        ),
        (
            "Third-party decisions",
            (
                "Admissions, visa outcomes, airline "
                "schedules, hotel bookings and government "
                "decisions are controlled by independent "
                "third parties."
            ),
        ),
        (
            "Fees and confirmation",
            (
                "The scope, price and applicable terms "
                "of any paid service should be confirmed "
                "in writing before payment."
            ),
        ),
        (
            "Intellectual property",
            (
                "Website text, design and branding may "
                "not be copied or reused without permission."
            ),
        ),
    ],
)


write(
    ROOT / "terms.html",
    page(
        (
            "Terms of Service | "
            "IndusBaltic Consultancy"
        ),
        (
            "Terms governing use of the IndusBaltic "
            "Consultancy website and services."
        ),
        "terms.html",
        "",
        terms_content,
    ),
)


disclaimer_content = legal_content(
    "Home / Disclaimer",
    "Service disclaimer",
    (
        "Important limitations relating to education, "
        "career, visit visa and travel guidance."
    ),
    [
        (
            "No guaranteed outcomes",
            (
                "IndusBaltic does not guarantee admission, "
                "scholarships, employment, professional "
                "licensing, visa approval, ticket "
                "availability or hotel availability."
            ),
        ),
        (
            "Education information",
            (
                "Programme requirements, fees, deadlines "
                "and admission conditions are controlled "
                "by the relevant institution and may change."
            ),
        ),
        (
            "Visa information",
            (
                "Visa guidance is general preparation "
                "support and is not legal representation. "
                "Applicants should verify requirements "
                "through official sources."
            ),
        ),
        (
            "Travel information",
            (
                "Airline fares, schedules, baggage rules, "
                "cancellation conditions and hotel terms "
                "are controlled by the relevant provider."
            ),
        ),
        (
            "Photography",
            (
                "Some photographs may be illustrative "
                "and should not be interpreted as verified "
                "clients, partner institutions or official "
                "representatives."
            ),
        ),
    ],
)


write(
    ROOT / "disclaimer.html",
    page(
        (
            "Disclaimer | "
            "IndusBaltic Consultancy"
        ),
        (
            "Important limitations relating to "
            "IndusBaltic education, visa and travel services."
        ),
        "disclaimer.html",
        "",
        disclaimer_content,
    ),
)


refund_content = legal_content(
    "Home / Refund policy",
    "Refund and cancellation policy",
    (
        "General principles for consultancy, "
        "airline, hotel and travel-related payments."
    ),
    [
        (
            "Written terms",
            (
                "The exact fee, service scope and "
                "refund conditions should be confirmed "
                "in writing before payment."
            ),
        ),
        (
            "Consultancy work",
            (
                "Fees for completed consultations, "
                "document reviews or work already performed "
                "may be non-refundable, subject to the "
                "written agreement and applicable law."
            ),
        ),
        (
            "Airline tickets",
            (
                "Refunds, changes, no-show penalties "
                "and cancellation charges are determined "
                "by the relevant airline fare rules."
            ),
        ),
        (
            "Hotels and tours",
            (
                "Hotel and tour cancellations are subject "
                "to the provider's terms. Some reservations "
                "may be non-refundable."
            ),
        ),
        (
            "Refund requests",
            (
                f"Requests should be sent to {EMAIL} "
                "with the client's name, service and "
                "payment details."
            ),
        ),
    ],
)


write(
    ROOT / "refund-policy.html",
    page(
        (
            "Refund and Cancellation Policy | "
            "IndusBaltic Consultancy"
        ),
        (
            "General refund and cancellation principles "
            "for consultancy and travel services."
        ),
        "refund-policy.html",
        "",
        refund_content,
    ),
)


thank_you_content = f"""
{page_hero(
    "Home / Enquiry received",
    "Thank you for contacting IndusBaltic",
    (
        "Your enquiry has been submitted. "
        "Our team will review the information "
        "and respond using the details you provided."
    ),
    students_image,
)}

<section>
  <div class="container compact-section">
    <div class="success-card">
      <div class="success-icon">✓</div>

      <h2>
        Your enquiry has been sent
      </h2>

      <p>
        Please check your inbox and spam folder
        for replies from {EMAIL}.
      </p>

      <div class="actions">
        <a
          class="button button-primary"
          href="/"
        >
          Return to homepage
        </a>

        <a
          class="button button-outline"
          href="https://wa.me/{PAKISTAN_PHONE_LINK.lstrip('+')}"
          target="_blank"
          rel="noopener noreferrer"
        >
          WhatsApp
        </a>
      </div>
    </div>
  </div>
</section>
"""


write(
    ROOT / "thank-you.html",
    page(
        (
            "Enquiry Received | "
            "IndusBaltic Consultancy"
        ),
        (
            "Your enquiry has been submitted "
            "to IndusBaltic Consultancy."
        ),
        "thank-you.html",
        "",
        thank_you_content,
        robots="noindex, nofollow",
    ),
)


not_found_content = f"""
<section
  class="page-hero full-error"
  style="--page-image: url('{travel_image}');"
>
  <div class="container page-hero-inner">
    <div class="page-hero-card">
      <div class="error-code">404</div>

      <h1>
        This page could not be found
      </h1>

      <p>
        The address may have changed.
        Return to the homepage or contact us.
      </p>

      <div class="actions top-space">
        <a
          class="button button-primary"
          href="/"
        >
          Return to homepage
        </a>

        <a
          class="button button-secondary"
          href="/contact.html"
        >
          Contact us
        </a>
      </div>
    </div>
  </div>
</section>

<script>
  if (
    window.location.pathname.startsWith(
      "/edu_services"
    )
  ) {{
    window.location.replace("/");
  }}
</script>
"""


write(
    ROOT / "404.html",
    page(
        (
            "Page Not Found | "
            "IndusBaltic Consultancy"
        ),
        (
            "The requested page could not be found."
        ),
        "404.html",
        "",
        not_found_content,
        robots="noindex, nofollow",
    ),
)


write(
    ASSETS / "favicon.svg",
    """
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 128 128"
    >
      <defs>
        <linearGradient
          id="g"
          x1="0"
          y1="0"
          x2="1"
          y2="1"
        >
          <stop
            offset="0"
            stop-color="#3569b8"
          />

          <stop
            offset="1"
            stop-color="#2f7b59"
          />
        </linearGradient>
      </defs>

      <rect
        width="128"
        height="128"
        rx="30"
        fill="url(#g)"
      />

      <text
        x="64"
        y="76"
        text-anchor="middle"
        font-family="Arial, sans-serif"
        font-size="42"
        font-weight="700"
        fill="#ffffff"
      >
        IBC
      </text>
    </svg>
    """,
)


write(
    ROOT / "site.webmanifest",
    json.dumps(
        {
            "name": "IndusBaltic Consultancy",
            "short_name": "IndusBaltic",
            "start_url": "/",
            "display": "standalone",
            "background_color": "#ffffff",
            "theme_color": "#f7fbff",
            "description": (
                "Education, career, visa "
                "and worldwide travel consultancy."
            ),
        },
        indent=2,
    ),
)


sitemap_pages = [
    "",
    "education.html",
    "career.html",
    "visas.html",
    "travel.html",
    "about.html",
    "contact.html",
    "privacy.html",
    "terms.html",
    "disclaimer.html",
    "refund-policy.html",
]

sitemap_urls = "\n".join(
    f"""
    <url>
      <loc>{canonical(slug)}</loc>
      <lastmod>{date.today().isoformat()}</lastmod>
      <changefreq>{
          "weekly" if not slug else "monthly"
      }</changefreq>
      <priority>{
          "1.0" if not slug else "0.7"
      }</priority>
    </url>
    """.strip()
    for slug in sitemap_pages
)


write(
    ROOT / "sitemap.xml",
    f"""
    <?xml version="1.0" encoding="UTF-8"?>

    <urlset
      xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
    >
      {sitemap_urls}
    </urlset>
    """,
)


write(
    ROOT / "robots.txt",
    f"""
    User-agent: *
    Allow: /

    Sitemap: {DOMAIN}/sitemap.xml
    """,
)


redirect_folder = ROOT / "edu_services"
redirect_folder.mkdir(exist_ok=True)


write(
    redirect_folder / "index.html",
    """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">

      <meta
        http-equiv="refresh"
        content="0; url=/"
      >

      <link
        rel="canonical"
        href="https://ibcglobal.github.io/"
      >

      <title>
        Redirecting to IndusBaltic
      </title>
    </head>

    <body>
      <p>
        Redirecting to
        <a href="/">
          IndusBaltic Consultancy
        </a>.
      </p>

      <script>
        window.location.replace("/");
      </script>
    </body>
    </html>
    """,
)


styles = r"""
:root {
  --blue-900: #163d6a;
  --blue-800: #24558d;
  --blue-700: #3569a8;
  --blue-600: #4a7eb9;
  --blue-100: #edf4fb;
  --blue-050: #f7fbff;

  --green-800: #275f46;
  --green-700: #347657;
  --green-600: #4a8b6b;
  --green-100: #edf7f1;

  --white: #ffffff;
  --surface: #f8fafc;
  --text: #243d50;
  --muted: #64798a;
  --border: #dce6ed;

  --shadow-sm:
    0 8px 24px rgba(28, 61, 94, 0.07);

  --shadow-md:
    0 18px 45px rgba(28, 61, 94, 0.11);

  --radius-sm: 12px;
  --radius-md: 18px;
  --radius-lg: 26px;
  --container: 1160px;
}

* {
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
}

body {
  margin: 0;
  color: var(--text);
  background: var(--white);
  font-family:
    Inter,
    ui-sans-serif,
    system-ui,
    -apple-system,
    BlinkMacSystemFont,
    "Segoe UI",
    Arial,
    sans-serif;
  line-height: 1.68;
  overflow-x: hidden;
}

h1,
h2,
h3,
p {
  margin-top: 0;
}

a {
  color: inherit;
  text-decoration: none;
}

img,
svg {
  display: block;
  max-width: 100%;
}

button,
input,
select,
textarea {
  font: inherit;
}

button {
  cursor: pointer;
}

.container {
  width:
    min(
      var(--container),
      calc(100% - 40px)
    );
  margin-inline: auto;
}

.utility-bar {
  color: #eaf3fa;
  background: var(--blue-900);
  font-size: 0.77rem;
}

.utility-inner {
  min-height: 36px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}

.utility-links {
  display: flex;
  align-items: center;
  gap: 18px;
}

.utility-links a:hover {
  color: #ffffff;
}

.site-header {
  position: sticky;
  top: 0;
  z-index: 1000;
  background:
    rgba(255, 255, 255, 0.97);
  border-bottom:
    1px solid rgba(36, 85, 141, 0.09);
  backdrop-filter: blur(13px);
}

.navbar {
  min-height: 76px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 28px;
}

.brand {
  min-width: 220px;
  display: inline-flex;
  align-items: center;
  gap: 12px;
}

.brand-mark {
  width: 46px;
  height: 46px;
  flex: 0 0 46px;
  display: grid;
  place-items: center;
  color: #ffffff;
  border-radius: 14px;
  background:
    linear-gradient(
      145deg,
      var(--blue-700),
      var(--green-600)
    );
  box-shadow:
    0 8px 20px
    rgba(53, 105, 168, 0.2);
  font-size: 0.78rem;
  font-weight: 900;
}

.brand-copy {
  display: flex;
  flex-direction: column;
  color: var(--blue-900);
  font-size: 1.05rem;
  font-weight: 850;
  line-height: 1.05;
}

.brand-copy small {
  margin-top: 5px;
  color: var(--muted);
  font-size: 0.61rem;
  font-weight: 750;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 21px;
  color: #405b70;
  font-size: 0.88rem;
  font-weight: 750;
}

.nav-links a {
  padding: 27px 0 24px;
  border-bottom: 3px solid transparent;
}

.nav-links a:hover,
.nav-links a.active {
  color: var(--blue-800);
  border-color: var(--green-600);
}

.nav-links .nav-cta {
  padding: 11px 17px;
  color: #ffffff;
  border: 0;
  border-radius: 10px;
  background: var(--blue-700);
}

.nav-links .nav-cta:hover,
.nav-links .nav-cta.active {
  color: #ffffff;
  border: 0;
  background: var(--blue-800);
}

.menu-button {
  display: none;
  width: 45px;
  height: 45px;
  border: 0;
  border-radius: 11px;
  color: var(--blue-800);
  background: var(--blue-100);
  font-size: 1.22rem;
}

.hero {
  --hero-image: none;
  position: relative;
  isolation: isolate;
  overflow: hidden;
  background: var(--blue-050);
}

.hero::before {
  content: "";
  position: absolute;
  inset: 0;
  z-index: -2;
  background-image:
    linear-gradient(
      90deg,
      rgba(249, 252, 255, 0.98) 0%,
      rgba(244, 249, 253, 0.91) 46%,
      rgba(238, 247, 242, 0.54) 100%
    ),
    var(--hero-image);
  background-position: center;
  background-size: cover;
  transform: scale(1.02);
  transition:
    opacity 0.45s ease,
    transform 6.5s ease;
}

.hero.hero-changing::before {
  opacity: 0.62;
  transform: scale(1.055);
}

.hero::after {
  content: "";
  position: absolute;
  right: -150px;
  bottom: -270px;
  z-index: -1;
  width: 590px;
  height: 590px;
  border:
    1px solid
    rgba(53, 105, 168, 0.11);
  border-radius: 50%;
  box-shadow:
    0 0 0 65px
      rgba(53, 105, 168, 0.025),
    0 0 0 130px
      rgba(52, 118, 87, 0.02);
}

.hero-grid {
  min-height: 600px;
  padding: 78px 0 104px;
  display: grid;
  grid-template-columns:
    minmax(0, 1.08fr)
    minmax(340px, 0.92fr);
  align-items: center;
  gap: 58px;
}

.hero-copy-card {
  max-width: 720px;
  padding: 35px;
  border:
    1px solid
    rgba(53, 105, 168, 0.11);
  border-radius: 24px;
  background:
    rgba(255, 255, 255, 0.84);
  box-shadow: var(--shadow-md);
  backdrop-filter: blur(9px);
}

.kicker {
  display: inline-flex;
  align-items: center;
  gap: 9px;
  margin-bottom: 19px;
  padding: 8px 13px;
  color: var(--green-800);
  border:
    1px solid
    rgba(52, 118, 87, 0.18);
  border-radius: 999px;
  background: var(--green-100);
  font-size: 0.72rem;
  font-weight: 850;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.kicker::before {
  content: "";
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--green-600);
}

.hero h1 {
  max-width: 760px;
  margin-bottom: 0;
  color: var(--blue-900);
  font-size:
    clamp(
      2.7rem,
      5.5vw,
      4.9rem
    );
  line-height: 1;
  letter-spacing: -0.058em;
}

.hero h1 span {
  color: var(--blue-700);
}

.hero-text {
  max-width: 640px;
  margin: 24px 0 30px;
  color: #50697c;
  font-size: 1.03rem;
}

.hero-note {
  margin: 23px 0 0;
  color: var(--muted);
  font-size: 0.83rem;
}

.hero-panel {
  padding: 28px;
  border:
    1px solid
    rgba(53, 105, 168, 0.13);
  border-radius: 23px;
  background:
    rgba(255, 255, 255, 0.9);
  box-shadow: var(--shadow-md);
  backdrop-filter: blur(10px);
}

.hero-panel h2 {
  margin-bottom: 7px;
  color: var(--blue-900);
  font-size: 1.33rem;
}

.hero-panel > p {
  margin-bottom: 20px;
  color: var(--muted);
  font-size: 0.87rem;
}

.flag-grid {
  display: grid;
  grid-template-columns:
    repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.flag-item {
  min-height: 72px;
  padding: 13px;
  display: flex;
  align-items: center;
  gap: 10px;
  border:
    1px solid
    rgba(53, 105, 168, 0.09);
  border-radius: 13px;
  background: var(--blue-050);
}

.flag-item img {
  width: 42px;
  height: 28px;
  flex: 0 0 42px;
  object-fit: contain;
  border-radius: 3px;
  background: #ffffff;
}

.globe-symbol {
  width: 42px;
  flex: 0 0 42px;
  font-size: 1.7rem;
  text-align: center;
}

.flag-item strong {
  display: block;
  color: var(--blue-900);
  font-size: 0.84rem;
}

.flag-item small {
  display: block;
  margin-top: 2px;
  color: var(--muted);
  font-size: 0.67rem;
  line-height: 1.3;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.top-space {
  margin-top: 27px;
}

.button {
  min-height: 48px;
  padding: 0 19px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid transparent;
  border-radius: 11px;
  font-size: 0.89rem;
  font-weight: 820;
  text-align: center;
  transition:
    transform 0.18s ease,
    background 0.18s ease,
    border-color 0.18s ease;
}

.button:hover {
  transform: translateY(-2px);
}

.button-primary {
  color: #ffffff;
  background: var(--blue-700);
  box-shadow:
    0 10px 22px
    rgba(53, 105, 168, 0.2);
}

.button-primary:hover {
  background: var(--blue-800);
}

.button-secondary {
  color: #ffffff;
  background: var(--green-700);
}

.button-secondary:hover {
  background: var(--green-800);
}

.button-light {
  color: #ffffff;
  border-color:
    rgba(255, 255, 255, 0.35);
  background:
    rgba(255, 255, 255, 0.11);
}

.button-light:hover {
  background:
    rgba(255, 255, 255, 0.18);
}

.button-outline {
  color: var(--blue-800);
  border-color: var(--border);
  background: #ffffff;
}

.button-outline:hover {
  border-color: var(--blue-700);
}

.trust-strip {
  position: relative;
  z-index: 4;
  margin-top: -38px;
}

.trust-grid {
  display: grid;
  grid-template-columns:
    repeat(4, minmax(0, 1fr));
  overflow: hidden;
  border-radius: 18px;
  background: #ffffff;
  box-shadow: var(--shadow-md);
}

.trust-item {
  padding: 23px 17px;
  text-align: center;
  border-right: 1px solid var(--border);
}

.trust-item:last-child {
  border-right: 0;
}

.trust-item strong {
  display: block;
  color: var(--blue-900);
  font-size: 1.38rem;
  line-height: 1.1;
  font-variant-numeric: tabular-nums;
}

.trust-item span {
  display: block;
  margin-top: 5px;
  color: var(--muted);
  font-size: 0.76rem;
}

section {
  padding: 82px 0;
}

.section-soft {
  background: var(--surface);
}

.section-mint {
  background:
    linear-gradient(
      180deg,
      var(--green-100),
      #f8fcfa
    );
}

.section-heading {
  max-width: 735px;
  margin-bottom: 39px;
}

.section-label {
  margin-bottom: 9px;
  color: var(--green-700);
  font-size: 0.72rem;
  font-weight: 850;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.section-heading h2,
.content-copy h2,
.gallery-heading h2 {
  margin-bottom: 0;
  color: var(--blue-900);
  font-size:
    clamp(
      1.95rem,
      4vw,
      3.08rem
    );
  line-height: 1.1;
  letter-spacing: -0.043em;
}

.section-heading p,
.gallery-heading p {
  margin: 14px 0 0;
  color: var(--muted);
}

.service-grid {
  display: grid;
  grid-template-columns:
    repeat(4, minmax(0, 1fr));
  gap: 18px;
}

.service-card {
  position: relative;
  min-height: 286px;
  padding: 26px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: #ffffff;
  transition:
    transform 0.2s ease,
    border-color 0.2s ease,
    box-shadow 0.2s ease;
}

.service-card::before {
  content: "";
  position: absolute;
  top: -70px;
  right: -70px;
  width: 140px;
  height: 140px;
  border-radius: 50%;
  background:
    linear-gradient(
      135deg,
      rgba(53, 105, 168, 0.07),
      rgba(74, 139, 107, 0.09)
    );
}

a.service-card:hover {
  transform: translateY(-5px);
  border-color:
    rgba(53, 105, 168, 0.34);
  box-shadow: var(--shadow-md);
}

.service-icon {
  width: 51px;
  height: 51px;
  margin-bottom: 19px;
  display: grid;
  place-items: center;
  border-radius: 14px;
  background:
    linear-gradient(
      135deg,
      var(--blue-100),
      var(--green-100)
    );
  font-size: 1.34rem;
}

.service-card h3 {
  margin-bottom: 9px;
  color: var(--blue-900);
  font-size: 1.07rem;
  line-height: 1.3;
}

.service-card p {
  margin-bottom: 0;
  color: var(--muted);
  font-size: 0.86rem;
}

.card-link {
  margin-top: auto;
  padding-top: 18px;
  color: var(--blue-700);
  font-size: 0.8rem;
  font-weight: 850;
}

.card-link::after {
  content: " →";
}

.split-grid,
.global-grid {
  display: grid;
  grid-template-columns:
    minmax(0, 0.97fr)
    minmax(0, 1.03fr);
  align-items: center;
  gap: 56px;
}

.photo-panel,
.world-visual {
  position: relative;
}

.photo-panel > img,
.world-visual > img {
  width: 100%;
  min-height: 420px;
  object-fit: cover;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
}

.world-visual > img {
  min-height: auto;
  aspect-ratio: 900 / 560;
  background: var(--blue-900);
}

.experience-badge {
  position: absolute;
  right: 19px;
  bottom: 19px;
  max-width: 220px;
  padding: 20px;
  border-radius: 16px;
  background: #ffffff;
  box-shadow:
    0 16px 38px
    rgba(22, 61, 106, 0.15);
}

.experience-badge strong {
  display: block;
  color: var(--blue-700);
  font-size: 1.65rem;
  line-height: 1.1;
}

.experience-badge span {
  display: block;
  margin-top: 7px;
  color: var(--blue-900);
  font-size: 0.78rem;
  font-weight: 720;
}

.content-copy p {
  margin: 17px 0;
  color: var(--muted);
}

.content-copy h3 {
  margin: 27px 0 10px;
  color: var(--blue-900);
}

.check-list {
  display: grid;
  gap: 12px;
  margin-top: 22px;
}

.check-item {
  display: flex;
  align-items: flex-start;
  gap: 11px;
}

.check {
  width: 24px;
  height: 24px;
  flex: 0 0 24px;
  display: grid;
  place-items: center;
  color: #ffffff;
  border-radius: 50%;
  background: var(--green-700);
  font-size: 0.69rem;
  font-weight: 900;
}

.destinations-section {
  background: #ffffff;
}

.destination-grid {
  display: grid;
  grid-template-columns:
    repeat(3, minmax(0, 1fr));
  gap: 17px;
}

.destination-card {
  --flag: none;
  position: relative;
  min-height: 220px;
  padding: 25px;
  overflow: hidden;
  border: 1px solid var(--border);
  border-radius: 18px;
  background:
    linear-gradient(
      145deg,
      #ffffff,
      var(--blue-050)
    );
  box-shadow: var(--shadow-sm);
}

.destination-card::before {
  content: "";
  position: absolute;
  top: 15px;
  right: 15px;
  width: 125px;
  height: 82px;
  background-image: var(--flag);
  background-position: center;
  background-repeat: no-repeat;
  background-size: contain;
  opacity: 0.11;
  filter: saturate(0.85);
}

.destination-card > * {
  position: relative;
  z-index: 1;
}

.destination-card span {
  display: inline-block;
  margin-bottom: 45px;
  padding: 6px 10px;
  color: var(--green-800);
  border-radius: 999px;
  background: var(--green-100);
  font-size: 0.68rem;
  font-weight: 850;
  letter-spacing: 0.07em;
  text-transform: uppercase;
}

.destination-card h3 {
  margin-bottom: 8px;
  color: var(--blue-900);
  font-size: 1.07rem;
}

.destination-card p {
  margin-bottom: 0;
  color: var(--muted);
  font-size: 0.85rem;
}

.world-card::before {
  content: "🌍";
  display: grid;
  place-items: center;
  background: none;
  font-size: 4.2rem;
  opacity: 0.14;
}

.region-pills {
  margin: 23px 0;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.region-pills span {
  padding: 8px 12px;
  color: var(--blue-800);
  border:
    1px solid
    rgba(53, 105, 168, 0.15);
  border-radius: 999px;
  background: var(--blue-100);
  font-size: 0.74rem;
  font-weight: 800;
}

.region-pills span:nth-child(even) {
  color: var(--green-800);
  border-color:
    rgba(52, 118, 87, 0.15);
  background: var(--green-100);
}

.small-note {
  padding-left: 14px;
  border-left:
    3px solid var(--green-600);
  font-size: 0.83rem;
}

.gallery-heading {
  margin-bottom: 33px;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 35px;
}

.gallery-heading > div:first-child {
  max-width: 760px;
}

.gallery-filters {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

.gallery-filters button {
  padding: 9px 13px;
  color: var(--blue-900);
  border: 1px solid var(--border);
  border-radius: 999px;
  background: #ffffff;
  font-size: 0.74rem;
  font-weight: 800;
}

.gallery-filters button:hover,
.gallery-filters button.active {
  color: #ffffff;
  border-color: var(--blue-700);
  background: var(--blue-700);
}

.heritage-gallery {
  display: grid;
  grid-template-columns:
    repeat(3, minmax(0, 1fr));
  grid-auto-rows: 300px;
  gap: 18px;
}

.heritage-card {
  position: relative;
  overflow: hidden;
  border-radius: 20px;
  background: var(--blue-900);
  box-shadow: var(--shadow-md);
}

.heritage-card.featured {
  grid-column: span 2;
}

.heritage-card img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition:
    transform 0.65s ease,
    filter 0.65s ease;
}

.heritage-card:hover img {
  transform: scale(1.05);
  filter: saturate(1.05);
}

.heritage-overlay {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(
      180deg,
      rgba(22, 61, 106, 0.01) 16%,
      rgba(22, 61, 106, 0.87) 100%
    );
}

.heritage-content {
  position: absolute;
  right: 0;
  bottom: 0;
  left: 0;
  z-index: 2;
  padding: 23px;
  color: #ffffff;
}

.heritage-content span {
  display: inline-block;
  margin-bottom: 7px;
  padding: 5px 9px;
  border-radius: 999px;
  background:
    rgba(52, 118, 87, 0.82);
  font-size: 0.63rem;
  font-weight: 850;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.heritage-content h3 {
  margin-bottom: 7px;
  color: #ffffff;
  font-size: 1.25rem;
}

.heritage-content p {
  margin-bottom: 0;
  color: #e2edf3;
  font-size: 0.8rem;
  line-height: 1.47;
}

.gallery-message {
  grid-column: 1 / -1;
  padding: 24px;
  border: 1px solid var(--border);
  border-radius: 15px;
  background: #ffffff;
}

.steps-grid {
  display: grid;
  grid-template-columns:
    repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.step-card {
  min-height: 205px;
  padding: 25px;
  border:
    1px solid
    rgba(53, 105, 168, 0.07);
  border-radius: 16px;
  background: #ffffff;
}

.step-number {
  margin-bottom: 15px;
  color: var(--blue-700);
  font-size: 1.72rem;
  font-weight: 900;
}

.step-card h3 {
  margin-bottom: 7px;
  color: var(--blue-900);
  font-size: 1.01rem;
}

.step-card p {
  margin-bottom: 0;
  color: var(--muted);
  font-size: 0.83rem;
}

.office-grid {
  display: grid;
  grid-template-columns:
    repeat(3, minmax(0, 1fr));
  gap: 17px;
}

.office-card {
  min-height: 190px;
  padding: 24px;
  border: 1px solid var(--border);
  border-radius: 17px;
  background: #ffffff;
  box-shadow: var(--shadow-sm);
}

.office-card img {
  width: 49px;
  height: 32px;
  margin-bottom: 18px;
  object-fit: contain;
  border:
    1px solid
    rgba(36, 85, 141, 0.12);
  border-radius: 3px;
}

.office-card h3 {
  margin-bottom: 6px;
  color: var(--blue-900);
  font-size: 1.05rem;
}

.office-card p {
  margin-bottom: 0;
  color: var(--muted);
  font-size: 0.85rem;
}

.cta-band {
  padding: 44px 0;
  color: #ffffff;
  background:
    linear-gradient(
      115deg,
      var(--blue-700),
      var(--green-700)
    );
}

.cta-grid {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 29px;
}

.cta-grid h2 {
  margin-bottom: 0;
  color: #ffffff;
  font-size:
    clamp(
      1.7rem,
      3vw,
      2.35rem
    );
  line-height: 1.15;
}

.cta-grid p {
  margin: 6px 0 0;
  color: #e3f0ed;
}

.notice {
  padding: 20px 0;
  color: #4e5e69;
  background: #f3f7fa;
  border-top: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
  font-size: 0.81rem;
}

.page-hero {
  --page-image: none;
  position: relative;
  isolation: isolate;
  overflow: hidden;
  padding: 74px 0 78px;
  background: var(--blue-050);
}

.page-hero::before {
  content: "";
  position: absolute;
  inset: 0;
  z-index: -2;
  background-image:
    linear-gradient(
      90deg,
      rgba(249, 252, 255, 0.98),
      rgba(244, 249, 253, 0.88) 54%,
      rgba(238, 247, 242, 0.46)
    ),
    var(--page-image);
  background-position: center;
  background-size: cover;
}

.page-hero-inner {
  display: flex;
  justify-content: flex-start;
}

.page-hero-card {
  max-width: 850px;
  padding: 31px;
  border:
    1px solid
    rgba(53, 105, 168, 0.11);
  border-radius: 22px;
  background:
    rgba(255, 255, 255, 0.87);
  box-shadow: var(--shadow-md);
  backdrop-filter: blur(8px);
}

.page-hero .breadcrumb {
  margin-bottom: 14px;
  color: var(--green-700);
  font-size: 0.77rem;
  font-weight: 760;
}

.page-hero h1 {
  max-width: 820px;
  margin-bottom: 0;
  color: var(--blue-900);
  font-size:
    clamp(
      2.3rem,
      5vw,
      4.05rem
    );
  line-height: 1.03;
  letter-spacing: -0.05em;
}

.page-hero p {
  max-width: 730px;
  margin: 19px 0 0;
  color: #536a7b;
  font-size: 0.97rem;
}

.content-grid {
  display: grid;
  grid-template-columns:
    minmax(0, 1fr)
    320px;
  align-items: start;
  gap: 46px;
}

.prose h2 {
  margin-bottom: 16px;
  color: var(--blue-900);
  font-size: 1.87rem;
}

.prose h3 {
  margin: 27px 0 9px;
  color: var(--blue-900);
  font-size: 1.12rem;
}

.prose p {
  margin-bottom: 16px;
  color: var(--muted);
}

.prose ul {
  margin: 12px 0 23px;
  padding-left: 21px;
  color: var(--muted);
}

.prose li {
  margin-bottom: 7px;
}

.info-box {
  margin: 25px 0;
  padding: 20px 21px;
  color: #3f5b4d;
  border-left:
    4px solid var(--green-600);
  border-radius: 0 13px 13px 0;
  background: var(--green-100);
}

.sidebar-card {
  position: sticky;
  top: 103px;
  padding: 25px;
  border: 1px solid var(--border);
  border-radius: 18px;
  background: #ffffff;
  box-shadow: var(--shadow-sm);
}

.sidebar-card h3 {
  margin-bottom: 8px;
  color: var(--blue-900);
}

.sidebar-card p {
  margin-bottom: 18px;
  color: var(--muted);
  font-size: 0.85rem;
}

.sidebar-card .button {
  width: 100%;
}

.contact-grid {
  display: grid;
  grid-template-columns:
    minmax(310px, 0.84fr)
    minmax(0, 1.16fr);
  gap: 32px;
}

.contact-panel {
  padding: 31px;
  color: #ffffff;
  border-radius: 22px;
  background:
    linear-gradient(
      145deg,
      var(--blue-800),
      var(--green-700)
    );
}

.contact-panel h2 {
  margin-bottom: 0;
  color: #ffffff;
  font-size: 1.9rem;
}

.contact-panel > p {
  margin: 13px 0 23px;
  color: #e2edf3;
}

.contact-item {
  margin-bottom: 11px;
  padding: 14px;
  border-radius: 11px;
  background:
    rgba(255, 255, 255, 0.11);
}

.contact-item small {
  display: block;
  margin-bottom: 3px;
  color: #d2f1df;
  font-size: 0.65rem;
  font-weight: 850;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.contact-item a {
  overflow-wrap: anywhere;
}

.form-card {
  padding: 31px;
  border: 1px solid var(--border);
  border-radius: 22px;
  background: var(--surface);
}

.form-card h2 {
  margin-bottom: 6px;
  color: var(--blue-900);
  font-size: 1.87rem;
}

.form-card > p {
  margin-bottom: 22px;
  color: var(--muted);
}

.form-grid {
  display: grid;
  grid-template-columns:
    repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.field {
  display: grid;
  gap: 6px;
}

.field.full {
  grid-column: 1 / -1;
}

.field label {
  color: var(--blue-900);
  font-size: 0.79rem;
  font-weight: 800;
}

.field input,
.field select,
.field textarea {
  width: 100%;
  padding: 12px 13px;
  border: 1px solid var(--border);
  border-radius: 10px;
  color: var(--text);
  background: #ffffff;
  outline: none;
}

.field input:focus,
.field select:focus,
.field textarea:focus {
  border-color: var(--blue-600);
  box-shadow:
    0 0 0 3px
    rgba(53, 105, 168, 0.1);
}

.field textarea {
  min-height: 145px;
  resize: vertical;
}

.honeypot {
  position: absolute;
  left: -10000px;
}

.consent-label {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  color: var(--muted);
  font-size: 0.8rem;
  font-weight: 500;
}

.consent-label input {
  width: 18px;
  height: 18px;
  flex: 0 0 18px;
  margin-top: 2px;
  accent-color: var(--green-700);
}

.consent-label a {
  color: var(--blue-700);
  text-decoration: underline;
}

.legal-layout {
  max-width: 900px;
}

.legal-card {
  padding: 35px;
  border: 1px solid var(--border);
  border-radius: 22px;
  background: #ffffff;
  box-shadow: var(--shadow-sm);
}

.legal-card h2 {
  margin: 29px 0 9px;
  color: var(--blue-900);
  font-size: 1.3rem;
}

.legal-card h2:first-of-type {
  margin-top: 13px;
}

.legal-card p {
  color: var(--muted);
}

.legal-updated {
  padding-bottom: 17px;
  border-bottom: 1px solid var(--border);
  font-size: 0.78rem;
}

.compact-section {
  max-width: 760px;
}

.success-card {
  padding: 38px;
  text-align: center;
  border: 1px solid var(--border);
  border-radius: 23px;
  background: #ffffff;
  box-shadow: var(--shadow-md);
}

.success-icon {
  width: 62px;
  height: 62px;
  margin: 0 auto 18px;
  display: grid;
  place-items: center;
  color: #ffffff;
  border-radius: 50%;
  background: var(--green-700);
  font-size: 1.7rem;
  font-weight: 900;
}

.success-card h2 {
  color: var(--blue-900);
}

.success-card p {
  color: var(--muted);
}

.success-card .actions {
  justify-content: center;
  margin-top: 23px;
}

.full-error {
  min-height: 600px;
  display: flex;
  align-items: center;
}

.error-code {
  margin-bottom: 10px;
  color: var(--green-700);
  font-size: 4.3rem;
  font-weight: 900;
  line-height: 1;
}

.floating-whatsapp {
  position: fixed;
  right: 20px;
  bottom: 20px;
  z-index: 900;
  min-height: 52px;
  padding: 0 17px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #ffffff;
  border-radius: 999px;
  background: var(--green-700);
  box-shadow:
    0 13px 31px
    rgba(39, 95, 70, 0.24);
  font-size: 0.81rem;
}

.floating-whatsapp:hover {
  background: var(--green-800);
}

.site-footer {
  padding: 50px 0 27px;
  color: #c4d4df;
  background: #1b3d5d;
  border-top:
    4px solid var(--green-600);
}

.footer-grid {
  display: grid;
  grid-template-columns:
    1.25fr
    0.75fr
    0.8fr
    0.95fr;
  gap: 38px;
}

.footer-brand-copy {
  color: #ffffff;
}

.footer-brand-copy small {
  color: #b7c9d4;
}

.footer-brand p {
  max-width: 430px;
  margin: 15px 0 0;
  font-size: 0.82rem;
}

.footer-heading {
  margin-bottom: 13px;
  color: #ffffff;
  font-size: 0.76rem;
  font-weight: 850;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.footer-links {
  display: grid;
  gap: 8px;
  font-size: 0.81rem;
}

.footer-links a {
  overflow-wrap: anywhere;
}

.footer-links a:hover {
  color: #ffffff;
}

.footer-bottom {
  margin-top: 34px;
  padding-top: 20px;
  display: flex;
  justify-content: space-between;
  gap: 22px;
  border-top:
    1px solid
    rgba(255, 255, 255, 0.11);
  font-size: 0.73rem;
}

.reveal {
  opacity: 0;
  transform: translateY(22px);
  transition:
    opacity 0.6s ease,
    transform 0.6s ease;
}

.reveal.visible {
  opacity: 1;
  transform: translateY(0);
}

a:focus-visible,
button:focus-visible,
input:focus-visible,
select:focus-visible,
textarea:focus-visible {
  outline:
    3px solid
    rgba(53, 105, 168, 0.3);
  outline-offset: 3px;
}

@media (max-width: 1050px) {
  .service-grid {
    grid-template-columns:
      repeat(2, minmax(0, 1fr));
  }

  .footer-grid {
    grid-template-columns:
      repeat(2, minmax(0, 1fr));
  }

  .footer-brand {
    grid-column: 1 / -1;
  }
}

@media (max-width: 980px) {
  .menu-button {
    display: grid;
    place-items: center;
  }

  .nav-links {
    position: absolute;
    top: 76px;
    left: 20px;
    right: 20px;
    display: none;
    padding: 17px;
    align-items: stretch;
    flex-direction: column;
    gap: 3px;
    border: 1px solid var(--border);
    border-radius: 15px;
    background: #ffffff;
    box-shadow: var(--shadow-md);
  }

  .nav-links.open {
    display: flex;
  }

  .nav-links a,
  .nav-links .nav-cta {
    padding: 11px 12px;
    border: 0;
    border-radius: 9px;
  }

  .nav-links a:hover,
  .nav-links a.active {
    border: 0;
    background: var(--blue-100);
  }

  .nav-links .nav-cta:hover,
  .nav-links .nav-cta.active {
    color: #ffffff;
    background: var(--blue-700);
  }

  .hero-grid,
  .split-grid,
  .global-grid,
  .content-grid,
  .contact-grid {
    grid-template-columns: 1fr;
  }

  .hero-panel,
  .sidebar-card {
    max-width: 690px;
  }

  .sidebar-card {
    position: static;
  }

  .destination-grid {
    grid-template-columns:
      repeat(2, minmax(0, 1fr));
  }

  .gallery-heading {
    align-items: flex-start;
    flex-direction: column;
  }

  .gallery-filters {
    justify-content: flex-start;
  }

  .heritage-gallery {
    grid-template-columns:
      repeat(2, minmax(0, 1fr));
  }

  .heritage-card.featured {
    grid-column: span 2;
  }

  .steps-grid {
    grid-template-columns:
      repeat(2, minmax(0, 1fr));
  }

  .office-grid {
    grid-template-columns: 1fr;
  }

  .office-card {
    min-height: auto;
  }
}

@media (max-width: 680px) {
  .container {
    width:
      min(
        var(--container),
        calc(100% - 26px)
      );
  }

  .utility-inner {
    min-height: 34px;
    justify-content: center;
    text-align: center;
  }

  .utility-links {
    display: none;
  }

  .navbar {
    min-height: 70px;
  }

  .brand {
    min-width: 0;
  }

  .brand-mark {
    width: 42px;
    height: 42px;
    flex-basis: 42px;
    font-size: 0.71rem;
  }

  .brand-copy small {
    display: none;
  }

  .nav-links {
    top: 70px;
    left: 13px;
    right: 13px;
  }

  .hero-grid {
    min-height: auto;
    padding: 58px 0 80px;
  }

  .hero-copy-card {
    padding: 25px;
  }

  .hero h1 {
    font-size:
      clamp(
        2.4rem,
        13vw,
        3.55rem
      );
  }

  .hero-text {
    font-size: 0.94rem;
  }

  .hero-panel {
    padding: 22px;
  }

  .flag-grid {
    grid-template-columns: 1fr;
  }

  .trust-strip {
    margin-top: -25px;
  }

  .trust-grid {
    grid-template-columns:
      repeat(2, minmax(0, 1fr));
  }

  .trust-item:nth-child(2) {
    border-right: 0;
  }

  .trust-item:nth-child(-n + 2) {
    border-bottom:
      1px solid var(--border);
  }

  section {
    padding: 64px 0;
  }

  .page-hero {
    padding: 58px 0 62px;
  }

  .page-hero-card {
    padding: 24px;
  }

  .page-hero h1 {
    font-size:
      clamp(
        2.1rem,
        12vw,
        3.2rem
      );
  }

  .service-grid,
  .destination-grid,
  .heritage-gallery,
  .steps-grid,
  .form-grid,
  .footer-grid {
    grid-template-columns: 1fr;
  }

  .service-card {
    min-height: 0;
  }

  .heritage-card.featured {
    grid-column: auto;
  }

  .heritage-gallery {
    grid-auto-rows: 290px;
  }

  .field.full {
    grid-column: auto;
  }

  .photo-panel > img {
    min-height: 350px;
  }

  .cta-grid,
  .footer-bottom {
    align-items: flex-start;
    flex-direction: column;
  }

  .cta-grid .button {
    width: 100%;
  }

  .contact-panel,
  .form-card,
  .legal-card {
    padding: 23px;
  }

  .floating-whatsapp {
    right: 13px;
    bottom: 13px;
    width: 52px;
    padding: 0;
    justify-content: center;
  }

  .floating-whatsapp strong {
    display: none;
  }

  .footer-brand {
    grid-column: auto;
  }
}

@media (
  prefers-reduced-motion: reduce
) {
  html {
    scroll-behavior: auto;
  }

  .hero::before,
  .service-card,
  .heritage-card img,
  .reveal {
    transition: none;
  }

  .reveal {
    opacity: 1;
    transform: none;
  }
}
"""


write(
    ASSETS / "styles.css",
    styles,
)


script = r"""
(() => {
  const reducedMotion =
    window.matchMedia(
      "(prefers-reduced-motion: reduce)"
    ).matches;

  const menuButton =
    document.querySelector(".menu-button");

  const navLinks =
    document.querySelector(".nav-links");

  if (menuButton && navLinks) {
    menuButton.addEventListener(
      "click",
      () => {
        const open =
          navLinks.classList.toggle("open");

        menuButton.setAttribute(
          "aria-expanded",
          String(open)
        );

        menuButton.textContent =
          open ? "✕" : "☰";
      }
    );

    navLinks
      .querySelectorAll("a")
      .forEach((link) => {
        link.addEventListener(
          "click",
          () => {
            navLinks.classList.remove("open");

            menuButton.setAttribute(
              "aria-expanded",
              "false"
            );

            menuButton.textContent = "☰";
          }
        );
      });
  }

  document
    .querySelectorAll("[data-year]")
    .forEach((element) => {
      element.textContent =
        new Date().getFullYear();
    });

  const hero =
    document.querySelector(
      ".hero[data-hero-images]"
    );

  if (hero) {
    const images =
      hero.dataset.heroImages
        .split("|")
        .map((item) => item.trim())
        .filter(Boolean);

    let currentIndex = 0;

    const setHeroImage = (source) => {
      hero.style.setProperty(
        "--hero-image",
        `url("${source}")`
      );
    };

    images.forEach((source) => {
      const image = new Image();
      image.src = source;
    });

    if (images.length > 0) {
      setHeroImage(images[0]);
    }

    if (
      images.length > 1
      && !reducedMotion
    ) {
      window.setInterval(
        () => {
          hero.classList.add(
            "hero-changing"
          );

          window.setTimeout(
            () => {
              currentIndex =
                (currentIndex + 1)
                % images.length;

              setHeroImage(
                images[currentIndex]
              );

              hero.classList.remove(
                "hero-changing"
              );
            },
            420
          );
        },
        6800
      );
    }
  }

  const counters =
    document.querySelectorAll(
      "[data-counter]"
    );

  const animateCounter = (element) => {
    const target =
      Number(
        element.dataset.counter || "0"
      );

    const suffix =
      element.dataset.suffix || "";

    const duration = 1100;
    const start = performance.now();

    const update = (time) => {
      const progress =
        Math.min(
          (time - start) / duration,
          1
        );

      const eased =
        1 - Math.pow(1 - progress, 3);

      element.textContent =
        `${Math.round(target * eased)}${suffix}`;

      if (progress < 1) {
        requestAnimationFrame(update);
      }
    };

    requestAnimationFrame(update);
  };

  if (
    counters.length
    && "IntersectionObserver" in window
    && !reducedMotion
  ) {
    const observer =
      new IntersectionObserver(
        (entries, activeObserver) => {
          entries.forEach((entry) => {
            if (!entry.isIntersecting) {
              return;
            }

            animateCounter(entry.target);

            activeObserver.unobserve(
              entry.target
            );
          });
        },
        {
          threshold: 0.65,
        }
      );

    counters.forEach((counter) => {
      observer.observe(counter);
    });

  } else {
    counters.forEach((counter) => {
      counter.textContent =
        `${counter.dataset.counter}`
        + `${counter.dataset.suffix || ""}`;
    });
  }

  const revealElements =
    document.querySelectorAll(
      [
        ".service-card",
        ".destination-card",
        ".step-card",
        ".office-card",
        ".photo-panel",
        ".world-visual",
        ".content-copy",
        ".sidebar-card",
        ".form-card",
        ".legal-card",
      ].join(",")
    );

  revealElements.forEach((element) => {
    element.classList.add("reveal");
  });

  if (
    revealElements.length
    && "IntersectionObserver" in window
    && !reducedMotion
  ) {
    const revealObserver =
      new IntersectionObserver(
        (entries, activeObserver) => {
          entries.forEach((entry) => {
            if (!entry.isIntersecting) {
              return;
            }

            entry.target.classList.add(
              "visible"
            );

            activeObserver.unobserve(
              entry.target
            );
          });
        },
        {
          threshold: 0.12,
        }
      );

    revealElements.forEach((element) => {
      revealObserver.observe(element);
    });

  } else {
    revealElements.forEach((element) => {
      element.classList.add("visible");
    });
  }

  const gallery =
    document.querySelector(
      "#heritageGallery"
    );

  const filterButtons =
    document.querySelectorAll(
      "[data-gallery-filter]"
    );

  let galleryItems = [];

  const escapeHtml = (value) =>
    String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");

  const normaliseImagePath = (value) => {
    const text = String(value || "");

    if (!text) {
      return "";
    }

    return text.startsWith("/")
      ? text
      : `/${text}`;
  };

  const renderGallery = (
    filter = "all"
  ) => {
    if (!gallery) {
      return;
    }

    const visibleItems =
      filter === "all"
        ? galleryItems
        : galleryItems.filter(
            (item) =>
              item.group === filter
          );

    if (!visibleItems.length) {
      gallery.innerHTML = `
        <div class="gallery-message">
          No photographs are currently
          available in this category.
        </div>
      `;

      return;
    }

    gallery.innerHTML =
      visibleItems
        .map(
          (item, index) => `
            <article
              class="heritage-card ${
                index === 0
                  ? "featured"
                  : ""
              }"
            >
              <img
                src="${escapeHtml(
                  normaliseImagePath(
                    item.image
                  )
                )}"
                alt="${escapeHtml(
                  item.alt
                  || item.title
                  || "Gallery photograph"
                )}"
                loading="lazy"
              >

              <div
                class="heritage-overlay"
              ></div>

              <div
                class="heritage-content"
              >
                <span>
                  ${escapeHtml(
                    item.label
                    || "IndusBaltic"
                  )}
                </span>

                <h3>
                  ${escapeHtml(
                    item.title
                    || "International opportunity"
                  )}
                </h3>

                <p>
                  ${escapeHtml(
                    item.subtitle
                    || ""
                  )}
                </p>
              </div>
            </article>
          `
        )
        .join("");
  };

  if (gallery) {
    fetch(
      "/assets/heritage/gallery.json",
      {
        cache: "no-store",
      }
    )
      .then((response) => {
        if (!response.ok) {
          throw new Error(
            `Gallery request failed: ${
              response.status
            }`
          );
        }

        return response.json();
      })
      .then((items) => {
        galleryItems =
          Array.isArray(items)
            ? items
            : [];

        renderGallery();
      })
      .catch((error) => {
        console.error(error);

        gallery.innerHTML = `
          <div class="gallery-message">
            The photo gallery could not
            be loaded.
          </div>
        `;
      });
  }

  filterButtons.forEach((button) => {
    button.addEventListener(
      "click",
      () => {
        filterButtons.forEach((item) => {
          item.classList.remove("active");

          item.setAttribute(
            "aria-pressed",
            "false"
          );
        });

        button.classList.add("active");

        button.setAttribute(
          "aria-pressed",
          "true"
        );

        renderGallery(
          button.dataset.galleryFilter
          || "all"
        );
      }
    );
  });
})();
"""


write(
    ASSETS / "script.js",
    script,
)


print()
print(
    "Production rebuild completed successfully."
)
