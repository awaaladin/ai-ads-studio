/**
 * Loads real data from the API while preserving student HTML layouts.
 */
(function () {
  const API = () => window.API_BASE || "/api";

  function token() {
    return localStorage.getItem("access_token");
  }

  function headers() {
    const h = { "Content-Type": "application/json" };
    if (token()) h.Authorization = "Bearer " + token();
    return h;
  }

  async function api(path, options = {}) {
    const res = await fetch(API() + path, {
      ...options,
      headers: { ...headers(), ...(options.headers || {}) },
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      const msg =
        typeof data.detail === "string"
          ? data.detail
          : data.detail
            ? JSON.stringify(data.detail)
            : res.statusText;
      throw new Error(msg);
    }
    return data;
  }

  function page() {
    const p = window.location.pathname;
    if (p.includes("create-ad")) return "create-ad";
    if (p.includes("notification")) return "notifications";
    if (p.includes("settings")) return "settings";
    if (p.includes("campaigns")) return "campaigns";
    if (p.includes("analytics") || p.includes("Dashboard.html")) return "analytics";
    if (p.includes("index") || p.endsWith("/")) return "dashboard";
    return "other";
  }

  function mainEl() {
    return document.getElementById("app-main") || document.getElementById("app-hydrate");
  }

  function setMain(html) {
    const m = mainEl();
    if (m) m.innerHTML = html;
  }

  function formatNum(n) {
    if (n >= 1000000) return (n / 1000000).toFixed(1) + "M";
    if (n >= 1000) return (n / 1000).toFixed(1) + "k";
    return String(n);
  }

  function formatMoney(v) {
    const n = parseFloat(v) || 0;
    return "$" + n.toLocaleString(undefined, { maximumFractionDigits: 0 });
  }

  function statCard(title, value, sub) {
    return `<div class="bg-white rounded-2xl border border-gray-200 p-5 shadow-sm">
      <p class="text-xs uppercase tracking-wide text-gray-400 font-semibold">${title}</p>
      <p class="text-2xl font-bold text-gray-900 mt-1">${value}</p>
      ${sub ? `<p class="text-sm text-gray-500 mt-1">${sub}</p>` : ""}
    </div>`;
  }

  async function renderDashboard() {
    setMain('<p class="text-gray-500">Loading dashboard...</p>');
    try {
      const d = await api("/dashboard/");
      const a = d.analytics || {};
      const briefs = d.recent_briefs || [];
      const campaigns = d.recent_campaigns || [];

      const briefList =
        briefs.length === 0
          ? `<p class="text-gray-500 text-sm">No ad briefs yet. <a href="/create-ad.html" class="text-blue-600 font-semibold">Create your first ad</a></p>`
          : briefs
              .map(
                (b) => `<div class="border border-gray-100 rounded-xl p-4 mb-2">
              <p class="font-semibold">${b.product_service}</p>
              <p class="text-sm text-gray-500">${b.audience} · ${b.platform}</p>
            </div>`
              )
              .join("");

      setMain(`
        <div class="max-w-6xl mx-auto">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          ${statCard("Campaigns", d.total_campaigns, (d.active_campaigns || 0) + " active")}
          ${statCard("Ad briefs", d.total_briefs, "")}
          ${statCard("Variants", d.total_variants, "")}
          ${statCard("CTR", (a.ctr || 0) + "%", formatNum(a.impressions || 0) + " impressions")}
        </div>
        <div class="grid md:grid-cols-2 gap-6">
          <div class="bg-white rounded-2xl border border-gray-200 p-5">
            <h2 class="font-bold mb-3">Recent briefs</h2>${briefList}
          </div>
          <div class="bg-white rounded-2xl border border-gray-200 p-5">
            <h2 class="font-bold mb-3">Recent campaigns</h2>
            ${
              campaigns.length
                ? campaigns
                    .map(
                      (c) => `<div class="border border-gray-100 rounded-xl p-4 mb-2">
                <p class="font-semibold">${c.name}</p>
                <p class="text-sm text-gray-500">${c.status} · ${c.platform}</p>
              </div>`
                    )
                    .join("")
                : '<p class="text-gray-500 text-sm">No campaigns yet. <a href="/campaigns.html" class="text-blue-600 font-semibold">View campaigns</a></p>'
            }
          </div>
        </div>
        </div>
      `);
    } catch (e) {
      setMain(`<p class="text-red-600">Could not load dashboard: ${e.message}</p>`);
    }
  }

  function campaignCard(c) {
    const statusColors = {
      active: "bg-green-100 text-green-700",
      paused: "bg-yellow-100 text-yellow-700",
      draft: "bg-gray-100 text-gray-600",
    };
    const badge = statusColors[c.status] || statusColors.draft;
    return `<div class="bg-white rounded-2xl border border-gray-200 p-5 shadow-sm hover:shadow-md transition">
      <div class="flex justify-between items-start mb-3">
        <h3 class="font-bold text-gray-900">${c.name}</h3>
        <span class="text-xs font-semibold px-2 py-1 rounded-full ${badge}">${c.status}</span>
      </div>
      <p class="text-sm text-gray-500 mb-4">${c.platform || "Multi-platform"}</p>
      <div class="grid grid-cols-3 gap-2 text-center text-sm">
        <div><p class="text-gray-400 text-xs">Impressions</p><p class="font-semibold">${formatNum(c.impressions || 0)}</p></div>
        <div><p class="text-gray-400 text-xs">Clicks</p><p class="font-semibold">${formatNum(c.clicks || 0)}</p></div>
        <div><p class="text-gray-400 text-xs">Spend</p><p class="font-semibold">${formatMoney(c.spend)}</p></div>
      </div>
    </div>`;
  }

  async function renderCampaigns() {
    const grid = document.getElementById("campaigns-grid");
    const empty = document.getElementById("campaigns-empty");
    if (!grid) return;

    try {
      const list = await api("/campaigns/");
      if (!list.length) {
        grid.innerHTML = "";
        if (empty) empty.classList.remove("hidden");
        return;
      }
      if (empty) empty.classList.add("hidden");
      grid.innerHTML = list.map(campaignCard).join("");
    } catch (e) {
      grid.innerHTML = `<p class="text-red-600 col-span-full">${e.message}</p>`;
    }
  }

  function barChart(container, values, labels) {
    if (!container) return;
    const max = Math.max(...values, 1);
    if (!values.some((v) => v > 0)) {
      container.innerHTML =
        '<p class="text-gray-400 text-sm text-center py-8">No performance data yet. Create a campaign to see charts.</p>';
      return;
    }
    container.innerHTML = values
      .map((v, i) => {
        const h = Math.max(8, Math.round((v / max) * 100));
        return `<div class="flex-1 flex flex-col items-center gap-1">
          <div class="w-full bg-blue-500 rounded-t-md transition-all" style="height:${h}%"></div>
          <span class="text-[10px] text-gray-400">${labels[i] || ""}</span>
        </div>`;
      })
      .join("");
  }

  function platformBars(container, campaigns) {
    if (!container) return;
    const byPlatform = {};
    campaigns.forEach((c) => {
      const p = c.platform || "Other";
      byPlatform[p] = (byPlatform[p] || 0) + parseFloat(c.spend || 0);
    });
    const entries = Object.entries(byPlatform);
    if (!entries.length) {
      container.innerHTML =
        '<p class="text-gray-400 text-sm">No spend data yet.</p>';
      return;
    }
    const max = Math.max(...entries.map(([, v]) => v), 1);
    container.innerHTML = entries
      .map(([name, spend]) => {
        const pct = Math.round((spend / max) * 100);
        return `<div>
          <div class="flex justify-between text-xs mb-1"><span>${name}</span><span>${formatMoney(spend)}</span></div>
          <div class="h-2 bg-gray-100 rounded-full"><div class="h-2 bg-blue-600 rounded-full" style="width:${pct}%"></div></div>
        </div>`;
      })
      .join("");
  }

  async function renderAnalytics() {
    try {
      const data = await api("/analytics/");
      const spend = document.getElementById("stat-spend");
      const impressions = document.getElementById("stat-impressions");
      const clicks = document.getElementById("stat-clicks");
      const ctr = document.getElementById("stat-ctr");
      if (spend) spend.textContent = formatMoney(data.spend);
      if (impressions) impressions.textContent = formatNum(data.impressions || 0);
      if (clicks) clicks.textContent = formatNum(data.clicks || 0);
      if (ctr) ctr.textContent = (data.ctr || 0) + "%";

      const campaigns = data.campaigns || [];
      const impVals = campaigns.slice(0, 7).map((c) => c.impressions || 0);
      const labels = campaigns.slice(0, 7).map((c) => (c.name || "").slice(0, 6));
      if (!impVals.length) {
        barChart(document.getElementById("performance-chart"), [0, 0, 0, 0, 0, 0, 0], ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]);
      } else {
        barChart(document.getElementById("performance-chart"), impVals, labels);
      }
      platformBars(document.getElementById("platform-chart"), campaigns);

      const activity = document.getElementById("analytics-activity");
      if (activity) {
        if (!campaigns.length) {
          activity.innerHTML =
            '<p class="text-gray-500 text-sm py-4 text-center">No recent activity. Start by creating a campaign.</p>';
        } else {
          activity.innerHTML = campaigns
            .slice(0, 5)
            .map(
              (c) => `<div class="flex justify-between py-3">
              <div><p class="font-semibold text-sm">${c.name}</p><p class="text-xs text-gray-500">${c.status} · ${c.platform}</p></div>
              <p class="text-sm text-gray-600">${formatNum(c.impressions || 0)} imp.</p>
            </div>`
            )
            .join("");
        }
      }
    } catch (e) {
      const root = document.getElementById("app-hydrate");
      if (root) {
        const err = document.createElement("p");
        err.className = "text-red-600 p-4";
        err.textContent = "Could not load analytics: " + e.message;
        root.prepend(err);
      }
    }
  }

  async function renderSettings() {
    try {
      const user = await api("/auth/me/");
      const fullName = [user.first_name, user.last_name].filter(Boolean).join(" ") || user.username;
      const nameInput = document.getElementById("settings-full-name");
      const emailInput = document.getElementById("settings-email");
      const preview = document.getElementById("profilePreview");
      if (nameInput) nameInput.value = fullName;
      if (emailInput) emailInput.value = user.email || "";
      if (preview) {
        preview.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(fullName)}&background=2563eb&color=fff&size=150`;
        preview.alt = fullName;
      }
    } catch (e) {
      console.error("Settings load failed", e);
    }
  }

  async function renderCreateAd() {
    const main = mainEl() || document.querySelector("main.flex-1");
    if (!main) return;

    let panel = document.getElementById("variants-panel");
    if (!panel) {
      const cols = main.querySelector(".grid");
      if (cols && cols.children.length > 1) {
        panel = cols.children[1];
        panel.id = "variants-panel";
      }
    }

    const form = main.querySelector("form");
    if (!form) return;

    form.removeAttribute("action");
    const handler = async (e) => {
      e.preventDefault();
      const btn = form.querySelector('input[type="submit"], button[type="submit"]');
      if (btn) {
        btn.disabled = true;
        btn.textContent = "Generating...";
      }
      try {
        const brief = await api("/ad-briefs/", {
          method: "POST",
          body: JSON.stringify({
            product_service: document.getElementById("prod-service")?.value,
            audience: document.getElementById("audience")?.value,
            tone: document.getElementById("tone")?.value,
            platform: document.getElementById("platform")?.value,
            key_message: document.getElementById("key-message")?.value || "",
          }),
        });
        const variants = await api(`/ad-briefs/${brief.id}/generate/`, { method: "POST" });
        if (!panel) return;
        if (!variants?.length) {
          panel.innerHTML =
            '<div class="bg-white p-8 rounded-2xl text-center text-gray-500">No variants returned. Check GROQ_API_KEY in backend .env</div>';
          return;
        }
        panel.innerHTML =
          '<h1 class="font-bold mb-5">Generated variants</h1>' +
          variants
            .map(
              (v) => `<div class="bg-white rounded-2xl border border-gray-200 p-5 mb-4">
            <h3 class="font-bold text-lg">${v.headline}</h3>
            <p class="text-gray-600 mt-2 whitespace-pre-wrap">${v.body}</p>
            ${v.cta ? `<p class="text-blue-600 font-semibold mt-3">${v.cta}</p>` : ""}
          </div>`
            )
            .join("");
      } catch (err) {
        alert("Generate failed: " + err.message);
      } finally {
        if (btn) {
          btn.disabled = false;
          btn.textContent = "Generate";
        }
      }
    };
    form.addEventListener("submit", handler);
    form.querySelectorAll('input[type="submit"]').forEach((b) => b.addEventListener("click", handler));
  }


  function timeAgo(iso) {
    if (!iso) return "";
    const diff = Date.now() - new Date(iso).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return "Just now";
    if (mins < 60) return `${mins}m ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs}h ago`;
    const days = Math.floor(hrs / 24);
    if (days === 1) return "Yesterday";
    return `${days} days ago`;
  }

  function notificationStyle(title, message) {
    const t = `${title} ${message}`.toLowerCase();
    if (/ctr|performance|jump|outperform|benchmark/.test(t)) {
      return { bg: "bg-green-50", icon: "fa-arrow-trend-up", color: "text-green-500" };
    }
    if (/variant|generated|ad |campaign|brief/.test(t)) {
      return { bg: "bg-blue-50", icon: "fa-bullhorn", color: "text-blue-500" };
    }
    if (/invoice|billing|payment/.test(t)) {
      return { bg: "bg-yellow-50", icon: "fa-folder-closed", color: "text-yellow-500" };
    }
    if (/joined|invite|team|user/.test(t)) {
      return { bg: "bg-gray-100", icon: "fa-user-plus", color: "text-gray-600" };
    }
    if (/expired|error|warning|reconnect|failed/.test(t)) {
      return { bg: "bg-red-50", icon: "fa-triangle-exclamation", color: "text-red-500" };
    }
    return { bg: "bg-blue-50", icon: "fa-bell", color: "text-blue-500" };
  }

  function notificationRow(n, isLast) {
    const style = notificationStyle(n.title, n.message);
    const unread = !n.is_read;
    const border = isLast ? "" : '<div class="border-b border-gray-100"></div>';
    const dot = unread ? '<div class="rounded-full bg-blue-500 h-2 w-2"></div>' : "";
    return (
      '<div class="notebar-div flex justify-between gap-4 p-5 md:p-6' +
      (unread ? "" : " opacity-75") +
      '">' +
      '<div class="flex gap-4">' +
      '<div class="w-12 h-12 md:w-14 md:h-14 ' +
      style.bg +
      ' rounded-2xl flex items-center justify-center shrink-0">' +
      '<i class="fa-solid ' +
      style.icon +
      " " +
      style.color +
      ' text-lg"></i></div>' +
      "<div>" +
      '<div class="flex items-center gap-2 flex-wrap">' +
      '<h3 class="text-sm md:text-lg font-bold text-gray-900">' +
      n.title +
      "</h3>" +
      dot +
      "</div>" +
      '<p class="text-gray-500 text-xs md:text-sm mt-1 leading-6">' +
      n.message +
      "</p></div></div>" +
      '<p class="text-gray-400 text-xs md:text-sm whitespace-nowrap">' +
      timeAgo(n.created_at) +
      "</p></div>" +
      border
    );
  }

  async function renderNotifications() {
    const listEl = document.getElementById("notifications-list");
    if (!listEl) return;

    try {
      const list = await api("/notifications/");
      const unread = list.filter((n) => !n.is_read).length;

      const badge = document.getElementById("notifications-new-badge");
      const tabBadge = document.getElementById("notifications-unread-tab");
      if (badge) {
        if (unread > 0) {
          badge.textContent = unread + " new";
          badge.classList.remove("hidden");
        } else {
          badge.classList.add("hidden");
        }
      }
      if (tabBadge) {
        if (unread > 0) {
          tabBadge.textContent = String(unread);
          tabBadge.classList.remove("hidden");
        } else {
          tabBadge.classList.add("hidden");
        }
      }

      if (!list.length) {
        listEl.innerHTML =
          '<p class="text-gray-500 text-center py-12 text-sm">No notifications yet. Create a campaign or generate an ad to see updates here.</p>';
        return;
      }

      listEl.innerHTML = list
        .map(function (n, i) {
          return notificationRow(n, i === list.length - 1);
        })
        .join("");
    } catch (e) {
      listEl.innerHTML =
        '<p class="text-red-600 text-center py-8 text-sm">' + e.message + "</p>";
    }
  }

  async function init() {
    if (!token()) return;
    const p = page();
    if (p === "dashboard") await renderDashboard();
    else if (p === "create-ad") await renderCreateAd();
    else if (p === "notifications") await renderNotifications();
    else if (p === "settings") await renderSettings();
    else if (p === "campaigns") await renderCampaigns();
    else if (p === "analytics") await renderAnalytics();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
