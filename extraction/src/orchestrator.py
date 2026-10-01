from schemas import ExtractionResult
from extractors.base import ExtractionStrategy

class TORExtractorOrchestrator:
    def __init__(self, primary_strategy: ExtractionStrategy, fallback_strategy: ExtractionStrategy = None, threshold: float = 0.8):
        self.primary_strategy = primary_strategy
        self.fallback_strategy = fallback_strategy
        self.threshold = threshold

    def execute_extraction(self, pdf_path: str) -> dict:
        result = self.primary_strategy.extract(pdf_path, threshold=self.threshold)
        
        if result.confidence >= self.threshold or not self.fallback_strategy:
            return self._format_response(result)
            
        print("Primary strategy failed confidence check. Triggering fallback...")
        
        fallback_result = self.fallback_strategy.extract(pdf_path, target_pages=[3, 4])
        return self._format_response(fallback_result)

    def _format_response(self, result: ExtractionResult) -> dict:
        return {
            "items": [item.model_dump() for item in result.items],
            "extraction_confidence": {
                "items_table": result.confidence
            },
            "extraction_method_used": [result.method_used]
        }