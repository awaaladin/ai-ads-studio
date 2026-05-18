# AI Ads Studio — Live API (copy-paste JS per endpoint)

| | |
|---|---|
| **Base URL** | `https://ai-ads-studio-kappa.vercel.app/api` |
| **Swagger** | `https://ai-ads-studio-kappa.vercel.app/docs/` |

Each section below is **one endpoint** + **JavaScript you can paste** into your HTML page. Every snippet uses the real **`id` / class** values from the class Tailwind templates (`signin.html`, `signup.html`, `index.html`, etc.).

Paste each `<script>` block at the **bottom of the matching HTML file**, just before `</body>`.

---

## HTML IDs used in this doc

| Page file | Section | IDs / selectors |
|-----------|---------|-----------------|
| `signin.html` | Sign in | `#login`, `#login-email`, `#login-pw`, `#login button.bg-blue-accent` |
| `signin.html` | Sign up tab | `#signup`, `#signup-name`, `#signup-email`, `#signup-pw`, `#signup button.bg-blue-accent` |
| `signup.html` | Sign up | `#signup-form`, `#signup-name`, `#signup-email`, `#signup-pw`, `#terms`, `button[type=submit]` |
| `index.html` | Dashboard | `#app-main` |
| `create-ad.html` | Brief form | `#prod-service`, `#audience`, `#tone`, `#platform`, `#key-message`, form `input[type=submit]` |
| `create-ad.html` | Results (add this id) | `#variants-panel` on the right white box |
| `campaigns.html` | Campaigns | `#campaigns-grid`, `#campaigns-empty`, `#studio-create-campaign`, `.studio-simulate-btn` |
| `analytics.html` | Stats | `#stat-spend`, `#stat-impressions`, `#stat-clicks`, `#stat-ctr`, `#analytics-error`, `#analytics-live-badge`, `#performance-chart`, `#platform-chart`, `#analytics-activity` |
| `notification.html` | Feed | `#notifications-list`, `#notifications-unread-tab` |
| `history.html` | History | `#app-main` |
| `settings.html` | Profile | `#settings-full-name`, `#settings-email`, `#billing-panel` |
| `pricing.html` | Upgrade | `#btn-upgrade`, `#pro-price` |

**Platform:** API expects `meta`, `tiktok`, `linkedin`, `youtube`. Your `#platform` select uses `friendly` for Meta — snippets map it to `meta`.

**Error boxes (add if missing):**

```html
<div id="login-error" hidden class="mb-4"></div>
<div id="signup-error" hidden class="mb-4"></div>
```

---

## Tiny helper (optional — include once per page if you use multiple snippets)

If you paste **more than one** block on the same page, add this **once** and delete the duplicate `api()` from the other blocks.

```html
<script>
  const API_BASE = "https://ai-ads-studio-kappa.vercel.app/api";

  async function api(path, options = {}) {
    const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
    const token = localStorage.getItem("access_token");
    if (token) headers.Authorization = "Bearer " + token;
    const res = await fetch(API_BASE + path, { ...options, headers });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      const msg =
        data.error ||
        (typeof data.detail === "string" ? data.detail : null) ||
        (Array.isArray(data.detail) ? data.detail.join(" ") : null) ||
        res.statusText;
      throw new Error(msg);
    }
    return data;
  }

  function showError(elId, message, ok) {
    const el = document.getElementById(elId);
    if (!el) return alert(message);
    el.hidden = false;
    el.className = ok
      ? "rounded-lg px-4 py-3 text-sm bg-green-50 text-green-800 mb-4"
      : "rounded-lg px-4 py-3 text-sm bg-red-50 text-red-800 mb-4";
    el.textContent = message;
  }

  function platformValue() {
    const v = document.getElementById("platform")?.value || "meta";
    return v === "friendly" ? "meta" : v;
  }
</script>
```

---

## System

### `GET /api/` — Health check

**Page:** any (e.g. `index.html`) · **Target:** optional `#api-status`

```html
<!-- Add somewhere: <p id="api-status"></p> -->
<script>
  (async function () {
    const API_BASE = "https://ai-ads-studio-kappa.vercel.app/api";
    const res = await fetch(API_BASE + "/");
    const data = await res.json();
    const el = document.getElementById("api-status");
    if (el) {
      el.textContent = data.status + " · DB: " + data.database + " · AI: " + data.ai;
      el.className = "text-sm text-gray-500";
    } else {
      console.log("Health:", data);
    }
  })();
</script>
```

---

### `GET /api/legal/terms/` — Terms text

**Page:** `signup.html` (wire to Terms link) · **Targets:** `#terms` checkbox area, open in modal or new panel

```html
<script>
  (async function () {
    const API_BASE = "https://ai-ads-studio-kappa.vercel.app/api";
    const res = await fetch(API_BASE + "/legal/terms/");
    const data = await res.json();
    // Example: show in alert when user clicks Terms link
    document.querySelectorAll('#signup-form a[href="#"]').forEach(function (a) {
      if (a.textContent.toLowerCase().includes("terms")) {
        a.addEventListener("click", function (e) {
          e.preventDefault();
          alert(data.title + "\n\n" + (data.body || data.content || "").slice(0, 500));
        });
      }
    });
  })();
</script>
```

