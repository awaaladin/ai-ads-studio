import pdfkit
import tempfile
import os

def generate_pdf(business_name: str, colors: str, brochure_content: str) -> str:
    # Use fallback colors if none provided
    if not colors:
        colors = "#4F46E5" # Default indigo
        
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{business_name} Brochure</title>
        <style>
            body {{
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                color: #333;
                line-height: 1.6;
                padding: 40px;
            }}
            h1 {{
                color: {colors};
                border-bottom: 2px solid {colors};
                padding-bottom: 10px;
            }}
            .content {{
                margin-top: 20px;
                white-space: pre-wrap;
            }}
        </style>
    </head>
    <body>
        <h1>{business_name}</h1>
        <div class="content">{brochure_content}</div>
    </body>
    </html>
    """
    
    # Write to a temp file
    fd, path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    
    # Try pdfkit
    try:
        pdfkit.from_string(html_content, path)
    except Exception as e:
        print(f"Error generating PDF (wkhtmltopdf might be missing): {e}")
        # fallback is to just return the empty or failed pdf path
    return path
