"""
Copy frontend2 assets into Django static/templates for local template serving.
Run: python manage.py build_web_templates
"""
import re
import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

URL_MAP = {
    'href="signup.html"': 'href="{% url \'web-signup\' %}"',
    'href="signin.html"': 'href="{% url \'web-signin\' %}"',
    'href="/index.html"': 'href="{% url \'web-home\' %}"',
    'href="/signin.html"': 'href="{% url \'web-signin\' %}"',
    'href="/signup.html"': 'href="{% url \'web-signup\' %}"',
    'href="/create-ad.html"': 'href="{% url \'web-create-ad\' %}"',
    'href="/signin/"': 'href="{% url \'web-signin\' %}"',
    'href="/signup/"': 'href="{% url \'web-signup\' %}"',
    'href="/pricing/"': 'href="{% url \'web-pricing\' %}"',
    'href="/campaigns.html"': 'href="{% url \'web-campaigns\' %}"',
    'href="/analytics.html"': 'href="{% url \'web-analytics\' %}"',
    'href="/notification.html"': 'href="{% url \'web-notifications\' %}"',
    'href="/settings.html"': 'href="{% url \'web-settings\' %}"',
    'href="/history.html"': 'href="{% url \'web-history\' %}"',
    'href="/pricing.html"': 'href="{% url \'web-pricing\' %}"',
}

STATIC_MAP = {
    'href="/favicon.svg"': 'href="{% static \'web/favicon.svg\' %}"',
    'href="/studio.css"': 'href="{% static \'web/studio.css\' %}"',
    'href="/landing.css"': 'href="{% static \'web/landing.css\' %}"',
    'src="/landing.js"': 'src="{% static \'web/landing.js\' %}"',
    'href="/studio.css" />': 'href="{% static \'web/studio.css\' %}" />',
    'src="/config.js"': '',
    'src="/ui.js"': '',
    'src="/auth.js"': '',
    'src="/product.js"': '',
    'src="/app.js"': '',
    'src="/nav.js"': '',
    'src="/student-api.js"': '',
}

APP_PAGES = {
    "index.html": ("dashboard.html", "dashboard"),
    "create-ad.html": ("create_ad.html", "create-ad"),
    "campaigns.html": ("campaigns.html", "campaigns"),
    "analytics.html": ("analytics.html", "analytics"),
    "notification.html": ("notifications.html", "notifications"),
    "settings.html": ("settings.html", "settings"),
    "history.html": ("history.html", "history"),
    "Dashboard.html": ("dashboard.html", "dashboard"),
}

AUTH_PAGES = {
    "signin.html": "signin.html",
    "signup.html": "signup.html",
}

SIMPLE_PAGES = {
    "pricing.html": ("pricing.html", "Pricing"),
    "landing.html": ("landing.html", "Landing"),
    "verify-email.html": ("verify_email.html", "Verify email"),
}


def _patch(content: str) -> str:
    for old, new in URL_MAP.items():
        content = content.replace(old, new)
    for old, new in STATIC_MAP.items():
        content = content.replace(old, new)
    content = re.sub(r"\n\s*\n\s*\n", "\n\n", content)
    return content


