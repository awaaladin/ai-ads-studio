from pathlib import Path


def detect_file_type(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext in {".jpg", ".jpeg", ".png", ".gif", ".webp"}:
        return "image"
    if ext in {".mp4", ".mov", ".webm"}:
        return "video"
    if ext == ".pdf":
        return "pdf"
    return "other"


def extract_text_from_upload(uploaded_file) -> str:
    """Best-effort text extraction for supported types."""
    name = uploaded_file.name.lower()
    if name.endswith(".pdf"):
        try:
            from pypdf import PdfReader
            import io

            reader = PdfReader(io.BytesIO(uploaded_file.read()))
            parts = []
            for page in reader.pages[:10]:
                text = page.extract_text()
                if text:
                    parts.append(text)
            uploaded_file.seek(0)
            return "\n".join(parts).strip()
        except Exception:
            uploaded_file.seek(0)
            return f"Uploaded PDF: {uploaded_file.name}"
    if name.endswith((".txt", ".md", ".csv")):
        try:
            return uploaded_file.read().decode("utf-8", errors="ignore")[:8000]
        finally:
            uploaded_file.seek(0)
    return f"Uploaded file: {uploaded_file.name}"
