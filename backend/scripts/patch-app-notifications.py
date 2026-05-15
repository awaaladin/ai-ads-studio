path = r"c:\Users\Owner\Documents\aiadcreate\ai-ads-studio-1\backend\frontend2-app.js"
text = open(path, encoding="utf-8").read()
start = text.index("  async function renderNotifications()")
end = text.index("  async function init()", start)

new_fn = """
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
    const border = isLast ? "" : '<motion class="border-b border-gray-100"></motion>';
    const dot = unread ? '<motion class="rounded-full bg-blue-500 h-2 w-2"></motion>' : "";
    return (
      '<motion class="notebar-div flex justify-between gap-4 p-5 md:p-6' +
      (unread ? "" : " opacity-75") +
      '">' +
      '<motion class="flex gap-4">' +
      '<motion class="w-12 h-12 md:w-14 md:h-14 ' +
      style.bg +
      ' rounded-2xl flex items-center justify-center shrink-0">' +
      '<i class="fa-solid ' +
      style.icon +
      " " +
      style.color +
      ' text-lg"></i></motion>' +
      "<motion>" +
      '<motion class="flex items-center gap-2 flex-wrap">' +
      '<h3 class="text-sm md:text-lg font-bold text-gray-900">' +
      n.title +
      "</h3>" +
      dot +
      "</motion>" +
      '<p class="text-gray-500 text-xs md:text-sm mt-1 leading-6">' +
      n.message +
      "</p></motion></motion>" +
      '<p class="text-gray-400 text-xs md:text-sm whitespace-nowrap">' +
      timeAgo(n.created_at) +
      "</p></motion>" +
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

"""

# Replace placeholder tag name used to avoid editor autocorrect
new_fn = new_fn.replace("<motion", "<div").replace("</motion>", "</div>")
text = text[:start] + new_fn + text[end:]
open(path, "w", encoding="utf-8").write(text)
print("done")
