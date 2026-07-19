from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from urllib.parse import quote


ROOT = Path(".")
ASSETS = ROOT / "assets"
HERITAGE = ASSETS / "heritage"
BACKUP = ROOT / "_backup_before_ceo_profile"

BACKUP.mkdir(exist_ok=True)


def backup(path: Path) -> None:
    if not path.exists():
        return

    destination = BACKUP / path.name
    shutil.copy2(path, destination)
    print(f"Backed up: {path}")


def replace_or_insert(
    text: str,
    start_marker: str,
    end_marker: str,
    replacement: str,
    insertion_marker: str,
) -> str:
    pattern = re.compile(
        re.escape(start_marker)
        + r".*?"
        + re.escape(end_marker),
        flags=re.DOTALL,
    )

    replacement = replacement.strip()

    if pattern.search(text):
        return pattern.sub(replacement, text, count=1)

    if insertion_marker not in text:
        raise RuntimeError(
            f"Could not find insertion marker: {insertion_marker}"
        )

    return text.replace(
        insertion_marker,
        replacement + "\n\n" + insertion_marker,
        1,
    )


def update_anchor(
    path: Path,
    visible_text: str,
    destination: str,
) -> None:
    text = path.read_text(encoding="utf-8")

    anchor_pattern = re.compile(
        r'<a\b(?P<attributes>[^>]*)>'
        r'(?P<body>.*?)'
        r'</a>',
        flags=re.DOTALL | re.IGNORECASE,
    )

    changed = False

    def replace_anchor(match: re.Match[str]) -> str:
        nonlocal changed

        body_text = re.sub(
            r"<[^>]+>",
            "",
            match.group("body"),
        )

        body_text = " ".join(body_text.split())

        if visible_text.lower() not in body_text.lower():
            return match.group(0)

        attributes = match.group("attributes")

        if re.search(r'\bhref="[^"]*"', attributes):
            attributes = re.sub(
                r'\bhref="[^"]*"',
                f'href="{destination}"',
                attributes,
                count=1,
            )
        else:
            attributes += f' href="{destination}"'

        changed = True

        return (
            f"<a{attributes}>"
            f"{match.group('body')}"
            f"</a>"
        )

    updated = anchor_pattern.sub(replace_anchor, text)

    if changed:
        path.write_text(updated, encoding="utf-8")
        print(f"Updated enquiry link in: {path}")
    else:
        print(
            f"Notice: button text not found in {path}: "
            f"{visible_text}"
        )


for path in [
    ROOT / "index.html",
    ROOT / "about.html",
    ROOT / "education.html",
    ROOT / "career.html",
    ROOT / "visas.html",
    ROOT / "travel.html",
    ROOT / "contact.html",
    ASSETS / "styles.css",
    ASSETS / "script.js",
    HERITAGE / "gallery.json",
]:
    backup(path)


# Remove the previously selected photograph in every supported format.

for suffix in [".jpg", ".jpeg", ".png", ".webp"]:
    path = HERITAGE / f"international-13{suffix}"

    if path.exists():
        path.unlink()
        print(f"Removed: {path}")


home_ceo_section = '''
<!-- BEGIN IBC FOUNDER NOTE -->
<section class="founder-note-section">
  <div class="container founder-note-grid">
    <div class="founder-note-label">
      <span class="founder-mark">CEO</span>

      <div>
        <small>Founder’s perspective</small>
        <strong>Why IndusBaltic exists</strong>
      </div>
    </div>

    <div class="founder-note-copy">
      <blockquote>
        “I know what it feels like to have ambition but no clear roadmap.
        That experience continues to shape the way we guide every client.”
      </blockquote>

      <p>
        Growing up in the desert region of Thal, access to information,
        opportunities and experienced guidance was limited. Reaching higher
        education required determination, patience and a willingness to keep
        looking for a path forward.
      </p>

      <a class="text-link" href="/about.html#founder-message">
        Read the Founder & CEO message
      </a>
    </div>
  </div>
</section>
<!-- END IBC FOUNDER NOTE -->
'''