def _extract_main(html: str) -> str:
    m = re.search(r"<main[^>]*>(.*)</main>", html, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return "<p class=\"text-gray-500\">Content missing — re-run build_web_templates.</p>"


class Command(BaseCommand):
    help = "Sync frontend2 HTML into Django templates and static files."

    def handle(self, *args, **options):
        root = Path(settings.FRONTEND_ROOT)
        if not root.is_dir():
            self.stderr.write(
                self.style.ERROR(
                    f"FRONTEND_ROOT not found: {root}\n"
                    "  Local: run from repo with frontend2/, or powershell -File backend/scripts/prepare-vercel-frontend.ps1\n"
                    "  Vercel (backend root): copy frontend2 into backend/frontend2 and commit, or set Root Directory to repo root."
                )
            )
            raise SystemExit(1)

        static_dest = Path(settings.BASE_DIR) / "studio" / "static" / "web"
        templates_dest = Path(settings.BASE_DIR) / "studio" / "templates" / "web"
        static_dest.mkdir(parents=True, exist_ok=True)
        templates_dest.mkdir(parents=True, exist_ok=True)

        for name in (
            "studio.css",
            "landing.css",
            "landing.js",
            "ui.js",
            "auth.js",
            "app.js",
            "product.js",
            "nav.js",
            "favicon.svg",
        ):
            src = root / name
            if src.is_file():
                shutil.copy2(src, static_dest / name)

        index_path = root / "index.html"
        if index_path.is_file():
            idx = index_path.read_text(encoding="utf-8", errors="replace")
            partials = templates_dest / "partials"
            partials.mkdir(parents=True, exist_ok=True)
            desk = re.search(
                r'(<nav class="hidden md:flex.*?</nav>)', idx, re.DOTALL | re.IGNORECASE
            )
            if desk:
                (partials / "sidebar_desktop.html").write_text(desk.group(1), encoding="utf-8")
            overlay_m = re.search(
                r'(<div id="overlay".*?</nav>)', idx, re.DOTALL | re.IGNORECASE
            )
            if overlay_m:
                (partials / "sidebar_mobile.html").write_text(overlay_m.group(1), encoding="utf-8")

        nav_src = static_dest / "nav.js"
        if nav_src.is_file():
            text = nav_src.read_text(encoding="utf-8")
            for old, new in (
                ('"/create-ad.html"', '"/create-ad/"'),
                ('"/pricing.html"', '"/pricing/"'),
                ('"/settings.html"', '"/settings/"'),
                ('"/signin.html"', '"/signin/"'),
                ('go("/signin.html")', 'go("/signin/")'),
                ('go("/create-ad.html")', 'go("/create-ad/")'),
            ):
                text = text.replace(old, new)
            nav_src.write_text(text, encoding="utf-8")

        for src_name, (dest_name, _nav) in APP_PAGES.items():
            src = root / src_name
            if not src.is_file():
                continue
            html = src.read_text(encoding="utf-8", errors="replace")
            main = _patch(_extract_main(html))
            out = (
                "{% extends \"web/base_app.html\" %}\n"
                "{% block title %}AI Ads Studio{% endblock %}\n"
                "{% block main %}\n"
                f"{main}\n"
                "{% endblock %}\n"
            )
            (templates_dest / dest_name).write_text(out, encoding="utf-8")
            self.stdout.write(f"  page: {dest_name}")

        for src_name, dest_name in AUTH_PAGES.items():
            src = root / src_name
            if not src.is_file():
                continue
            html = src.read_text(encoding="utf-8", errors="replace")
            body_m = re.search(r"<body[^>]*>(.*)</body>", html, re.DOTALL | re.IGNORECASE)
            body = _patch(body_m.group(1).strip() if body_m else html)
            if src_name == "signin.html":
                out = (
                    "{% extends \"web/base_auth.html\" %}\n"
                    "{% block title %}Sign in{% endblock %}\n"
                    "{% block body %}\n"
                    f"{body}\n"
                    "{% endblock %}\n"
                )
            else:
                out = (
                    "{% extends \"web/base_auth.html\" %}\n"
                    "{% block title %}Sign up{% endblock %}\n"
                    "{% block body %}\n"
                    f"{body}\n"
                    "{% endblock %}\n"
                )
            (templates_dest / dest_name).write_text(out, encoding="utf-8")
            self.stdout.write(f"  auth: {dest_name}")

        for src_name, (dest_name, page_title) in SIMPLE_PAGES.items():
            src = root / src_name
            if not src.is_file():
                continue
            html = src.read_text(encoding="utf-8", errors="replace")
            body_m = re.search(r"<body[^>]*>(.*)</body>", html, re.DOTALL | re.IGNORECASE)
            body = _patch(body_m.group(1).strip() if body_m else html)
            extra_head = ""
            extra_js = ""
            if src_name == "landing.html":
                extra_head = (
                    "{% block extra_head %}\n"
                    "  <link rel=\"stylesheet\" href=\"{% static 'web/landing.css' %}\" />\n"
                    "  <link rel=\"preconnect\" href=\"https://fonts.googleapis.com\" />\n"
                    "  <link href=\"https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap\" rel=\"stylesheet\" />\n"
                    "{% endblock %}\n"
                    "{% block body_class %}bg-white min-h-screen{% endblock %}\n"
                )
                extra_js = (
                    "{% block extra_js %}\n"
                    "  <script src=\"{% static 'web/landing.js' %}\"></script>\n"
                    "{% endblock %}\n"
                )
            load_static = "{% load static %}\n" if src_name == "landing.html" else ""
            out = (
                "{% extends \"web/base_simple.html\" %}\n"
                + load_static
                + "{% block title %}" + page_title + "{% endblock %}\n"
                + extra_head
                + "{% block body %}\n"
                f"{body}\n"
                "{% endblock %}\n"
                + extra_js
            )
            (templates_dest / dest_name).write_text(out, encoding="utf-8")
            self.stdout.write(f"  simple: {dest_name}")

        self.stdout.write(self.style.SUCCESS("Done. Run: python manage.py runserver"))
