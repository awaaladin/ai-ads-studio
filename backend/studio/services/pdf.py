import os
import tempfile

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def generate_pdf(business_name: str, colors: str, brochure_content: str) -> str:
    fd, path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)

    doc = SimpleDocTemplate(path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = [
        Paragraph(business_name, styles["Title"]),
        Spacer(1, 12),
        Paragraph(brochure_content.replace("\n", "<br/>"), styles["Normal"]),
    ]
    doc.build(story)
    return path