---

### `GET /api/legal/privacy/` — Privacy text

**Page:** `signup.html` · same pattern as Terms

```html
<script>
  (async function () {
    const API_BASE = "https://ai-ads-studio-kappa.vercel.app/api";
    const res = await fetch(API_BASE + "/legal/privacy/");
    const data = await res.json();
    document.querySelectorAll('#signup-form a[href="#"]').forEach(function (a) {
      if (a.textContent.toLowerCase().includes("privacy")) {
        a.addEventListener("click", function (e) {
          e.preventDefault();
          alert(data.title + "\n\n" + (data.body || data.content || "").slice(0, 500));
        });
      }
    });
  })();
</script>
```

---

## Authentication

### `POST /api/auth/register/` — Create account

**Page:** `signup.html` or `#signup` on `signin.html`  
**Targets:** `#signup-form` or `#signup`, `#signup-name`, `#signup-email`, `#signup-pw`, submit `button.bg-blue-accent` or `button[type=submit]`, errors in `#signup-error`

```html
<div id="signup-error" hidden class="mb-4"></div>
<script>
  document.addEventListener("DOMContentLoaded", function () {
    const API_BASE = "https://ai-ads-studio-kappa.vercel.app/api";
    const form = document.getElementById("signup-form");
    const root = document.getElementById("signup") || document;
    const btn =
      form?.querySelector('button[type="submit"]') ||
      root.querySelector("#signup button.bg-blue-accent");

    async function register() {
      const email = document.getElementById("signup-email").value.trim().toLowerCase();
      const password = document.getElementById("signup-pw").value;
      const fullName = document.getElementById("signup-name")?.value.trim() || "";
      const terms = document.getElementById("terms");
      if (terms && !terms.checked) {
        showError("signup-error", "Please accept the Terms.", false);
        return;
      }
      if (password.length < 8) {
        showError("signup-error", "Password must be at least 8 characters.", false);
        return;
      }
      btn.disabled = true;
      try {
        const res = await fetch(API_BASE + "/auth/register/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            email,
            work_email: email,
            full_name: fullName,
            password,
            password_confirm: password,
          }),
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok) throw new Error(data.email?.[0] || data.error || data.detail || "Register failed");
        showError("signup-error", "Account created! Log in next.", true);
        // Optional: auto-login — see POST /auth/login/ snippet
      } catch (e) {
        showError("signup-error", e.message, false);
      } finally {
        btn.disabled = false;
      }
    }

    function showError(id, message, ok) {
      const el = document.getElementById(id);
      if (!el) return alert(message);
      el.hidden = false;
      el.className = ok
        ? "rounded-lg px-4 py-3 text-sm bg-green-50 text-green-800 mb-4"
        : "rounded-lg px-4 py-3 text-sm bg-red-50 text-red-800 mb-4";
      el.textContent = message;
    }

    if (form) form.addEventListener("submit", function (e) { e.preventDefault(); register(); });
    else if (btn) btn.addEventListener("click", register);
  });
</script>
```

---

### `POST /api/auth/login/` — Sign in

**Page:** `signin.html`  
**Targets:** `#login-email`, `#login-pw`, `#login button.bg-blue-accent`, `#login-error`

```html
<div id="login-error" hidden class="mb-4"></div>
<script>
  document.addEventListener("DOMContentLoaded", function () {
    const API_BASE = "https://ai-ads-studio-kappa.vercel.app/api";
    const btn = document.querySelector("#login button.bg-blue-accent");
    const emailEl = document.getElementById("login-email");
    const pwEl = document.getElementById("login-pw");

    async function login() {
      const email = emailEl.value.trim().toLowerCase();
      const password = pwEl.value;
      btn.disabled = true;
      try {
        const res = await fetch(API_BASE + "/auth/login/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok) throw new Error(data.detail || data.error || "Login failed");
        localStorage.setItem("access_token", data.access);
        localStorage.setItem("refresh_token", data.refresh);
        window.location.href = "/index.html";
      } catch (e) {
        const err = document.getElementById("login-error");
        if (err) { err.hidden = false; err.className = "rounded-lg px-4 py-3 text-sm bg-red-50 text-red-800 mb-4"; err.textContent = e.message; }
        else alert(e.message);
      } finally {
        btn.disabled = false;
      }
    }

    btn?.addEventListener("click", login);
    pwEl?.addEventListener("keydown", function (e) { if (e.key === "Enter") login(); });
  });
</script>
```

---

### `POST /api/auth/refresh/` — Refresh JWT

**Page:** any authenticated page (runs once on load)

