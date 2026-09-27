import io
from typing import Optional

try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
    WEASYPRINT_ERROR = None
except Exception as e:
    WEASYPRINT_AVAILABLE = False
    WEASYPRINT_ERROR = str(e)


def is_pdf_available() -> bool:
    """Returns True if WeasyPrint and system rendering libraries are functional."""
    return WEASYPRINT_AVAILABLE


def html_to_pdf_bytes(html_content: str, document_type: str = "resume") -> Optional[io.BytesIO]:
    """
    Compiles an HTML snippet into print-ready PDF bytes.
    document_type can be 'resume' or 'cover_letter'.
    """
    if not WEASYPRINT_AVAILABLE:
        return None

    if document_type == "resume":
        page_css = """
        @page {
            size: A4;
            margin: 12mm 14mm;
        }
        *, *::before, *::after {
            box-sizing: border-box;
        }
        body {
            margin: 0;
            padding: 0;
            font-family: 'Times New Roman', Times, serif;
            color: #111111;
            font-size: 10.5pt;
            line-height: 1.35;
        }
        .resume-name {
            font-size: 16pt;
            font-weight: bold;
            text-align: center;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 2pt;
        }
        .resume-contact {
            font-size: 9.5pt;
            text-align: center;
            color: #333333;
            margin-bottom: 10pt;
        }
        .resume-section-title {
            font-size: 11pt;
            font-weight: bold;
            text-transform: uppercase;
            border-bottom: 1pt solid #111111;
            padding-bottom: 1pt;
            margin-top: 10pt;
            margin-bottom: 4pt;
            letter-spacing: 0.03em;
        }
        .role-header {
            display: flex;
            justify-content: space-between;
            margin-top: 4pt;
            margin-bottom: 1pt;
        }
        .role-title-company {
            font-weight: bold;
        }
        .role-meta {
            font-style: italic;
            color: #222222;
        }
        .resume-ul {
            margin: 2pt 0 4pt 0;
            padding-left: 18pt;
        }
        .resume-li {
            margin-bottom: 1.5pt;
            line-height: 1.25;
        }
        .inline-category {
            margin: 2pt 0;
            line-height: 1.3;
        }
        """
    else:  # cover_letter
        page_css = """
        @page {
            size: A4;
            margin: 20mm 20mm;
        }
        *, *::before, *::after {
            box-sizing: border-box;
        }
        body {
            margin: 0;
            padding: 0;
            font-family: 'Calibri', 'Inter', sans-serif;
            color: #1A1A1A;
            font-size: 11pt;
            line-height: 1.5;
        }
        p {
            margin-top: 0;
            margin-bottom: 10pt;
        }
        """

    full_document_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
{page_css}
</style>
</head>
<body>
{html_content}
</body>
</html>"""

    pdf_buffer = io.BytesIO()
    HTML(string=full_document_html).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer