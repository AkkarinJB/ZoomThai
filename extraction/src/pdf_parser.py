import pdfplumber
import json
from typing import Dict, Any

def clean_thai_number(text: str) -> float:
    """แปลงตัวเลขไทยเป็นอารบิก ลบลูกน้ำ และแปลงเป็น float"""
    if not text or not isinstance(text, str):
        return 0.0
    thai_to_arabic = str.maketrans('๐๑๒๓๔๕๖๗๘๙', '0123456789')
    cleaned_text = text.translate(thai_to_arabic)
    cleaned_text = cleaned_text.replace(',', '').strip()
    
    try:
        return float(cleaned_text)
    except ValueError:
        return 0.0

class TORExtractor:
    def __init__(self, vlm_client=None):
        self.vlm_client = vlm_client 
        self.confidence_threshold = 0.8

    def extract_document(self, pdf_path: str) -> Dict[str, Any]:
        result = {
            "items": [],
            "extraction_confidence": {"header": 0.0, "items_table": 0.0, "overall": 0.0},
            "extraction_method_used": []
        }
        
        with pdfplumber.open(pdf_path) as pdf:
            raw_tables = self._extract_tables_with_plumber(pdf)
            print(f" จำนวนตารางที่ pdfplumber พบ: {len(raw_tables)}")
            confidence = self._calculate_table_confidence(raw_tables)
            
            if confidence >= self.confidence_threshold:
                result["items"] = self._parse_items_from_raw(raw_tables)
                result["extraction_confidence"]["items_table"] = confidence
                result["extraction_method_used"].append("pdfplumber")
            else:
                vlm_result = self._fallback_to_vlm(pdf_path, target_pages=[3, 4])
                
                result["items"] = vlm_result["items"]
                result["extraction_confidence"]["items_table"] = vlm_result["confidence"]
                result["extraction_method_used"].append("vlm_fallback")

        return result

    def _extract_tables_with_plumber(self, pdf):
        all_tables = []
        
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                all_tables.append(table)
                
        return all_tables

    def _calculate_table_confidence(self, tables):
        if not tables:
            return 0.0
        for table in tables:
            if len(table) > 1 and len(table[0]) >= 6:
                return 0.85
        return 0.4

    def _parse_items_from_raw(self, raw_tables):
        parsed_items = []
        
        for table in raw_tables:
            for row in table:
                if not row or not row[0] or "ลำดับ" in str(row[0]):
                    continue
                
                try:
                    print(f"Log ROW: {row}")
                    
                    item = {
                        "line_no": int(clean_thai_number(row[0])),
                        "item_code": str(row[1]).strip() if row[1] else "",
                        "description": str(row[2]).strip().replace('\n', ' ') if row[2] else "",
                        "quantity": clean_thai_number(row[3]),
                        "unit": str(row[4]).strip() if row[4] else "",
                        "unit_price_estimate": clean_thai_number(row[5]),
                        "total_price_estimate": clean_thai_number(row[6])
                    }
                    
                    if item["line_no"] > 0:
                        parsed_items.append(item)
                        
                except Exception as e:
                    print(f"PARSE ERROR: {e} | ROW: {row}")
                    continue
                    
        return parsed_items

    def _fallback_to_vlm(self, pdf_path: str, target_pages: list):
        print("Fallback to VLM extraction due to low confidence from pdfplumber.")
        mock_items = [
            {
                "line_no": 1,
                "item_code": "1010040001",
                "description": "50 sq. mm. XLPE-insulated 22 kV stranded aluminum cable",
                "quantity": 5000.0,
                "unit": "meter",
                "unit_price_estimate": 145.00,
                "total_price_estimate": 725000.00
            }
        ]
        return {"items": mock_items, "confidence": 0.88}