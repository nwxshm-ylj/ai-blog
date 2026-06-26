(function () {
  "use strict";

  var reduceMotionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");

  function prefersReducedMotion() {
    return reduceMotionQuery.matches;
  }

  function initReveal() {
    var revealItems = Array.prototype.slice.call(document.querySelectorAll("[data-reveal]"));
    if (!revealItems.length) return;

    if (prefersReducedMotion() || !("IntersectionObserver" in window)) {
      revealItems.forEach(function (item) {
        item.classList.add("is-visible");
      });
      return;
    }

    document.documentElement.classList.add("reveal-ready");

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    }, {
      rootMargin: "0px 0px -12% 0px",
      threshold: 0.12
    });

    revealItems.forEach(function (item, index) {
      if (!item.style.getPropertyValue("--reveal-delay")) {
        item.style.setProperty("--reveal-delay", Math.min(index % 6, 5) * 45 + "ms");
      }
      observer.observe(item);
    });
  }

  function initHeaderScroll() {
    var header = document.querySelector("[data-site-header]");
    if (!header) return;

    var ticking = false;

    function update() {
      header.classList.toggle("header-scrolled", window.scrollY > 8);
      ticking = false;
    }

    update();
    window.addEventListener("scroll", function () {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(update);
    }, { passive: true });
  }

  function initMobileMenu() {
    var menu = document.querySelector("[data-mobile-menu]");
    if (!menu) return;

    var summary = menu.querySelector("summary");
    if (!summary) return;

    function syncExpanded() {
      summary.setAttribute("aria-expanded", menu.open ? "true" : "false");
    }

    syncExpanded();
    menu.addEventListener("toggle", syncExpanded);
  }

  function initProjectFilters() {
    var filters = document.querySelector("[data-project-filters]");
    if (!filters) return;

    filters.addEventListener("click", function (event) {
      var button = event.target.closest("button[data-filter]");
      if (!button || !filters.contains(button)) return;

      filters.querySelectorAll("button[data-filter]").forEach(function (item) {
        item.classList.toggle("filter-active", item === button);
        item.setAttribute("aria-pressed", item === button ? "true" : "false");
      });
    });
  }

  function init() {
    initReveal();
    initHeaderScroll();
    initMobileMenu();
    initProjectFilters();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();