about_ceo_section = '''
<!-- BEGIN IBC CEO MESSAGE -->
<section class="ceo-message-section" id="founder-message">
  <div class="container ceo-message-grid">
    <aside class="ceo-profile-card">
      <div class="ceo-profile-mark">CEO</div>

      <div class="section-label">
        Founder & CEO
      </div>

      <h2>A personal message</h2>

      <p class="ceo-profile-role">
        IndusBaltic Consultancy
      </p>

      <div class="ceo-profile-line"></div>

      <p>
        Education, career, visit visa and international travel guidance.
      </p>
    </aside>

    <article class="ceo-message-copy">
      <div class="quote-mark" aria-hidden="true">“</div>

      <h2>
        I began with determination, not a roadmap
      </h2>

      <p>
        I grew up in the desert region of Thal, where opportunities were not
        always easy to see and reliable guidance was difficult to find. I had
        ambition and a strong desire to continue my education, but I did not
        have someone who could clearly explain the journey ahead.
      </p>

      <p>
        Reaching higher education required persistence. There were difficult
        moments, limited resources and many questions, but the desire to learn
        kept me moving forward. That determination later gave me the
        opportunity to travel abroad through a UNESCO fellowship.
      </p>

      <p>
        My professional journey also brought experience in large technology
        and corporate environments. Those years taught me the importance of
        preparation, communication, responsibility and making decisions with
        reliable information.
      </p>

      <p>
        IndusBaltic was created from a simple belief: capable people should not
        be held back because they lack clear information or someone willing to
        guide them honestly. Our purpose is to offer the kind of practical
        support I once needed myself.
      </p>

      <p>
        We cannot promise outcomes that are controlled by universities,
        authorities, employers, airlines or other organisations. What we can
        promise is that we will listen carefully, explain the available
        options and treat each client’s plans with respect.
      </p>

      <footer class="ceo-signature">
        <strong>Founder & CEO</strong>
        <span>IndusBaltic Consultancy</span>
      </footer>
    </article>
  </div>
</section>
<!-- END IBC CEO MESSAGE -->
'''


index_path = ROOT / "index.html"
index = index_path.read_text(encoding="utf-8")

index = replace_or_insert(
    index,
    "<!-- BEGIN IBC FOUNDER NOTE -->",
    "<!-- END IBC FOUNDER NOTE -->",
    home_ceo_section,
    '<section class="destinations-section">',
)

index_path.write_text(index, encoding="utf-8")
print("Added Founder note to index.html")


about_path = ROOT / "about.html"
about = about_path.read_text(encoding="utf-8")

about = replace_or_insert(
    about,
    "<!-- BEGIN IBC CEO MESSAGE -->",
    "<!-- END IBC CEO MESSAGE -->",
    about_ceo_section,
    '<section class="section-soft">',
)

about_path.write_text(about, encoding="utf-8")
print("Added CEO message to about.html")


# Add service-specific enquiry URLs.

service_links = [
    (
        ROOT / "education.html",
        "Request education counselling",
        "Education counselling",
    ),
    (
        ROOT / "career.html",
        "Discuss your career",
        "Career counselling",
    ),
    (
        ROOT / "visas.html",
        "Request visa guidance",
        "Visit visa guidance",
    ),
    (
        ROOT / "travel.html",
        "Request a travel quote",
        "Worldwide airline tickets",
    ),
]

for page_path, button_text, service_name in service_links:
    destination = (
        "/contact.html?service="
        + quote(service_name, safe="")
    )

    update_anchor(
        page_path,
        button_text,
        destination,
    )


# Rewrite gallery captions in a more natural and cautious style.

gallery_path = HERITAGE / "gallery.json"

