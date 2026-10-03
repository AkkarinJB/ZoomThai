from pydantic import BaseModel, Field
from typing import List, Optional

class ProcurementItem(BaseModel):
    line_no: int
    item_code: Optional[str] = ""
    description: str
    quantity: float
    unit: str
    unit_price_estimate: Optional[float] = None
    total_price_estimate: Optional[float] = None

class ExtractionResult(BaseModel):
    items: List[ProcurementItem]
    confidence: float
    method_used: str