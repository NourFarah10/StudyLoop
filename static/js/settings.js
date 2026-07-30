document.addEventListener("DOMContentLoaded", () => {

    // ===============================
    // Live theme preview
    // ===============================
    // Instantly applies the selected theme to this page so the user can
    // see it right away. The actual save (and the theme applying across
    // every other page) still happens the normal way: through the
    // existing form POST to /settings, which updates the DB — after
    // that, layout.html reads the saved value on every request and sets
    // data-theme accordingly, site-wide.

    document.querySelectorAll(".theme-option-input").forEach(input => {

        input.addEventListener("change", function () {

            if (this.checked) {
                document.documentElement.setAttribute("data-theme", this.value);
            }

        });

    });

});