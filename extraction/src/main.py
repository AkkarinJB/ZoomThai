import json
import os
from extractors.plumber import PlumberExtractionStrategy
from extractors.gemini import VLMExtractionStrategy
from orchestrator import TORExtractorOrchestrator
from utils import clean_thai_number

class MockGeminiClient:
    class Models:
        def generate_content(self, model, contents):
            class Response:
                text = json.dumps([
                    {
                        "line_no": 1,
                        "item_code": "MOCK-001",
                        "description": "Mock VLM Extracted Item",
                        "quantity": 100.0,
                        "unit": "ชุด",
                        "unit_price_estimate": 500.0,
                        "total_price_estimate": 50000.0
                    }
                ])
            return Response()
    
    def __init__(self):
        self.models = self.Models()

def main():
    print("Initializing Extraction Pipeline (2-Stage)...")
    
    # 1. Primary Strategy
    primary = PlumberExtractionStrategy()
    
    # 2. Fallback Strategy (Using Mock Client since we don't have API keys in the script)
    vlm_client = MockGeminiClient()
    fallback = VLMExtractionStrategy(vlm_client=vlm_client)
    
    # Orchestrator
    orchestrator = TORExtractorOrchestrator(
        primary_strategy=primary,
        fallback_strategy=fallback,
        threshold=0.8
    )
    
    pdf_path = "/Users/akkarin/Desktop/ZoomThai/extraction/fixtures/tor_samples/PEA-TDDP.2(A)-082-2564.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"Error: Could not find PDF at {pdf_path}")
        return
        
    print(f"Running extraction on: {pdf_path}")
    result = orchestrator.execute_extraction(pdf_path)
    
    print("\n=== EXTRACTION RESULT ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # Store Trace
    with open("extraction_trace.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("\nSaved trace to extraction_trace.json")

if __name__ == "__main__":
    main()
