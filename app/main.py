# app/main.py
import time
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.extractor import extract_text_from_pdf
from app.llm import extract_invoice_data
from app.schemas import ExtractionResponse, InvoiceData

app = FastAPI(
    title="Document Intelligence API",
    description="Extract structured data from invoices and business documents using AI.",
    version="1.0.0"
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def health():
    return {"status": "ok", "version": "1.0.0"}

@app.post("/extract/invoice", response_model=ExtractionResponse)
async def extract_invoice(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(400, "Only PDF files are supported")
    
    start = time.time()
    file_bytes = await file.read()

    if len(file_bytes) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(413, "File too large. Maximum size is 10MB.")

    try:
        text, page_count = extract_text_from_pdf(file_bytes)
    except Exception as e:
        raise HTTPException(422, f"PDF parsing failed: {str(e)}")

    if len(text.strip()) < 50:
        raise HTTPException(422, "Could not extract readable text from PDF. Is it a scanned image?")

    try:
        raw_data = extract_invoice_data(text)
        invoice = InvoiceData(**raw_data)
    except Exception as e:
        raise HTTPException(500, f"LLM extraction failed: {str(e)}")

    elapsed_ms = (time.time() - start) * 1000

    return ExtractionResponse(
        filename=file.filename,
        pages=page_count,
        data=invoice,
        processing_time_ms=round(elapsed_ms, 2)
    )

@app.post("/extract/batch")
async def extract_batch(files: list[UploadFile] = File(...)):
    if len(files) > 10:
        raise HTTPException(400, "Maximum 10 files per batch request")
    
    results = []
    for file in files:
        try:
            file_bytes = await file.read()
            text, pages = extract_text_from_pdf(file_bytes)
            raw_data = extract_invoice_data(text)
            invoice = InvoiceData(**raw_data)
            results.append({"filename": file.filename, "status": "success", "data": invoice})
        except Exception as e:
            results.append({"filename": file.filename, "status": "error", "error": str(e)})
    
    return {"processed": len(results), "results": results}