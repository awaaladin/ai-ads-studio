import mimetypes

from django.conf import settings
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import redirect


def api_config_js(request):
    """Instructor/local dev: exposes API base URL without editing student repos."""
    base = request.build_absolute_uri("/api").rstrip("/")
    body = f'window.API_BASE = "{base}";\n'
    return HttpResponse(body, content_type="application/javascript")


def serve_student_frontend(request, path=""):
    """
    Serve pulled HTML from backend/dev-frontend/ (gitignored).
    UI:  http://localhost:8000/
    API: http://localhost:8000/api/
    """
    root = settings.FRONTEND_ROOT
    if not root.is_dir():
        return HttpResponse(
            "<h1>Frontend not pulled yet</h1>"
            "<p>Run: <code>powershell -File backend/scripts/sync-frontend2.ps1</code></p>",
            status=503,
            content_type="text/html",
        )

    safe = (path or "").strip("/")
    if not safe:
        return redirect("/signin.html")
    if ".." in safe.split("/"):
        raise Http404("Invalid path")

    target = (root / safe).resolve()
    if not str(target).startswith(str(root.resolve())):
        raise Http404("Invalid path")

    if target.is_dir():
        target = target / "index.html"

    if not target.is_file():
        raise Http404(f"Page not found: {safe}")

    content_type, _ = mimetypes.guess_type(str(target))
    return FileResponse(open(target, "rb"), content_type=content_type or "application/octet-stream")
