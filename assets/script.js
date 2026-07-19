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
