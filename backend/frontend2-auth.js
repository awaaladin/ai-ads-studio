/**
 * Auth gate + login/register API wiring.
 */
(function () {
  const API_BASE = window.API_BASE || "/api";
  const PUBLIC_PATHS = ["/signin.html", "/signup.html", "/signin", "/signup"];

  function path() {
    return window.location.pathname.replace(/\/+$/, "") || "/";
  }

  function isAuthPage() {
    const p = path();
    return p === "/" || PUBLIC_PATHS.some((x) => p.endsWith(x.replace(".html", "")) || p.endsWith(x));
  }

  function isAppPage() {
    const p = path();
    return (
      p.endsWith("index.html") ||
      p.includes("create-ad") ||
      p.includes("notification") ||
      p.includes("settings") ||
      p.includes("campaigns") ||
      p.includes("analytics") ||
      p.endsWith("Dashboard.html")
    );
  }

  function clearAuth() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  }

  function goSignin() {
    if (!path().endsWith("signin.html") && path() !== "/signin") {
      window.location.replace("/signin.html");
    }
  }

  function goDashboard() {
    window.location.replace("/index.html");
  }

  function formatError(data) {
    if (!data) return "Request failed";
    if (typeof data.detail === "string") return data.detail;
    if (typeof data.detail === "object") {
      return Object.entries(data.detail)
        .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(", ") : v}`)
        .join("\n");
    }
    return JSON.stringify(data);
  }

  async function validateToken() {
    const t = localStorage.getItem("access_token");
    if (!t) return false;
    try {
      const res = await fetch(API_BASE + "/auth/me/", {
        headers: { Authorization: "Bearer " + t },
      });
      if (!res.ok) {
        clearAuth();
        return false;
      }
      return true;
    } catch {
      clearAuth();
      return false;
    }
  }

  async function guard() {
    const loggedIn = await validateToken();

    if (loggedIn) {
      if (isAuthPage()) goDashboard();
      return;
    }

    clearAuth();
    if (
      isAppPage() ||
      (path() === "/" && document.title.includes("AI Ads Studio") && !document.getElementById("login-email"))
    ) {
      goSignin();
    }
  }

  async function apiPost(url, body) {
    const res = await fetch(API_BASE + url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(formatError(data));
    return data;
  }

  async function registerAndLogin(email, password, fullName) {
    await apiPost("/auth/register/", {
      email,
      work_email: email,
      full_name: fullName || "",
      password,
      password_confirm: password,
    });
    const login = await apiPost("/auth/login/", { email, password });
    localStorage.setItem("access_token", login.access);
    localStorage.setItem("refresh_token", login.refresh);
    goDashboard();
  }

  function wireLogin() {
    const email = document.getElementById("login-email");
    const password = document.getElementById("login-pw");
    if (!email || !password) return;

    const btn = document.querySelector("#login button.bg-blue-accent");
    if (!btn) return;

    const handler = async (e) => {
      e.preventDefault();
      try {
        const data = await apiPost("/auth/login/", {
          email: email.value.trim(),
          password: password.value,
        });
        localStorage.setItem("access_token", data.access);
        localStorage.setItem("refresh_token", data.refresh);
        goDashboard();
      } catch (err) {
        alert("Sign in failed: " + err.message);
      }
    };

    btn.addEventListener("click", handler);
    email.addEventListener("keydown", (e) => {
      if (e.key === "Enter") handler(e);
    });
    password.addEventListener("keydown", (e) => {
      if (e.key === "Enter") handler(e);
    });
  }

  function wireSignup() {
    const email = document.getElementById("signup-email");
    const password = document.getElementById("signup-pw");
    const name = document.getElementById("signup-name");
    if (!email || !password) return;

    const handler = async (e) => {
      e.preventDefault();
      const em = email.value.trim();
      if (!em || !em.includes("@")) {
        alert("Please enter a valid email address (e.g. you@company.com).");
        return;
      }
      if (!password.value || password.value.length < 8) {
        alert("Password must be at least 8 characters.");
        return;
      }
      try {
        await registerAndLogin(em, password.value, name?.value?.trim() || "");
      } catch (err) {
        alert("Registration failed: " + err.message);
      }
    };

    const form = document.getElementById("signup-form");
    if (form) {
      form.addEventListener("submit", handler);
      return;
    }

    const btn = document.querySelector("#signup button.bg-blue-accent");
    if (btn) btn.addEventListener("click", handler);
  }

  function init() {
    guard().then(() => {
      wireLogin();
      wireSignup();
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
