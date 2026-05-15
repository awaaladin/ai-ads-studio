/**

 * Wires sidebar labels to pages (student HTML has no hrefs yet).

 */

(function () {

  const ROUTES = {

    Dashboard: "/index.html",

    "Create Ad": "/create-ad.html",

    Campaigns: "/campaigns.html",

    Analytics: "/analytics.html",

    Notifications: "/notification.html",

    Settings: "/settings.html",

    "Sign in": "/signin.html",

    "Sign out": "/signin.html",

  };



  function go(href) {

    if (!href || href === "#") return;

    window.location.href = href;

  }



  function wireNavItem(el) {

    const label = (el.textContent || "").replace(/\s+/g, " ").trim();

    for (const [key, href] of Object.entries(ROUTES)) {

      if (label.includes(key)) {

        el.style.cursor = "pointer";

        el.setAttribute("role", "link");

        el.setAttribute("tabindex", "0");

        el.addEventListener("click", () => {

          if (key === "Sign out") {

            localStorage.removeItem("access_token");

            localStorage.removeItem("refresh_token");

          }

          go(href);

        });

        el.addEventListener("keydown", (e) => {

          if (e.key === "Enter" || e.key === " ") {

            e.preventDefault();

            el.click();

          }

        });

        break;

      }

    }

  }



  function highlightActiveNav() {

    const p = window.location.pathname;

    let active = "Dashboard";

    if (p.includes("create-ad")) active = "Create Ad";

    else if (p.includes("campaigns")) active = "Campaigns";

    else if (p.includes("analytics") || p.includes("Dashboard.html")) active = "Analytics";

    else if (p.includes("notification")) active = "Notifications";

    else if (p.includes("settings")) active = "Settings";



    document.querySelectorAll("nav li").forEach((el) => {

      const label = (el.textContent || "").replace(/\s+/g, " ").trim();

      const isActive = label.includes(active);

      el.classList.toggle("font-semibold", isActive);

      el.classList.toggle("text-blue-700", isActive);

      el.classList.toggle("bg-blue-100", isActive);

      el.classList.toggle("text-gray-600", !isActive);

    });

  }



  function wire() {

    document.querySelectorAll("nav li").forEach(wireNavItem);

    highlightActiveNav();



    document.querySelectorAll("button").forEach((el) => {

      const t = (el.textContent || "").trim();

      if (/new ad/i.test(t)) {

        el.addEventListener("click", (e) => {

          e.preventDefault();

          go("/create-ad.html");

        });

      }

    });



    document.querySelectorAll("nav h1").forEach((brand) => {

      brand.style.cursor = "pointer";

      brand.addEventListener("click", () => go("/index.html"));

    });

  }



  if (document.readyState === "loading") {

    document.addEventListener("DOMContentLoaded", wire);

  } else {

    wire();

  }

})();


