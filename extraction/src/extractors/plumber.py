import pdfplumber
from typing import List
from extractors.base import ExtractionStrategy
from schemas import ExtractionResult, ProcurementItem
from utils import clean_thai_number

class PlumberExtractionStrategy(ExtractionStrategy):
    def extract(self, pdf_path: str, **kwargs) -> ExtractionResult:
        threshold = kwargs.get('threshold', 0.8)
        
        with pdfplumber.open(pdf_path) as pdf:
            raw_tables = self._extract_tables(pdf)
            print(f"จำนวนตารางที่ pdfplumber พบ: {len(raw_tables)}")
            
            confidence = self._calculate_confidence(raw_tables)
            items = []
            
            if confidence >= threshold:
                items = self._parse_items(raw_tables)
                
            return ExtractionResult(
                items=items,
                confidence=confidence,
                method_used="pdfplumber"
            )

    def _extract_tables(self, pdf) -> List:
        all_tables = []
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                all_tables.append(table)
        return all_tables

    def _calculate_confidence(self, tables: List) -> float:
        if not tables:
            return 0.0
        for table in tables:
            if len(table) > 1 and len(table[0]) >= 6:
                return 0.85
        return 0.4

    def _parse_items(self, raw_tables: List) -> List[ProcurementItem]:
        parsed_items = []
        for table in raw_tables:
            for row in table:
                if not row or not row[0] or "ลำดับ" in str(row[0]):
                    continue
                try:
                    item = ProcurementItem(
                        line_no=int(clean_thai_number(row[0])),
                        item_code=str(row[1]).strip() if row[1] else "",
                        description=str(row[2]).strip().replace('\n', ' ') if row[2] else "",
                        quantity=clean_thai_number(row[3]),
                        unit=str(row[4]).strip() if row[4] else "",
                        unit_price_estimate=clean_thai_number(row[5]),
                        total_price_estimate=clean_thai_number(row[6])
                    )
                    if item.line_no > 0:
                        parsed_items.append(item)
                except Exception as e:
                    print(f"PARSE ERROR: {e} | ROW: {row}")
                    continue
        return parsed_items