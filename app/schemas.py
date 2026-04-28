# app/schemas.py
from pydantic import BaseModel
from typing import Optional

class LineItem(BaseModel):
    description: str
    quantity:    Optional[float] = None
    unit_price:  Optional[float] = None
    total:       Optional[float] = None

class InvoiceData(BaseModel):
    vendor_name:    Optional[str]   = None
    invoice_number: Optional[str]   = None
    invoice_date:   Optional[str]   = None
    due_date:       Optional[str]   = None
    subtotal:       Optional[float] = None
    tax:            Optional[float] = None
    total_amount:   Optional[float] = None
    currency:       Optional[str]   = None
    line_items:     list[LineItem]  = []
    raw_confidence: Optional[str]   = None  # "high" | "medium" | "low"

class ExtractionResponse(BaseModel):
    filename:   str
    pages:      int
    data:       InvoiceData
    processing_time_ms: float