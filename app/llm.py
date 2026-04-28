# app/llm.py
import google.generativeai as genai
import json, re, os

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.0-flash")

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
    prompt = f"""You are a document data extraction specialist.
Extract invoice data from this document text and return JSON matching this schema exactly:
{INVOICE_SCHEMA}

Rules:
- Return ONLY valid JSON. No markdown, no explanation, no preamble, no backticks.
- If a field cannot be found, use null.
- Numbers must be floats, not strings.
- Dates in YYYY-MM-DD format.

Document text:
---
{text[:6000]}
---

Return ONLY the JSON object:"""

    response = model.generate_content(prompt)
    raw = response.text.strip()

    # Strip markdown fences if Gemini adds them anyway
    raw = re.sub(r'^```json\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)

    return json.loads(raw)