```html
<script>
  (async function () {
    const API_BASE = "https://ai-ads-studio-kappa.vercel.app/api";
    const refresh = localStorage.getItem("refresh_token");
    if (!refresh) return;
    const res = await fetch(API_BASE + "/auth/refresh/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh }),
    });
    const data = await res.json().catch(() => ({}));
    if (res.ok && data.access) {
      localStorage.setItem("access_token", data.access);
      if (data.refresh) localStorage.setItem("refresh_token", data.refresh);
    }
  })();
</script>
```

---

### `POST /api/auth/logout/` — Sign out

**Page:** any · **Target:** add a button, e.g. `<button id="studio-logout" class="text-sm text-red-600">Log out</button>` in the nav

```html
<button id="studio-logout" type="button" class="text-sm text-red-600 font-medium">Log out</button>
<script>
  document.getElementById("studio-logout")?.addEventListener("click", async function () {
    const API_BASE = "https://ai-ads-studio-kappa.vercel.app/api";
    const refresh = localStorage.getItem("refresh_token");
    const token = localStorage.getItem("access_token");
    try {
      await fetch(API_BASE + "/auth/logout/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer " + token,
        },
        body: JSON.stringify({ refresh }),
      });
    } catch (e) { /* ignore */ }
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    window.location.href = "/signin.html";
  });
</script>
```

---

### `GET /api/auth/me/` — Current user + usage

**Page:** `settings.html`  
**Targets:** `#settings-email`, `#settings-full-name`, `#billing-panel`

```html
<script>
  document.addEventListener("DOMContentLoaded", async function () {
    const API_BASE = "https://ai-ads-studio-kappa.vercel.app/api";
    const token = localStorage.getItem("access_token");
    if (!token) { window.location.href = "/signin.html"; return; }

    const res = await fetch(API_BASE + "/auth/me/", {
      headers: { Authorization: "Bearer " + token },
    });
    const user = await res.json().catch(() => ({}));
    if (!res.ok) { window.location.href = "/signin.html"; return; }

    const nameEl = document.getElementById("settings-full-name");
    const emailEl = document.getElementById("settings-email");
    if (nameEl) nameEl.value = user.full_name || user.first_name || "";
    if (emailEl) emailEl.value = user.email || "";

    const panel = document.getElementById("billing-panel");
    if (panel) {
      panel.innerHTML =
        '<div class="bg-white rounded-2xl border p-5">' +
        '<p class="text-sm text-gray-500">Plan</p>' +
        '<p class="text-xl font-bold capitalize">' + (user.plan || "free") + "</p>" +
        '<p class="text-sm mt-2">Generations: ' +
        (user.generations_used ?? 0) + " / " + (user.generations_limit ?? 10) +
        "</p></div>";
    }
  });
</script>
```

---

### `POST /api/auth/password-reset/` — Request reset email

**Page:** `signin.html` · **Target:** “Forgot?” link — add `#reset-email` input in a small modal, or reuse `#login-email`

```html
<script>
  document.addEventListener("DOMContentLoaded", function () {
    const forgot = document.querySelector('#login a[href="#"]');
    forgot?.addEventListener("click", async function (e) {
      e.preventDefault();
      const email = document.getElementById("login-email").value.trim().toLowerCase();
      if (!email) return alert("Enter your email first.");
      const API_BASE = "https://ai-ads-studio-kappa.vercel.app/api";
      const res = await fetch(API_BASE + "/auth/password-reset/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
      const data = await res.json().catch(() => ({}));
      alert(data.detail || "Check your email if an account exists.");
    });
  });
</script>
```

---

### `POST /api/auth/password-reset/confirm/` — Set new password

**Page:** custom `reset-password.html` · **Targets:** add `#reset-token`, `#reset-pw`, `#reset-pw2`, `#reset-submit`

```html
<input type="hidden" id="reset-token" />
<input type="password" id="reset-pw" class="border rounded-lg w-full p-3" placeholder="New password" />
<input type="password" id="reset-pw2" class="border rounded-lg w-full p-3 mt-2" placeholder="Confirm" />
<button type="button" id="reset-submit" class="mt-4 w-full py-3 bg-blue-600 text-white rounded-lg">Update password</button>
<script>
  // Set token from URL: ?token=abc
  document.getElementById("reset-token").value =
    new URLSearchParams(location.search).get("token") || "";

  document.getElementById("reset-submit").addEventListener("click", async function () {
    const API_BASE = "https://ai-ads-studio-kappa.vercel.app/api";
    const res = await fetch(API_BASE + "/auth/password-reset/confirm/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        token: document.getElementById("reset-token").value,
        password: document.getElementById("reset-pw").value,
        password_confirm: document.getElementById("reset-pw2").value,
      }),
    });
    const data = await res.json().catch(() => ({}));
    alert(data.detail || (res.ok ? "Password updated" : "Failed"));
    if (res.ok) location.href = "/signin.html";
  });
</script>
```

---

### `POST /api/auth/verify-email/` — Verify email token

