// Embeds every chart on the page. Each <div data-spec="specs/…json"> gets its own Vega / Vega-Lite view,
// styled by the shared theme in js/theme.json.

async function embedCharts() {
  const theme = await fetch("js/theme.json").then((r) => r.json());

  // Wait for the web fonts so Vega measures label widths with the right typeface.
  if (document.fonts && document.fonts.ready) {
    await document.fonts.ready;
  }

  const charts = document.querySelectorAll("[data-spec]");
  await Promise.all(
    Array.from(charts).map((el) =>
      vegaEmbed(el, el.dataset.spec, {
        config: theme,
        renderer: "svg",
        actions: false,
        tooltip: { theme: "custom" },
      }).catch((err) => {
        el.textContent = "This chart could not be loaded.";
        console.error(el.dataset.spec, err);
      })
    )
  );
}

// Highlight the current level in the top bar while scrolling.
function trackLevels() {
  const links = document.querySelectorAll(".levels a");
  const byId = new Map(Array.from(links).map((a) => [a.getAttribute("href").slice(1), a]));
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          links.forEach((a) => a.classList.remove("active"));
          const link = byId.get(entry.target.id);
          if (link) link.classList.add("active");
        }
      });
    },
    { rootMargin: "-45% 0px -50% 0px" }
  );
  byId.forEach((_, id) => {
    const section = document.getElementById(id);
    if (section) observer.observe(section);
  });
}

embedCharts();
trackLevels();
