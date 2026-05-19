import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

# Vercel Python runtime expects `app`
app = application

# Apply migrations on cold start (Supabase) when build-time migrate did not run
if os.environ.get("VERCEL") and os.environ.get("RUN_STARTUP_MIGRATE", "true").lower() in (
    "1",
    "true",
    "yes",
):
    try:
        from django.core.management import call_command

        call_command("migrate", "--noinput", verbosity=0)
    except Exception as exc:
        import sys

        print(f"[wsgi] startup migrate failed: {exc}", file=sys.stderr)
