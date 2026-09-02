(function () {
  const shell = document.querySelector("[data-app-shell]");
  if (!shell) {
    return;
  }

  const stored = window.localStorage.getItem("open-fmea-sidebar-collapsed");
  if (stored === "1") {
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
