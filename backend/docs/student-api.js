/**
 * AI Ads Studio — Student API client (async fetch)
 * Live API: https://ai-ads-studio-kappa.vercel.app/api
 *
 * Add to EVERY HTML page (before your page scripts):
 *   <script>
 *     window.API_BASE = "https://ai-ads-studio-kappa.vercel.app/api";
 *   </script>
 *   <script src="student-api.js"></script>
 *
 * Then call: StudioAPI.initPage() on DOMContentLoaded
 */
(function (global) {
  "use strict";

  const TOKEN_KEY = "access_token";
  const REFRESH_KEY = "refresh_token";

  const API_BASE = (global.API_BASE || "https://ai-ads-studio-kappa.vercel.app/api").replace(
    /\/$/,
    ""
  );

  /* ---------- helpers ---------- */

  function escapeHtml(value) {
    if (value == null) return "";
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function formatError(data, fallback) {
    if (!data) return fallback || "Request failed";
    if (typeof data.error === "string" && data.error) return data.error;
    if (typeof data.detail === "string") return data.detail;
    if (Array.isArray(data.detail)) return data.detail.join(" ");
    if (typeof data.detail === "object" && data.detail) {
      return Object.entries(data.detail)
        .map(function (kv) {
          return kv[0] + ": " + (Array.isArray(kv[1]) ? kv[1].join(", ") : kv[1]);
        })
        .join(" ");
    }
    var fields = Object.entries(data)
      .filter(function (kv) {
        return kv[0] !== "detail" && kv[0] !== "error";
      })
      .map(function (kv) {
        return Array.isArray(kv[1]) ? kv[1].join(", ") : String(kv[1]);
      });
    return fields.length ? fields.join(" ") : fallback || "Request failed";
  }

  function showAlert(containerId, message, type) {
    var el = document.getElementById(containerId);
    if (!el) return;
    el.hidden = false;
    el.innerHTML =
      '<div class="rounded-lg px-4 py-3 text-sm ' +
      (type === "success" ? "bg-green-50 text-green-800" : "bg-red-50 text-red-800") +
      '" role="alert">' +
      escapeHtml(message) +
      "</div>";
  }

  function setLoading(btn, loading, label) {
    if (!btn) return;
    if (loading) {
      btn.dataset._label = btn.textContent;
      btn.disabled = true;
      if (label) btn.textContent = label;
    } else {
      btn.disabled = false;
      if (btn.dataset._label) {
        btn.textContent = btn.dataset._label;
        delete btn.dataset._label;
      }
    }
  }

  function getToken() {
    return localStorage.getItem(TOKEN_KEY);
  }

  function setAuth(access, refresh) {
    if (access) localStorage.setItem(TOKEN_KEY, access);
    if (refresh) localStorage.setItem(REFRESH_KEY, refresh);
  }

  function clearAuth() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
  }

  async function tryRefresh() {
    var refresh = localStorage.getItem(REFRESH_KEY);
    if (!refresh) return false;
    try {
      var res = await fetch(API_BASE + "/auth/refresh/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh: refresh }),
      });
      var data = await res.json().catch(function () {
        return {};
      });
      if (!res.ok) {
        clearAuth();
        return false;
      }
      if (data.access) localStorage.setItem(TOKEN_KEY, data.access);
      if (data.refresh) localStorage.setItem(REFRESH_KEY, data.refresh);
      return true;
    } catch (e) {
      clearAuth();
      return false;
    }
  }

  /**
   * Core API call — path like "/auth/login/" (leading slash required)
   */
  async function api(path, options, retried) {
    options = options || {};
    var headers = Object.assign({ "Content-Type": "application/json" }, options.headers || {});
    var token = getToken();
    if (token) headers.Authorization = "Bearer " + token;

    var res = await fetch(API_BASE + path, Object.assign({}, options, { headers: headers }));
    var data = await res.json().catch(function () {
      return {};
    });

    if (res.status === 401 && !retried && (await tryRefresh())) {
      return api(path, options, true);
    }

    if (!res.ok) {
      var err = new Error(formatError(data, res.statusText));
      err.status = res.status;
      err.data = data;
      throw err;
    }
    return data;
  }

  /* ---------- auth API ---------- */

  async function register(email, password, fullName) {
    return api("/auth/register/", {
      method: "POST",
      body: JSON.stringify({
        email: email,
        work_email: email,
        full_name: fullName || "",
        password: password,
        password_confirm: password,
      }),
    });
  }

  async function login(email, password) {
    var data = await api("/auth/login/", {
      method: "POST",
      body: JSON.stringify({ email: email, password: password }),
    });
    setAuth(data.access, data.refresh);
    return data;
  }

  async function registerAndLogin(email, password, fullName) {
    await register(email, password, fullName);
    return login(email, password);
  }

  async function logout() {
    var refresh = localStorage.getItem(REFRESH_KEY);
    try {
      if (refresh) {
        await api("/auth/logout/", {
          method: "POST",
          body: JSON.stringify({ refresh: refresh }),
        });
      }
    } catch (e) {
      /* ignore */
    }
    clearAuth();
  }

  async function me() {
    return api("/auth/me/");
  }

  /* ---------- app API ---------- */

  async function getDashboard() {
    return api("/dashboard/");
  }

  async function getAnalytics() {
    return api("/analytics/");
  }

  async function listCampaigns(search) {
    var q = search ? "?search=" + encodeURIComponent(search) : "";
    return api("/campaigns/" + q);
  }

  async function createCampaign(payload) {
    return api("/campaigns/", { method: "POST", body: JSON.stringify(payload) });
  }

  async function simulateCampaign(campaignId) {
    return api("/campaigns/" + campaignId + "/simulate/", { method: "POST", body: "{}" });
  }

  async function listNotifications(unreadOnly) {
    var q = unreadOnly ? "?unread=true" : "";
    return api("/notifications/" + q);
  }

  async function markNotificationRead(id) {
    return api("/notifications/" + id + "/read/", { method: "PATCH", body: "{}" });
  }

  async function createBrief(payload) {
    return api("/ad-briefs/", { method: "POST", body: JSON.stringify(payload) });
  }

  async function generateVariants(briefId) {
    return api("/ad-briefs/" + briefId + "/generate/", { method: "POST", body: "{}" });
  }

  function normalizePlatform(value) {
    var map = {
      friendly: "meta",
      meta: "meta",
      tiktok: "tiktok",
      linkedin: "linkedin",
      youtube: "youtube",
    };
    return map[(value || "meta").toLowerCase()] || value;
  }

  /* ---------- DOM wiring (match class branch HTML ids) ---------- */

  function wireSignin() {
    var emailEl = document.getElementById("login-email");
    var pwEl = document.getElementById("login-pw");
    if (!emailEl || !pwEl) return;

    var btn =
      document.querySelector("#login button.bg-blue-accent") ||
      document.querySelector("#login button[type=button].bg-blue-accent");

    async function submit(e) {
      if (e) e.preventDefault();
      var email = emailEl.value.trim().toLowerCase();
      if (!email.includes("@")) {
        showAlert("login-error", "Enter a valid email.", "error");
        return;
      }
      if (!pwEl.value) {
        showAlert("login-error", "Enter your password.", "error");
        return;
      }
      setLoading(btn, true, "Signing in…");
      try {
        await login(email, pwEl.value);
        showAlert("login-error", "Success! Redirecting…", "success");
        window.location.href = "/index.html";
      } catch (err) {
        showAlert("login-error", err.message, "error");
      } finally {
        setLoading(btn, false);
      }
    }

    if (btn) btn.addEventListener("click", submit);
    pwEl.addEventListener("keydown", function (e) {
      if (e.key === "Enter") submit(e);
    });
  }

  function wireSignup() {
    var form = document.getElementById("signup-form");
    var emailEl = document.getElementById("signup-email");
    var pwEl = document.getElementById("signup-pw");
    var nameEl = document.getElementById("signup-name");
    if (!emailEl || !pwEl) return;

    var btn =
      document.querySelector("#signup button.bg-blue-accent") ||
      document.querySelector("#signup-form button[type=submit]");

    async function submit(e) {
      if (e) e.preventDefault();
      var email = emailEl.value.trim().toLowerCase();
      if (!email.includes("@")) {
        showAlert("signup-error", "Enter a valid email.", "error");
        return;
      }
      if (pwEl.value.length < 8) {
        showAlert("signup-error", "Password must be at least 8 characters.", "error");
        return;
      }
      setLoading(btn, true, "Creating account…");
      try {
        await registerAndLogin(email, pwEl.value, nameEl ? nameEl.value.trim() : "");
        window.location.href = "/index.html";
      } catch (err) {
        showAlert("signup-error", err.message, "error");
      } finally {
        setLoading(btn, false);
      }
    }

    if (form) form.addEventListener("submit", submit);
    else if (btn) btn.addEventListener("click", submit);
  }

  function findVariantsPanel() {
    var panel = document.getElementById("variants-panel");
    if (panel) return panel;
    var headings = document.querySelectorAll("h1");
    for (var i = 0; i < headings.length; i++) {
      if (headings[i].textContent.indexOf("Generated variants") !== -1) {
        var col = headings[i].closest(".grid") || headings[i].parentElement;
        if (col) {
          var box = col.querySelector(".bg-white.border");
          if (box) return box;
        }
      }
    }
    return null;
  }

  function wireCreateAd() {
    var form = document.querySelector("form");
    if (!form) return;

    form.addEventListener("submit", async function (e) {
      e.preventDefault();
      var btn = form.querySelector('input[type="submit"], button[type="submit"]');
      setLoading(btn, true, "Generating…");
      try {
        var brief = await createBrief({
          product_service: document.getElementById("prod-service").value,
          audience: document.getElementById("audience").value,
          tone: document.getElementById("tone").value,
          platform: normalizePlatform(document.getElementById("platform").value),
          key_message: document.getElementById("key-message")
            ? document.getElementById("key-message").value
            : "",
        });
        var variants = await generateVariants(brief.id);
        var panel = findVariantsPanel();
        if (panel) {
          panel.classList.remove("items-center", "justify-center");
          panel.innerHTML = variants
            .map(function (v) {
              return (
                '<article class="bg-white border border-gray-200 rounded-2xl p-5 mb-4 shadow-sm">' +
                "<h3 class=\"font-bold text-lg\">" +
                escapeHtml(v.headline) +
                "</h3>" +
                '<p class="text-gray-600 mt-2 whitespace-pre-wrap">' +
                escapeHtml(v.body || v.primary_text) +
                "</p>" +
                (v.cta || v.call_to_action
                  ? '<p class="text-blue-600 font-semibold mt-2">' +
                    escapeHtml(v.cta || v.call_to_action) +
                    "</p>"
                  : "") +
                "</article>"
              );
            })
            .join("");
        }
      } catch (err) {
        alert(err.message);
      } finally {
        setLoading(btn, false);
      }
    });
  }

  async function wireDashboard() {
    var main = document.getElementById("app-main") || document.getElementById("app-hydrate");
    if (!main) return;
    try {
      var d = await getDashboard();
      main.innerHTML =
        '<div class="max-w-6xl mx-auto">' +
        "<h2 class=\"text-xl font-bold mb-4\">Dashboard</h2>" +
        '<div class="grid grid-cols-2 md:grid-cols-4 gap-4">' +
        '<div class="bg-white rounded-2xl p-4 border"><p class="text-xs text-gray-500">Campaigns</p><p class="text-2xl font-bold">' +
        d.total_campaigns +
        "</p></div>" +
        '<div class="bg-white rounded-2xl p-4 border"><p class="text-xs text-gray-500">Briefs</p><p class="text-2xl font-bold">' +
        d.total_briefs +
        "</p></div>" +
        '<div class="bg-white rounded-2xl p-4 border"><p class="text-xs text-gray-500">Variants</p><p class="text-2xl font-bold">' +
        d.total_variants +
        "</p></div>" +
        "</div></div>";
    } catch (err) {
      main.innerHTML = '<p class="text-red-600">' + escapeHtml(err.message) + "</p>";
    }
  }

  async function wireCampaigns() {
    var grid = document.getElementById("campaigns-grid");
    var empty = document.getElementById("campaigns-empty");
    var createBtn = document.getElementById("studio-create-campaign");
    if (!grid) return;

    async function load() {
      var list = await listCampaigns();
      if (!list.length) {
        if (empty) empty.classList.remove("hidden");
        grid.innerHTML = "";
        return;
      }
      if (empty) empty.classList.add("hidden");
      grid.innerHTML = list
        .map(function (c) {
          return (
            '<article class="bg-white border border-gray-200 rounded-2xl p-5 shadow-sm flex flex-col" data-campaign-id="' +
            c.id +
            '">' +
            "<h3 class=\"font-bold\">" +
            escapeHtml(c.name) +
            "</h3>" +
            '<p class="text-sm text-gray-500">' +
            escapeHtml(c.status) +
            " · " +
            escapeHtml(c.platform) +
            "</p>" +
            '<button type="button" class="studio-simulate-btn mt-4 text-sm font-semibold text-blue-700 bg-blue-50 py-2 rounded-lg" data-id="' +
            c.id +
            '">Simulate live run</button></article>"
          );
        })
        .join("");

      grid.querySelectorAll(".studio-simulate-btn").forEach(function (btn) {
        btn.addEventListener("click", async function () {
          try {
            await simulateCampaign(btn.getAttribute("data-id"));
            await load();
          } catch (err) {
            alert(err.message);
          }
        });
      });
    }

    if (createBtn) {
      createBtn.addEventListener("click", async function () {
        var name = prompt("Campaign name");
        if (!name) return;
        try {
          await createCampaign({ name: name, platform: "meta", status: "draft" });
          await load();
        } catch (err) {
          alert(err.message);
        }
      });
    }

    await load();
  }

  async function wireAnalytics() {
    try {
      var data = await getAnalytics();
      var spend = document.getElementById("stat-spend");
      var impressions = document.getElementById("stat-impressions");
      var clicks = document.getElementById("stat-clicks");
      var ctr = document.getElementById("stat-ctr");
      if (spend) spend.textContent = "$" + parseFloat(data.spend || 0).toFixed(0);
      if (impressions) impressions.textContent = data.impressions || 0;
      if (clicks) clicks.textContent = data.clicks || 0;
      if (ctr) ctr.textContent = (data.ctr || 0) + "%";
      var errEl = document.getElementById("analytics-error");
      if (data.demo_mode && errEl) {
        errEl.hidden = false;
        errEl.textContent = data.disclaimer || "Demo metrics only.";
        errEl.classList.remove("hidden");
      }
    } catch (err) {
      var errBox = document.getElementById("analytics-error");
      if (errBox) {
        errBox.hidden = false;
        errBox.textContent = err.message;
        errBox.classList.remove("hidden");
      }
    }
  }

  async function wireNotifications() {
    var listEl = document.getElementById("notifications-list");
    if (!listEl) return;
    try {
      var list = await listNotifications();
      if (!list.length) {
        listEl.innerHTML = '<p class="text-center text-gray-500 py-8">No notifications yet.</p>';
        return;
      }
      listEl.innerHTML = list
        .map(function (n) {
          return (
            '<div class="py-4 ' +
            (n.is_read ? "opacity-60" : "") +
            '"><p class="font-semibold">' +
            escapeHtml(n.title) +
            "</p><p class=\"text-sm text-gray-500\">" +
            escapeHtml(n.message) +
            "</p></div>"
          );
        })
        .join("");
    } catch (err) {
      listEl.innerHTML = '<p class="text-red-600">' + escapeHtml(err.message) + "</p>";
    }
  }

  function injectAuthErrorSlots() {
    if (!document.getElementById("login-error")) {
      var loginH1 = document.querySelector("#login h1");
      if (loginH1 && loginH1.parentElement) {
        var slot = document.createElement("div");
        slot.id = "login-error";
        slot.hidden = true;
        loginH1.parentElement.insertBefore(slot, loginH1.nextSibling);
      }
    }
    if (!document.getElementById("signup-error")) {
      var h1 = document.querySelector("#signup h1") || document.querySelector("#signup-form h1");
      if (h1) {
        var slot = document.createElement("div");
        slot.id = "signup-error";
        slot.hidden = true;
        h1.parentElement.insertBefore(slot, h1.nextSibling);
      }
    }
  }

  async function requireAuth() {
    if (!getToken()) {
      window.location.href = "/signin.html";
      return false;
    }
    try {
      await me();
      return true;
    } catch (e) {
      clearAuth();
      window.location.href = "/signin.html";
      return false;
    }
  }

  async function initPage() {
    injectAuthErrorSlots();

    var path = window.location.pathname.toLowerCase();

    if (path.includes("signin")) {
      wireSignin();
      wireSignup();
      return;
    }
    if (path.includes("signup") || path.includes("ad-page")) {
      wireSignup();
      return;
    }

    if (!(await requireAuth())) return;

    if (path.includes("index") || path.endsWith("/")) {
      await wireDashboard();
    } else if (path.includes("create-ad")) {
      wireCreateAd();
    } else if (path.includes("campaigns")) {
      await wireCampaigns();
    } else if (path.includes("analytics") || path.includes("dashboard.html")) {
      await wireAnalytics();
    } else if (path.includes("notification")) {
      await wireNotifications();
    }
  }

  global.StudioAPI = {
    API_BASE: API_BASE,
    api: api,
    escapeHtml: escapeHtml,
    getToken: getToken,
    setAuth: setAuth,
    clearAuth: clearAuth,
    register: register,
    login: login,
    registerAndLogin: registerAndLogin,
    logout: logout,
    me: me,
    getDashboard: getDashboard,
    getAnalytics: getAnalytics,
    listCampaigns: listCampaigns,
    createCampaign: createCampaign,
    simulateCampaign: simulateCampaign,
    listNotifications: listNotifications,
    createBrief: createBrief,
    generateVariants: generateVariants,
    wireSignin: wireSignin,
    wireSignup: wireSignup,
    wireCreateAd: wireCreateAd,
    initPage: initPage,
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      initPage().catch(function (e) {
        console.error(e);
      });
    });
  }
})();
