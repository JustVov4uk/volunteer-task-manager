"use strict";

document.addEventListener("DOMContentLoaded", function () {
    var sidebar = document.getElementById("sidebarMenu");

    if (sidebar && window.bootstrap) {
        sidebar.addEventListener("shown.bs.collapse", function () {
            document.body.classList.add("sidebar-open");
        });

        sidebar.addEventListener("hidden.bs.collapse", function () {
            document.body.classList.remove("sidebar-open");
        });
    }

    if (window.bootstrap) {
        document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (el) {
            new bootstrap.Tooltip(el);
        });

        document.querySelectorAll('[data-bs-toggle="popover"]').forEach(function (el) {
            new bootstrap.Popover(el);
        });
    }

    document.querySelectorAll("[data-background]").forEach(function (el) {
        el.style.backgroundImage = "url(" + el.getAttribute("data-background") + ")";
    });

    var currentYear = document.querySelector(".current-year");
    if (currentYear) {
        currentYear.textContent = new Date().getFullYear().toString();
    }
});
