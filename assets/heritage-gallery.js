(() => {
  const gallery = document.querySelector("#heritageGallery");

  if (!gallery) {
    return;
  }

  const filters = document.querySelectorAll("[data-gallery-filter]");
  let items = [];

  const escapeHtml = (value) =>
    String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");

  const renderGallery = (filter = "all") => {
    const visibleItems =
      filter === "all"
        ? items
        : items.filter((item) => item.group === filter);

    gallery.innerHTML = visibleItems
      .map(
        (item, index) => `
          <article
            class="heritage-card ${index === 0 ? "heritage-card-featured" : ""}"
          >
            <img
              src="${escapeHtml(item.image)}"
              alt="${escapeHtml(item.alt)}"
              loading="lazy"
            >

            <div class="heritage-card-overlay"></div>

            <div class="heritage-card-content">
              <span>${escapeHtml(item.label)}</span>
              <h3>${escapeHtml(item.title)}</h3>
              <p>${escapeHtml(item.subtitle)}</p>
            </div>
          </article>
        `
      )
      .join("");
  };

  const loadGallery = async () => {
    try {
      const response = await fetch(
        "assets/heritage/gallery.json",
        { cache: "no-store" }
      );

      if (!response.ok) {
        throw new Error(`Gallery request failed: ${response.status}`);
      }

      items = await response.json();
      renderGallery();
    } catch (error) {
      console.error(error);

      gallery.innerHTML = `
        <div class="gallery-error">
          The location gallery could not be loaded.
        </div>
      `;
    }
  };

  filters.forEach((button) => {
    button.addEventListener("click", () => {
      filters.forEach((item) => {
        item.classList.remove("active");
        item.setAttribute("aria-pressed", "false");
      });

      button.classList.add("active");
      button.setAttribute("aria-pressed", "true");

      renderGallery(button.dataset.galleryFilter);
    });
  });

  loadGallery();
})();
