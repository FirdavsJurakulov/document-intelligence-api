# app/extractor.py
import pdfplumber

def extract_text_from_pdf(file_bytes: bytes) -> tuple[str, int]:
    """Returns (full_text, page_count)"""
    import io
    text_parts = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        page_count = len(pdf.pages)
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
            # Also extract tables
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if row:
                        text_parts.append(" | ".join(
                            str(cell) for cell in row if cell
                        ))
    return "\n".join(text_parts), page_count