**Page:** `verify-email.html` (create) · **Target:** `#verify-token` from `?token=`

```html
<input type="hidden" id="verify-token" />
<script>
  document.getElementById("verify-token").value =
    new URLSearchParams(location.search).get("token") || "";
  (async function () {
    const API_BASE = "https://ai-ads-studio-kappa.vercel.app/api";
    const res = await fetch(API_BASE + "/auth/verify-email/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token: document.getElementById("verify-token").value }),
    });
    const data = await res.json().catch(() => ({}));
    document.body.insertAdjacentHTML(
      "beforeend",
      '<p class="p-8 text-center">' + (data.detail || (res.ok ? "Email verified!" : "Invalid token")) + "</p>"
    );
  })();
</script>
```

---

## Dashboard

### `GET /api/dashboard/` — Dashboard stats

**Page:** `index.html`  
**Target:** `#app-main`

```html
<script>
  document.addEventListener("DOMContentLoaded", async function () {
    const API_BASE = "https://ai-ads-studio-kappa.vercel.app/api";
    const token = localStorage.getItem("access_token");
  if (!token) { window.location.href = "/signin.html"; return; }

    const main = document.getElementById("app-main");
    if (!main) return;

    const res = await fetch(API_BASE + "/dashboard/", {
      headers: { Authorization: "Bearer " + token },
    });
    const d = await res.json().catch(() => ({}));
    if (!res.ok) {
      main.innerHTML = '<p class="text-red-600 p-4">' + (d.detail || "Failed to load") + "</p>";
      return;
    }

    main.innerHTML =
      '<div class="max-w-6xl mx-auto p-4">' +
      '<h2 class="text-xl font-bold mb-4">Dashboard</h2>' +
      '<div class="grid grid-cols-2 md:grid-cols-4 gap-4">' +
      '<div class="bg-white rounded-2xl p-4 border border-gray-200 shadow-sm"><p class="text-xs text-gray-500">Campaigns</p><p class="text-2xl font-bold">' +
      (d.total_campaigns ?? 0) +
      "</p></div>" +
      '<div class="bg-white rounded-2xl p-4 border border-gray-200 shadow-sm"><p class="text-xs text-gray-500">Briefs</p><p class="text-2xl font-bold">' +
      (d.total_briefs ?? 0) +
      "</p></div>" +
      '<div class="bg-white rounded-2xl p-4 border border-gray-200 shadow-sm"><p class="text-xs text-gray-500">Variants</p><p class="text-2xl font-bold">' +
      (d.total_variants ?? 0) +
      "</p></div></div></div></div>";
  });
</script>
```

---

## Analytics

### `GET /api/analytics/` — Spend, impressions, clicks, CTR

**Page:** `analytics.html`  
**Targets:** `#stat-spend`, `#stat-impressions`, `#stat-clicks`, `#stat-ctr`, `#analytics-error`, `#analytics-live-badge`

```html
<script>
  document.addEventListener("DOMContentLoaded", async function () {
    const API_BASE = "https://ai-ads-studio-kappa.vercel.app/api";
    const token = localStorage.getItem("access_token");
    if (!token) { window.location.href = "/signin.html"; return; }

    async function load() {
      const res = await fetch(API_BASE + "/analytics/", {
        headers: { Authorization: "Bearer " + token },
      });
      const data = await res.json().catch(() => ({}));
      const errEl = document.getElementById("analytics-error");

      if (!res.ok) {
        if (errEl) { errEl.classList.remove("hidden"); errEl.textContent = data.detail || "Error"; }
        return;
      }

      document.getElementById("stat-spend").textContent =
        "$" + Number(data.spend || 0).toFixed(0);
      document.getElementById("stat-impressions").textContent = data.impressions ?? 0;
      document.getElementById("stat-clicks").textContent = data.clicks ?? 0;
      document.getElementById("stat-ctr").textContent = (data.ctr ?? 0) + "%";

      const badge = document.getElementById("analytics-live-badge");
      if (badge) badge.classList.remove("hidden"), badge.classList.add("flex");

      if (data.demo_mode && errEl) {
        errEl.classList.remove("hidden");
        errEl.textContent = data.disclaimer || "Demo metrics only.";
      }
    }

    await load();
    setInterval(load, 8000); // live refresh
  });
</script>
```

---

## Generation history

### `GET /api/generations/` — Past AI runs

**Page:** `history.html`  
**Target:** `#app-main`

