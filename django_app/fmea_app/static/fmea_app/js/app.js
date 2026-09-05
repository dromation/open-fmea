(function () {
  const THEME_STORAGE_KEY = "open-fmea-theme";

  function readStoredTheme() {
    try {
      const value = window.localStorage.getItem(THEME_STORAGE_KEY);
      return value === "light" || value === "dark" ? value : null;
    } catch (err) {
      return null;
    }
  }

  function writeStoredTheme(value) {
    try {
      window.localStorage.setItem(THEME_STORAGE_KEY, value);
    } catch (err) {
      /* localStorage unavailable (private browsing, disabled storage) —
         the toggle still works for the current page load via the
         data-theme attribute, it just won't persist. */
    }
  }

  function systemPrefersLight() {
    return (
      window.matchMedia &&
      window.matchMedia("(prefers-color-scheme: light)").matches
    );
  }

  const root = document.documentElement;
  const storedTheme = readStoredTheme();
  if (storedTheme) {
    root.setAttribute("data-theme", storedTheme);
  }

  document.querySelectorAll("[data-theme-toggle]").forEach((button) => {
    button.addEventListener("click", () => {
      const current = root.getAttribute("data-theme") || (systemPrefersLight() ? "light" : "dark");
      const next = current === "light" ? "dark" : "light";
      root.setAttribute("data-theme", next);
      writeStoredTheme(next);
    });
  });

  const shell = document.querySelector("[data-app-shell]");
  if (!shell) {
    return;
  }

  const storedSidebar = window.localStorage.getItem("open-fmea-sidebar-collapsed");
  if (storedSidebar === "1") {
    shell.classList.add("sidebar-collapsed");
  }

  document.querySelectorAll("[data-sidebar-toggle]").forEach((button) => {
    button.addEventListener("click", () => {
      shell.classList.toggle("sidebar-collapsed");
      window.localStorage.setItem(
        "open-fmea-sidebar-collapsed",
        shell.classList.contains("sidebar-collapsed") ? "1" : "0"
      );
    });
  });

  const currentPath = window.location.pathname.replace(/\/+$/, "") || "/";
  document.querySelectorAll("[data-nav-link]").forEach((link) => {
    const linkUrl = new URL(link.href, window.location.origin);
    const linkPath = linkUrl.pathname.replace(/\/+$/, "") || "/";
    if (linkPath === currentPath) {
      link.classList.add("is-active");
      link.setAttribute("aria-current", "page");
    }
  });
})();
