document.addEventListener("DOMContentLoaded", () => {
    const currentPath = window.location.pathname;

    document.querySelectorAll("[data-nav-url]").forEach((link) => {
        const navUrl = link.getAttribute("data-nav-url");
        if (!navUrl) {
            return;
        }

        const isHome = navUrl === "/" && currentPath === "/";
        const isSection = navUrl !== "/" && currentPath.startsWith(navUrl);
        if (isHome || isSection) {
            link.classList.add("is-active");
        }
    });
});