```html
<script>
  document.addEventListener("DOMContentLoaded", async function () {
    const API_BASE = "https://ai-ads-studio-kappa.vercel.app/api";
    const token = localStorage.getItem("access_token");
    if (!token) { window.location.href = "/signin.html"; return; }
    const main = document.getElementById("app-main");
    if (!main) return;

    const res = await fetch(API_BASE + "/generations/", {
      headers: { Authorization: "Bearer " + token },
    });
    const list = await res.json().catch(() => []);
    if (!res.ok) {
      main.innerHTML = '<p class="text-red-600">Could not load history.</p>';
      return;
    }

    main.innerHTML =
      "<h2 class=\"text-xl font-bold mb-4\">Generation history</h2>" +
      (list.length
        ? list
            .map(function (g) {
              return (
                '<article class="bg-white border border-gray-200 rounded-2xl p-4 mb-3 shadow-sm">' +
                "<p class=\"text-xs text-gray-500\">" +
                new Date(g.created_at).toLocaleString() +
                "</p>" +
                "<p class=\"font-semibold\">" +
                (g.source_type || "brief") +
                " · " +
                (g.variant_count || 0) +
                " variants</p></article>"
              );
            })
            .join("")
        : '<p class="text-gray-500">No generations yet. Create an ad first.</p>');
  });
</script>
```

---

## Ad briefs

### `GET /api/ad-briefs/` — List briefs

**Page:** `history.html` or `index.html` · **Target:** `#app-main`

```html
<script>
  document.addEventListener("DOMContentLoaded", async function () {
    const API_BASE = "https://ai-ads-studio-kappa.vercel.app/api";
    const token = localStorage.getItem("access_token");
    const main = document.getElementById("app-main");
    const res = await fetch(API_BASE + "/ad-briefs/", {
      headers: { Authorization: "Bearer " + token },
    });
    const briefs = await res.json();
    main.innerHTML = briefs
      .map(function (b) {
        return (
          '<div class="bg-white border rounded-xl p-4 mb-2">' +
          "<strong>" +
          b.product_service +
          "</strong> · " +
          b.platform +
          "</div>"
        );
      })
      .join("");
  });
</script>
```

---

### `POST /api/ad-briefs/` — Create brief (form only, no generate)

**Page:** `create-ad.html` · **Targets:** `#prod-service`, `#audience`, `#tone`, `#platform`, `#key-message`

```html
<script>
  document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    form?.addEventListener("submit", async function (e) {
      e.preventDefault();
      const API_BASE = "https://ai-ads-studio-kappa.vercel.app/api";
      const token = localStorage.getItem("access_token");
      const platform = document.getElementById("platform").value;
      const res = await fetch(API_BASE + "/ad-briefs/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer " + token,
        },
        body: JSON.stringify({
          product_service: document.getElementById("prod-service").value,
          audience: document.getElementById("audience").value,
          tone: document.getElementById("tone").value,
          platform: platform === "friendly" ? "meta" : platform,
          key_message: document.getElementById("key-message").value,
        }),
      });
      const brief = await res.json();
      if (res.ok) {
        sessionStorage.setItem("last_brief_id", brief.id);
        alert("Brief saved! ID: " + brief.id);
      } else alert(brief.detail || "Failed");
    });
  });
</script>
```

---

### `POST /api/ad-briefs/{brief_id}/generate/` — Generate variants (full create-ad flow)

**Page:** `create-ad.html`  
**Targets:** form fields + `#variants-panel` (add this id to the right column white box)

```html
<!-- On the right column box: id="variants-panel" -->
<script>
  document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    const submitBtn = form?.querySelector('input[type="submit"]');

    form?.addEventListener("submit", async function (e) {
      e.preventDefault();
      const API_BASE = "https://ai-ads-studio-kappa.vercel.app/api";
      const token = localStorage.getItem("access_token");
      if (!token) { location.href = "/signin.html"; return; }

      const headers = {
        "Content-Type": "application/json",
        Authorization: "Bearer " + token,
      };
      const platform = document.getElementById("platform").value;

      submitBtn.disabled = true;
      submitBtn.value = "Generating…";

      try {
        const briefRes = await fetch(API_BASE + "/ad-briefs/", {
          method: "POST",
          headers,
          body: JSON.stringify({
            product_service: document.getElementById("prod-service").value,
            audience: document.getElementById("audience").value,
            tone: document.getElementById("tone").value,
            platform: platform === "friendly" ? "meta" : platform,
            key_message: document.getElementById("key-message").value,
          }),
        });
        const brief = await briefRes.json();
        if (!briefRes.ok) throw new Error(brief.detail || brief.error || "Brief failed");

        const genRes = await fetch(API_BASE + "/ad-briefs/" + brief.id + "/generate/", {
          method: "POST",
          headers,
          body: "{}",
        });
        const variants = await genRes.json();
        if (!genRes.ok) throw new Error(variants.detail || variants.error || "Generate failed");

        const panel =
          document.getElementById("variants-panel") ||
          document.querySelector(".bg-white.border.rounded-2xl");
        if (panel) {
          panel.innerHTML = variants
            .map(function (v) {
              return (
                '<article class="p-5 border-b">' +
                "<h3 class=\"font-bold text-lg\">" +
                v.headline +
                "</h3>" +
                '<p class="text-gray-600 mt-2 whitespace-pre-wrap">' +
                (v.body || v.primary_text) +
                "</p>" +
                (v.cta
                  ? '<p class="text-blue-600 font-semibold mt-2">' + v.cta + "</p>"
                  : "") +
                "</article>"
              );
            })
            .join("");
        }
      } catch (err) {
        alert(err.message);
      } finally {
        submitBtn.disabled = false;
        submitBtn.value = "Generate ads";
      }
    });
  });
</script>
```

