
(function () {
    const KEY = "smartlab-theme";

    function setTheme(theme) {
        document.documentElement.setAttribute("data-theme", theme);
        localStorage.setItem(KEY, theme);

        document.querySelectorAll(".theme-toggle").forEach(button => {
            button.textContent =
                theme === "dark" ? "☀ Light Mode" : "☾ Dark Mode";
        });
    }

    const savedTheme = localStorage.getItem(KEY) || "light";
    setTheme(savedTheme);

    window.toggleSmartLabTheme = function () {
        const current = document.documentElement.getAttribute("data-theme");
        setTheme(current === "dark" ? "light" : "dark");
    };
})();