if gallery_path.exists():
    try:
        gallery_items = json.loads(
            gallery_path.read_text(encoding="utf-8")
        )
    except json.JSONDecodeError as error:
        raise RuntimeError(
            f"gallery.json is not valid JSON: {error}"
        ) from error

    cleaned_items = []

    for item in gallery_items:
        image_value = str(
            item.get("image", "")
        ).lower()

        if "international-13" in image_value:
            continue

        filename = Path(image_value).stem.lower()

        if "krakow" in filename or "poland" in filename:
            item["title"] = "Kraków and Poland"
            item["subtitle"] = (
                "A view connected with our Poland contact point "
                "and European enquiries."
            )
            item["label"] = "Poland"
            item["group"] = "europe"

        elif "bhakkar" in filename:
            item["title"] = "District Bhakkar"
            item["subtitle"] = (
                "A view from the district where our Pakistan "
                "contact points are based."
            )
            item["label"] = "Pakistan"
            item["group"] = "local"

        elif "thal" in filename and "youth" not in filename:
            item["title"] = "The Thal region"
            item["subtitle"] = (
                "A view of the landscape and community "
                "connected with our local work."
            )
            item["label"] = "Local community"
            item["group"] = "local"

        elif any(
            word in filename
            for word in [
                "youth",
                "young",
                "student",
                "people",
            ]
        ):
            item["title"] = "Students and young people"
            item["subtitle"] = (
                "Young people considering education, careers "
                "and future opportunities."
            )
            item["label"] = "Education"
            item["group"] = "local"

        elif "pakistan" in filename:
            item["title"] = "Pakistan"
            item["subtitle"] = (
                "A glimpse of the communities and places "
                "connected with our work."
            )
            item["label"] = "Pakistan"
            item["group"] = "local"

        elif "europe" in filename:
            item["title"] = "Europe"
            item["subtitle"] = (
                "A European setting connected with international "
                "education and travel planning."
            )
            item["label"] = "Europe"
            item["group"] = "europe"

        elif "international" in filename:
            item["title"] = "International education and travel"
            item["subtitle"] = (
                "An international setting connected with "
                "education or travel planning."
            )
            item["label"] = "International"
            item["group"] = "international"

        cleaned_items.append(item)

    gallery_path.write_text(
        json.dumps(
            cleaned_items,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    print("Updated gallery captions")


ceo_css = r'''
/* BEGIN IBC CEO PROFILE UPGRADE */

.founder-note-section {
  padding: 70px 0;
  background:
    linear-gradient(
      135deg,
      #f8fbfe,
      #eef7f2
    );
  border-top: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
}

.founder-note-grid {
  display: grid;
  grid-template-columns: minmax(250px, 0.72fr) minmax(0, 1.28fr);
  align-items: center;
  gap: 54px;
}

.founder-note-label {
  display: flex;
  align-items: center;
  gap: 17px;
}

.founder-mark {
  width: 76px;
  height: 76px;
  flex: 0 0 76px;
  display: grid;
  place-items: center;
  color: #ffffff;
  border-radius: 22px;
  background:
    linear-gradient(
      145deg,
      var(--blue-700),
      var(--green-600)
    );
  box-shadow:
    0 14px 30px
    rgba(53, 105, 168, 0.19);
  font-size: 1rem;
  font-weight: 900;
  letter-spacing: 0.05em;
}

.founder-note-label small {
  display: block;
  margin-bottom: 5px;
  color: var(--green-700);
  font-size: 0.7rem;
  font-weight: 850;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.founder-note-label strong {
  display: block;
  color: var(--blue-900);
  font-size: 1.35rem;
  line-height: 1.25;
}

.founder-note-copy blockquote {
  margin: 0 0 17px;
  color: var(--blue-900);
  font-size: clamp(1.35rem, 2.6vw, 2rem);
  font-weight: 750;
  line-height: 1.35;
  letter-spacing: -0.025em;
}

.founder-note-copy p {
  margin-bottom: 16px;
  color: var(--muted);
}

.text-link {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  color: var(--blue-700);
  font-size: 0.85rem;
  font-weight: 850;
}

.text-link::after {
  content: "→";
}

.text-link:hover {
  color: var(--green-700);
}

.ceo-message-section {
  padding: 84px 0;
  background: #ffffff;
}

.ceo-message-grid {
  display: grid;
  grid-template-columns: minmax(250px, 0.72fr) minmax(0, 1.28fr);
  align-items: start;
  gap: 52px;
}

.ceo-profile-card {
  position: sticky;
  top: 110px;
  padding: 30px;
  overflow: hidden;
  border: 1px solid var(--border);
  border-radius: 23px;
  background:
    linear-gradient(
      155deg,
      #f7fbff,
      #edf7f1
    );
  box-shadow: var(--shadow-sm);
}

.ceo-profile-card::after {
  content: "";
  position: absolute;
  right: -65px;
  bottom: -75px;
  width: 180px;
  height: 180px;
  border: 1px solid rgba(53, 105, 168, 0.12);
  border-radius: 50%;
  box-shadow:
    0 0 0 35px rgba(53, 105, 168, 0.025),
    0 0 0 70px rgba(52, 118, 87, 0.018);
}

.ceo-profile-card > * {
  position: relative;
  z-index: 1;
}

.ceo-profile-mark {
  width: 78px;
  height: 78px;
  margin-bottom: 25px;
  display: grid;
  place-items: center;
  color: #ffffff;
  border-radius: 23px;
  background:
    linear-gradient(
      145deg,
      var(--blue-700),
      var(--green-600)
    );
  font-size: 1.05rem;
  font-weight: 900;
}

.ceo-profile-card h2 {
  margin-bottom: 5px;
  color: var(--blue-900);
  font-size: 1.75rem;
  line-height: 1.18;
}

.ceo-profile-role {
  margin-bottom: 0;
  color: var(--green-700);
  font-size: 0.84rem;
  font-weight: 800;
}

.ceo-profile-line {
  width: 52px;
  height: 3px;
  margin: 24px 0;
  border-radius: 999px;
  background: var(--green-600);
}

.ceo-profile-card > p:last-child {
  margin-bottom: 0;
  color: var(--muted);
  font-size: 0.86rem;
}

.ceo-message-copy {
  position: relative;
  padding: 40px;
  border: 1px solid var(--border);
  border-radius: 25px;
  background: #ffffff;
  box-shadow: var(--shadow-sm);
}

.quote-mark {
  position: absolute;
  top: 14px;
  right: 30px;
  color: rgba(53, 105, 168, 0.09);
  font-family: Georgia, serif;
  font-size: 7rem;
  line-height: 1;
}

.ceo-message-copy h2 {
  position: relative;
  max-width: 680px;
  margin-bottom: 24px;
  color: var(--blue-900);
  font-size: clamp(2rem, 4vw, 3rem);
  line-height: 1.12;
  letter-spacing: -0.04em;
}

.ceo-message-copy p {
  position: relative;
  margin-bottom: 18px;
  color: var(--muted);
  font-size: 0.98rem;
}

.ceo-message-copy p:first-of-type::first-letter {
  float: left;
  margin: 8px 8px 0 0;
  color: var(--blue-700);
  font-family: Georgia, serif;
  font-size: 3.8rem;
  line-height: 0.75;
}

.ceo-signature {
  margin-top: 31px;
  padding-top: 22px;
  display: flex;
  flex-direction: column;
  border-top: 1px solid var(--border);
}

.ceo-signature strong {
  color: var(--blue-900);
  font-size: 1rem;
}

.ceo-signature span {
  margin-top: 2px;
  color: var(--green-700);
  font-size: 0.8rem;
  font-weight: 750;
}

@media (max-width: 900px) {
  .founder-note-grid,
  .ceo-message-grid {
    grid-template-columns: 1fr;
  }

  .founder-note-grid {
    gap: 32px;
  }

  .ceo-profile-card {
    position: static;
    max-width: 520px;
  }
}

@media (max-width: 680px) {
  .founder-note-section,
  .ceo-message-section {
    padding: 60px 0;
  }

  .founder-note-label {
    align-items: flex-start;
  }

  .founder-mark {
    width: 64px;
    height: 64px;
    flex-basis: 64px;
    border-radius: 19px;
  }

  .ceo-message-copy,
  .ceo-profile-card {
    padding: 24px;
  }

  .quote-mark {
    right: 18px;
    font-size: 5.5rem;
  }
}

/* END IBC CEO PROFILE UPGRADE */
'''


styles_path = ASSETS / "styles.css"
styles = styles_path.read_text(encoding="utf-8")

css_pattern = re.compile(
    r"/\* BEGIN IBC CEO PROFILE UPGRADE \*/.*?"
    r"/\* END IBC CEO PROFILE UPGRADE \*/",
    flags=re.DOTALL,
)

if css_pattern.search(styles):
    styles = css_pattern.sub(
        ceo_css.strip(),
        styles,
        count=1,
    )
else:
    styles = (
        styles.rstrip()
        + "\n\n"
        + ceo_css.strip()
        + "\n"
    )

styles_path.write_text(styles, encoding="utf-8")
print("Added CEO profile styling")


service_script = r'''
/* BEGIN IBC SERVICE PRESELECTION */

(() => {
  const serviceSelect = document.querySelector("#service");

  if (!serviceSelect) {
    return;
  }

  const params = new URLSearchParams(window.location.search);
  const requestedService = params.get("service");

  if (!requestedService) {
    return;
  }

  const normalise = (value) =>
    String(value)
      .trim()
      .toLowerCase()
      .replace(/\s+/g, " ");

  const requestedValue = normalise(requestedService);

  const matchingOption = Array.from(
    serviceSelect.options
  ).find((option) => {
    return (
      normalise(option.value) === requestedValue
      || normalise(option.textContent) === requestedValue
    );
  });

  if (!matchingOption) {
    return;
  }

  serviceSelect.value = matchingOption.value;
  serviceSelect.classList.add("preselected");

  const formCard = serviceSelect.closest(".form-card");

  if (formCard) {
    window.setTimeout(() => {
      formCard.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }, 250);
  }
})();

/* END IBC SERVICE PRESELECTION */
'''


script_path = ASSETS / "script.js"
script = script_path.read_text(encoding="utf-8")

js_pattern = re.compile(
    r"/\* BEGIN IBC SERVICE PRESELECTION \*/.*?"
    r"/\* END IBC SERVICE PRESELECTION \*/",
    flags=re.DOTALL,
)

if js_pattern.search(script):
    script = js_pattern.sub(
        service_script.strip(),
        script,
        count=1,
    )
else:
    script = (
        script.rstrip()
        + "\n\n"
        + service_script.strip()
        + "\n"
    )

script_path.write_text(script, encoding="utf-8")
print("Added contact-form service preselection")


print()
print("CEO profile and website improvements completed.")
print(f"Backups saved in: {BACKUP}")