---

### `GET /api/ad-briefs/{brief_id}/` — One brief

**Page:** any · uses `sessionStorage.last_brief_id` from create step

```html
<script>
  (async function () {
    const API_BASE = "https://ai-ads-studio-kappa.vercel.app/api";
    const token = localStorage.getItem("access_token");
    const briefId = sessionStorage.getItem("last_brief_id");
    if (!briefId) return console.warn("No brief id — create a brief first");

    const res = await fetch(API_BASE + "/ad-briefs/" + briefId + "/", {
      headers: { Authorization: "Bearer " + token },
    });
    console.log(await res.json());
  })();
</script>
```

---

### `GET /api/ad-briefs/{brief_id}/variants/` — List variants for a brief

**Page:** `create-ad.html` · **Target:** `#variants-panel`

```html
<script>
  (async function () {
    const API_BASE = "https://ai-ads-studio-kappa.vercel.app/api";
    const token = localStorage.getItem("access_token");
    const briefId = sessionStorage.getItem("last_brief_id");
    const panel = document.getElementById("variants-panel");
    if (!briefId || !panel) return;

    const res = await fetch(API_BASE + "/ad-briefs/" + briefId + "/variants/", {
      headers: { Authorization: "Bearer " + token },
    });
    const variants = await res.json();
    panel.innerHTML = variants
      .map(function (v) {
        return "<h3 class=\"font-bold p-4\">" + v.headline + "</h3><p class=\"px-4 pb-4\">" + v.body + "</p>";
      })
      .join("");
  })();
</script>
```

---

## Campaigns

### `GET /api/campaigns/` — List campaigns

**Page:** `campaigns.html`  
**Targets:** `#campaigns-grid`, `#campaigns-empty`

```html
<script>
  document.addEventListener("DOMContentLoaded", async function () {
    const API_BASE = "https://ai-ads-studio-kappa.vercel.app/api";
    const token = localStorage.getItem("access_token");
    const grid = document.getElementById("campaigns-grid");
    const empty = document.getElementById("campaigns-empty");

    const res = await fetch(API_BASE + "/campaigns/", {
      headers: { Authorization: "Bearer " + token },
    });
    const list = await res.json();
    if (!list.length) {
      empty?.classList.remove("hidden");
      grid.innerHTML = "";
      return;
    }
    empty?.classList.add("hidden");
    grid.innerHTML = list
      .map(function (c) {
        return (
          '<article class="bg-white border border-gray-200 rounded-2xl p-5 shadow-sm" data-campaign-id="' +
          c.id +
          '">' +
          "<h3 class=\"font-bold\">" +
          c.name +
          "</h3>" +
          '<p class="text-sm text-gray-500">' +
          c.status +
          " · " +
          c.platform +
          '</p><button type="button" class="studio-simulate-btn mt-4 text-sm font-semibold text-blue-700 bg-blue-50 py-2 rounded-lg w-full" data-id="' +
          c.id +
          '">Simulate live run</button></article>'
        );
      })
      .join("");
  });
</script>
```

---

### `GET /api/campaigns/?search=` — Search by name

**Page:** `campaigns.html` · add search input: `<input id="campaign-search" class="border rounded-lg px-3 py-2 text-sm" placeholder="Search campaigns" />`

```html
<input id="campaign-search" type="search" placeholder="Search campaigns"
  class="border border-gray-200 rounded-lg px-3 py-2 text-sm mb-4 w-full max-w-xs" />
<script>
  document.getElementById("campaign-search")?.addEventListener("input", async function (e) {
    const q = e.target.value.trim();
    const API_BASE = "https://ai-ads-studio-kappa.vercel.app/api";
    const token = localStorage.getItem("access_token");
    const url = API_BASE + "/campaigns/" + (q ? "?search=" + encodeURIComponent(q) : "");
    const res = await fetch(url, { headers: { Authorization: "Bearer " + token } });
    const list = await res.json();
    document.getElementById("campaigns-grid").innerHTML = list
      .map(function (c) {
        return '<article class="bg-white border rounded-2xl p-5"><h3 class="font-bold">' + c.name + "</h3></article>";
      })
      .join("");
  });
</script>
```

---

### `POST /api/campaigns/` — Create campaign

**Page:** `campaigns.html`  
**Target:** `#studio-create-campaign`

```html
<script>
  document.getElementById("studio-create-campaign")?.addEventListener("click", async function () {
    const name = prompt("Campaign name");
    if (!name) return;
    const API_BASE = "https://ai-ads-studio-kappa.vercel.app/api";
    const token = localStorage.getItem("access_token");
    await fetch(API_BASE + "/campaigns/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + token,
      },
      body: JSON.stringify({ name, platform: "meta", status: "draft" }),
    });
    location.reload(); // or re-run GET list snippet
  });
</script>
```

