import os
import uuid
from pathlib import Path

from django.conf import settings
from django.core.files import File


def _supabase_client():
    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
        return None
    try:
        from supabase import create_client

        return create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
    except Exception:
        return None


def upload_file_to_storage(local_path: str, object_name: str | None = None) -> str:
    object_name = object_name or f"{uuid.uuid4()}{Path(local_path).suffix}"
    client = _supabase_client()

    if client:
        bucket = settings.SUPABASE_STORAGE_BUCKET
        with open(local_path, "rb") as handle:
            client.storage.from_(bucket).upload(object_name, handle)
        return f"{settings.SUPABASE_URL}/storage/v1/object/public/{bucket}/{object_name}"

    media_dir = Path(settings.MEDIA_ROOT) / "uploads"
    media_dir.mkdir(parents=True, exist_ok=True)
    dest = media_dir / object_name
    dest.write_bytes(Path(local_path).read_bytes())
    return f"{settings.MEDIA_URL}uploads/{object_name}"


def save_uploaded_file(uploaded_file, subdir: str = "assets") -> tuple[str, str]:
    """Persist upload to MEDIA_ROOT; returns (relative path, public URL)."""
    ext = Path(uploaded_file.name).suffix
    filename = f"{uuid.uuid4()}{ext}"
    relative = f"{subdir}/{filename}"
    dest_dir = Path(settings.MEDIA_ROOT) / subdir
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / filename

    with open(dest_path, "wb+") as out:
        for chunk in uploaded_file.chunks():
            out.write(chunk)

    public_url = f"{settings.MEDIA_URL}{relative}".replace("\\", "/")
    return str(relative), public_url


def store_pdf_for_model(instance, local_pdf_path: str, field_name: str = "pdf_file"):
    with open(local_pdf_path, "rb") as handle:
        getattr(instance, field_name).save(
            f"{uuid.uuid4()}.pdf",
            File(handle),
            save=False,
        )
