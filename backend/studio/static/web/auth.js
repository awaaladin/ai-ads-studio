/**
 * Auth gate + login/register (Django template routes: /signin/, /signup/).
 */
(function (global) {
  const UI = function () {
    return global.StudioUI;
  };
  function path() {
    return window.location.pathname.replace(/\/+$/, "") || "/";
  }

  function isLanding() {
    return path() === "/" || path() === "";
  }

  function isSignInPage() {
    const p = path();
    return p === "/signin" || p.endsWith("/signin");
  }

  function isSignUpPage() {
    const p = path();
    return p === "/signup" || p.endsWith("/signup");
  }

  function isPricingPage() {
    const p = path();
    return p === "/pricing" || p.endsWith("/pricing");
  }

  function isVerifyEmailPage() {
    const p = path();
    return p === "/verify-email" || p.endsWith("/verify-email");
  }

  /** Pages that must not require login (pricing stays reachable when signed in). */
  function isPublicPage() {
    return isLanding() || isSignInPage() || isSignUpPage() || isPricingPage() || isVerifyEmailPage();
  }

  /** After login, only leave entry/auth pages — not pricing. */
  function shouldRedirectLoggedInToApp() {
    return isLanding() || isSignInPage() || isSignUpPage();
  }

  function isAppPage() {
    const p = path();
    return (
      p.includes("create-ad") ||
      p.includes("settings") ||
      p.endsWith("index.html") ||
      p.endsWith("Dashboard.html")
    );
  }

  function goSignin() {
    window.location.href = "/signin/";
  }

  function goSignup() {
    window.location.href = "/signup/";
  }

  function goAppHome() {
    window.location.href = "/create-ad/";
  }

  function switchPage(page) {
    if (page === "signup") {
      goSignup();
      return false;
    }
    if (page === "login") {
      goSignin();
      return false;
    }
    return false;
  }

  global.switchPage = switchPage;

  async function validateToken() {
    const ui = UI();
    if (!ui || !ui.getToken()) return false;
    try {
      await ui.api("/auth/me/");
      return true;
    } catch {
      ui.clearAuth();
      return false;
    }
  }

  async function guard() {
    const loggedIn = await validateToken();
    if (loggedIn) {
      if (shouldRedirectLoggedInToApp()) goAppHome();
      return;
    }
    UI()?.clearAuth();
    if (isAppPage()) goSignin();
  }

  async function apiPost(url, body) {
    return UI().api(url, { method: "POST", body: JSON.stringify(body) });
  }

  async function registerAndLogin(email, password, fullName) {
    const ui = UI();
    var reg = await fetch(ui.apiBase() + "/auth/register/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: email,
        work_email: email,
        full_name: fullName || "",
        password: password,
        password_confirm: password,
      }),
    });
    var regData = await reg.json().catch(function () {
      return {};
    });
    if (!reg.ok) {
      var em = regData.email;
      if (Array.isArray(em)) em = em[0];
      if (/already exists/i.test(String(em || ""))) {
        throw new Error("This email is already registered. Use Sign in with your password.");
      }
      throw new Error(em || regData.detail || regData.error || "Registration failed");
    }
    if (regData.verification_required) {
      ui.toast(regData.verification_message || "Check your email to verify before signing in.", "success");
      goSignin();
      return;
    }
    let login;
    try {
      login = await apiPost("/auth/login/", { email: email, password: password });
    } catch (err) {
      throw new Error(
        "Account was created but sign-in failed. Try Sign in with the same password."
      );
    }
    UI().setAuth(login.access, login.refresh);
    UI().toast("Account created — welcome!", "success");
    goAppHome();
  }

  function wireLogin() {
    const email = document.getElementById("login-email");
    const password = document.getElementById("login-pw");
    if (!email || !password) return;

    const btn =
      document.querySelector("#signin-panel button.bg-blue-accent") ||
      document.querySelector("#signin-panel button[type=button].bg-blue-accent");
    if (!btn) return;

    const handler = async function (e) {
      if (e) e.preventDefault();
      const ui = UI();
      ui.showAlert("login-error", "", "error");
      const errEl = document.getElementById("login-error");
      if (errEl) errEl.hidden = true;

      const em = email.value.trim().toLowerCase();
      if (!em || !em.includes("@")) {
        ui.showAlert("login-error", "Enter a valid email address.", "error");
        return;
      }
      if (!password.value) {
        ui.showAlert("login-error", "Enter your password.", "error");
        return;
      }

      ui.setButtonLoading(btn, true);
      try {
        const data = await apiPost("/auth/login/", { email: em, password: password.value });
        ui.setAuth(data.access, data.refresh);
        ui.toast("Signed in successfully", "success");
        goAppHome();
      } catch (err) {
        var msg = err.message || "Sign in failed";
        if (
          (err.status === 401 || err.status === 400) &&
          !/verify your email/i.test(msg)
        ) {
          msg =
            "No account with this email on this server. Use Create account first (each server has its own database).";
        }
        ui.showAlert("login-error", msg, "error");
      } finally {
        ui.setButtonLoading(btn, false);
      }
    };

    btn.addEventListener("click", handler);
    email.addEventListener("keydown", function (e) {
      if (e.key === "Enter") handler(e);
    });
    password.addEventListener("keydown", function (e) {
      if (e.key === "Enter") handler(e);
    });
  }

  function wireSignup() {
    const email = document.getElementById("signup-email");
    const password = document.getElementById("signup-pw");
    const name = document.getElementById("signup-name");
    if (!email || !password) return;

    const handler = async function (e) {
      e.preventDefault();
      const ui = UI();
      const terms = document.getElementById("terms");
      if (terms && !terms.checked) {
        ui.showAlert("signup-error", "Please accept the Terms and Privacy Policy.", "error");
        return;
      }
      const em = email.value.trim().toLowerCase();
      if (!em || !em.includes("@")) {
        ui.showAlert("signup-error", "Enter a valid email address.", "error");
        return;
      }
      if (!password.value || password.value.length < 8) {
        ui.showAlert("signup-error", "Password must be at least 8 characters.", "error");
        return;
      }

      const btn = document.querySelector("#signup-form button[type=submit]");
      ui.setButtonLoading(btn, true);
      try {
        await registerAndLogin(em, password.value, name?.value?.trim() || "");
      } catch (err) {
        ui.showAlert("signup-error", err.message || "Registration failed", "error");
      } finally {
        ui.setButtonLoading(btn, false);
      }
    };

    const form = document.getElementById("signup-form");
    if (form) form.addEventListener("submit", handler);
  }

  function injectErrorSlots() {
    const loginForm =
      document.querySelector("#signin-panel .max-w-\\[400px\\]") ||
      document.querySelector("#signin-panel h1")?.parentElement;
    if (loginForm && !document.getElementById("login-error")) {
      const slot = document.createElement("div");
      slot.id = "login-error";
      slot.hidden = true;
      slot.className = "text-sm text-red-600 mb-3 p-2 rounded bg-red-50";
      loginForm.insertBefore(slot, loginForm.children[2] || null);
    }
    const signupH1 = document.querySelector("#signup-form h1");
    if (signupH1 && !document.getElementById("signup-error")) {
      const slot = document.createElement("div");
      slot.id = "signup-error";
      slot.hidden = true;
      slot.className = "text-sm text-red-600 mb-3";
      signupH1.parentElement.insertBefore(slot, signupH1.nextSibling);
    }
  }

  function init() {
    if (!global.StudioUI) {
      console.error("studio: load ui.js before auth.js");
      return;
    }
    injectErrorSlots();
    document.querySelectorAll('a[href="signup.html"]').forEach(function (a) {
      a.setAttribute("href", "/signup/");
    });
    document.querySelectorAll('a[href="signin.html"]').forEach(function (a) {
      a.setAttribute("href", "/signin/");
    });
    guard().then(function () {
      wireLogin();
      wireSignup();
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})(window);