---

### `GET /api/campaigns/{campaign_id}/` — One campaign

Uses `data-campaign-id` on cards from the list snippet:

```html
<script>
  document.getElementById("campaigns-grid")?.addEventListener("click", async function (e) {
    const card = e.target.closest("[data-campaign-id]");
    if (!card || e.target.classList.contains("studio-simulate-btn")) return;
    const id = card.getAttribute("data-campaign-id");
    const API_BASE = "https://ai-ads-studio-kappa.vercel.app/api";
    const token = localStorage.getItem("access_token");
    const res = await fetch(API_BASE + "/campaigns/" + id + "/", {
      headers: { Authorization: "Bearer " + token },
    });
    alert(JSON.stringify(await res.json(), null, 2));
  });
</script>
```

---

### `PATCH /api/campaigns/{campaign_id}/` — Update campaign

Add edit button: `class="studio-edit-campaign"` with `data-id`

```html
<script>
  document.getElementById("campaigns-grid")?.addEventListener("click", async function (e) {
    const btn = e.target.closest(".studio-edit-campaign");
    if (!btn) return;
    const id = btn.getAttribute("data-id");
    const name = prompt("New name");
    if (!name) return;
    const API_BASE = "https://ai-ads-studio-kappa.vercel.app/api";
    const token = localStorage.getItem("access_token");
    await fetch(API_BASE + "/campaigns/" + id + "/", {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + token,
      },
      body: JSON.stringify({ name }),
    });
    location.reload();
  });
</script>
```

---

### `DELETE /api/campaigns/{campaign_id}/` — Delete campaign

Add button: `class="studio-delete-campaign text-red-600 text-sm mt-2" data-id="..."`

```html
<script>
  document.getElementById("campaigns-grid")?.addEventListener("click", async function (e) {
    const btn = e.target.closest(".studio-delete-campaign");
    if (!btn || !confirm("Delete campaign?")) return;
    const id = btn.getAttribute("data-id");
    const API_BASE = "https://ai-ads-studio-kappa.vercel.app/api";
    const token = localStorage.getItem("access_token");
    await fetch(API_BASE + "/campaigns/" + id + "/", {
      method: "DELETE",
      headers: { Authorization: "Bearer " + token },
    });
    location.reload();
  });
</script>
```

---

### `POST /api/campaigns/{campaign_id}/simulate/` — Simulate metrics

**Page:** `campaigns.html`  
**Target:** `.studio-simulate-btn` (created by list snippet above)

```html
<script>
  document.getElementById("campaigns-grid")?.addEventListener("click", async function (e) {
    const btn = e.target.closest(".studio-simulate-btn");
    if (!btn) return;
    const id = btn.getAttribute("data-id");
    const API_BASE = "https://ai-ads-studio-kappa.vercel.app/api";
    const token = localStorage.getItem("access_token");
    btn.disabled = true;
    const res = await fetch(API_BASE + "/campaigns/" + id + "/simulate/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + token,
      },
      body: "{}",
    });
    btn.disabled = false;
    if (res.ok) alert("Simulated! Check Analytics.");
    else alert("Simulate failed");
  });
</script>
```

---

## Notifications

### `GET /api/notifications/` — All notifications

**Page:** `notification.html`  
**Target:** `#notifications-list`

```html
<script>
  document.addEventListener("DOMContentLoaded", async function () {
    const API_BASE = "https://ai-ads-studio-kappa.vercel.app/api";
    const token = localStorage.getItem("access_token");
    const listEl = document.getElementById("notifications-list");

    const res = await fetch(API_BASE + "/notifications/", {
      headers: { Authorization: "Bearer " + token },
    });
    const list = await res.json();
    listEl.innerHTML = list.length
      ? list
          .map(function (n) {
            return (
              '<div class="py-4 border-b ' +
              (n.is_read ? "opacity-60" : "") +
              '" data-id="' +
              n.id +
              '">' +
              "<p class=\"font-semibold\">" +
              n.title +
              "</p><p class=\"text-sm text-gray-500\">" +
              n.message +
              "</p></div>"
            );
          })
          .join("")
      : '<p class="text-center text-gray-500 py-8">No notifications yet.</p>';
  });
</script>
```

---

### `GET /api/notifications/?unread=true` — Unread only

**Page:** `notification.html`  
**Target:** `#notifications-unread-tab` (tab button)

```html
<script>
  document.getElementById("notifications-unread-tab")?.addEventListener("click", async function () {
    const API_BASE = "https://ai-ads-studio-kappa.vercel.app/api";
    const token = localStorage.getItem("access_token");
    const res = await fetch(API_BASE + "/notifications/?unread=true", {
      headers: { Authorization: "Bearer " + token },
    });
    const list = await res.json();
    document.getElementById("notifications-list").innerHTML = list
      .map(function (n) {
        return '<div class="py-4 font-semibold">' + n.title + "</div>";
      })
      .join("");
  });
</script>
```

