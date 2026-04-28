# app/llm.py
import anthropic, json, re

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

SYSTEM_PROMPT = """You are a document data extraction specialist.
Extract structured data from the document text provided.
Return ONLY valid JSON. No markdown, no explanation, no preamble.
If a field cannot be found, use null.
Numbers should be floats (not strings).
Dates should be in YYYY-MM-DD format where possible."""

INVOICE_SCHEMA = """{
  "vendor_name": "string or null",
  "invoice_number": "string or null",
  "invoice_date": "YYYY-MM-DD or null",
  "due_date": "YYYY-MM-DD or null",
  "subtotal": float or null,
  "tax": float or null,
  "total_amount": float or null,
  "currency": "USD/EUR/etc or null",
  "line_items": [
    {"description": "...", "quantity": float, "unit_price": float, "total": float}
  ],
  "raw_confidence": "high | medium | low"
}"""

def extract_invoice_data(text: str) -> dict:
    prompt = f"""Extract invoice data from this document text and return JSON matching this schema:
{INVOICE_SCHEMA}

Document text:
---
{text[:6000]}  
---

Return ONLY the JSON object:"""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = message.content[0].text.strip()
    # Strip markdown fences if present
    raw = re.sub(r'^```json\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    return json.loads(raw)