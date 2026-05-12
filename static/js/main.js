document.addEventListener("DOMContentLoaded", () => {
    const yearNode = document.getElementById("footer-year");
    if (yearNode) {
        yearNode.textContent = new Date().getFullYear().toString();
    }

    const header = document.getElementById("site-header");
    if (!header) {
        return;
    }

    const syncHeaderState = () => {
        header.classList.toggle("is-scrolled", window.scrollY > 12);
    };

    syncHeaderState();
    window.addEventListener("scroll", syncHeaderState, { passive: true });
});