---

### `PATCH /api/notifications/{notification_id}/read/` — Mark read

Click a row in `#notifications-list` (uses `data-id` from list snippet):

```html
<script>
  document.getElementById("notifications-list")?.addEventListener("click", async function (e) {
    const row = e.target.closest("[data-id]");
    if (!row) return;
    const id = row.getAttribute("data-id");
    const API_BASE = "https://ai-ads-studio-kappa.vercel.app/api";
    const token = localStorage.getItem("access_token");
    await fetch(API_BASE + "/notifications/" + id + "/read/", {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + token,
      },
      body: "{}",
    });
    row.classList.add("opacity-60");
  });
</script>
```

---

## Billing (Pro)

### `GET /api/auth/billing/status/` — Plan + limits

**Page:** `settings.html` · **Target:** `#billing-panel`

```html
<script>
  document.addEventListener("DOMContentLoaded", async function () {
    const API_BASE = "https://ai-ads-studio-kappa.vercel.app/api";
    const token = localStorage.getItem("access_token");
    const panel = document.getElementById("billing-panel");
    const res = await fetch(API_BASE + "/auth/billing/status/", {
      headers: { Authorization: "Bearer " + token },
    });
    const data = await res.json();
    if (panel && res.ok) {
      panel.innerHTML =
        '<p class="text-sm">Plan: <strong>' +
        data.plan +
        "</strong></p><p class=\"text-sm\">Used: " +
        data.generations_used +
        " / " +
        data.generations_limit +
        "</p>";
    }
  });
</script>
```

---

### `POST /api/auth/billing/checkout/` — Upgrade to Pro

**Page:** `pricing.html`  
**Target:** `#btn-upgrade`

```html
<script>
  document.getElementById("btn-upgrade")?.addEventListener("click", async function () {
    const API_BASE = "https://ai-ads-studio-kappa.vercel.app/api";
    const token = localStorage.getItem("access_token");
    const res = await fetch(API_BASE + "/auth/billing/checkout/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + token,
      },
      body: JSON.stringify({}),
    });
    const data = await res.json();
    if (data.url) window.location.href = data.url;
    else alert(data.detail || "Checkout unavailable");
  });
</script>
```

---

### `POST /api/auth/billing/portal/` — Manage subscription

**Page:** `settings.html` · add `<button id="btn-billing-portal" class="text-blue-600 text-sm font-medium">Manage billing</button>` inside `#billing-panel`

```html
<button type="button" id="btn-billing-portal" class="text-blue-600 text-sm font-medium mt-2">Manage billing</button>
<script>
  document.getElementById("btn-billing-portal")?.addEventListener("click", async function () {
    const API_BASE = "https://ai-ads-studio-kappa.vercel.app/api";
    const token = localStorage.getItem("access_token");
    const res = await fetch(API_BASE + "/auth/billing/portal/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + token,
      },
      body: JSON.stringify({}),
    });
    const data = await res.json();
    if (data.url) window.location.href = data.url;
  });
</script>
```

---

## Projects (legacy demo — no login)

These endpoints are **public** in the API. Add your own IDs if you build a projects page.

### `GET /api/projects/`

```html
<script>
  (async function () {
    const res = await fetch("https://ai-ads-studio-kappa.vercel.app/api/projects/");
    console.log(await res.json());
  })();
</script>
```

### `POST /api/projects/`

```html
<!-- inputs: #project-name, #project-brand -->
<script>
  document.querySelector("form")?.addEventListener("submit", async function (e) {
    e.preventDefault();
    const res = await fetch("https://ai-ads-studio-kappa.vercel.app/api/projects/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: document.getElementById("project-name").value,
        brand: document.getElementById("project-brand").value,
      }),
    });
    console.log(await res.json());
  });
</script>
```

### `POST /api/projects/{project_id}/generate/`

```html
<script>
  (async function () {
    const projectId = "PASTE-UUID-HERE";
    const res = await fetch(
      "https://ai-ads-studio-kappa.vercel.app/api/projects/" + projectId + "/generate/",
      { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" }
    );
    console.log(await res.json());
  })();
</script>
```

---

## All-in-one alternative

If you prefer **one file** that wires every page automatically, use [`student-api.js`](./student-api.js) instead of copying snippets:

```html
<script>window.API_BASE = "https://ai-ads-studio-kappa.vercel.app/api";</script>
<script src="student-api.js"></script>
```

---

## Typical order for students

1. `POST /auth/register/` on `signup.html`
2. `POST /auth/login/` on `signin.html`
3. `GET /dashboard/` on `index.html`
4. `POST /ad-briefs/` + `POST …/generate/` on `create-ad.html`
5. `GET /campaigns/`, `GET /analytics/`, `GET /notifications/`

More request/response detail: [API_GUIDE.md](./API_GUIDE.md)
