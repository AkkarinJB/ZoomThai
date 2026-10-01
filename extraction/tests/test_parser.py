import pytest
from unittest.mock import patch, MagicMock
from utils import clean_thai_number
from orchestrator import TORExtractorOrchestrator
from extractors.base import ExtractionStrategy
from schemas import ExtractionResult, ProcurementItem

def test_clean_thai_number_normal():
    assert clean_thai_number("1,250,000.00") == 1250000.0

def test_clean_thai_number_thai_digits():
    assert clean_thai_number("๑,๒๕๐.๕๐") == 1250.5

def test_clean_thai_number_invalid_or_empty():
    assert clean_thai_number("") == 0.0
    assert clean_thai_number("-") == 0.0

class DummyLowConfidenceStrategy(ExtractionStrategy):
    def extract(self, pdf_path, **kwargs):
        return ExtractionResult(
            items=[], 
            confidence=0.4, 
            method_used="pdfplumber"
            )

class DummyHighConfidenceFallbackStrategy(ExtractionStrategy):
    def extract(self, pdf_path, **kwargs):
        item = ProcurementItem(
            line_no=1, 
            item_code="", 
            description="Test Item", 
            quantity=1.0, 
            unit="pc", 
            unit_price_estimate=10.0, 
            total_price_estimate=10.0
            )
        return ExtractionResult(
            items=[item], 
            confidence=0.85, 
            method_used="vlm_fallback"
            )

def test_extractor_low_confidence_structure():
    primary = DummyLowConfidenceStrategy()
    fallback = DummyHighConfidenceFallbackStrategy()
    
    orchestrator = TORExtractorOrchestrator(
        primary_strategy=primary, 
        fallback_strategy=fallback
        )
    result = orchestrator.execute_extraction("dummy_path.pdf")
    
    assert "vlm_fallback" in result["extraction_method_used"][0]
    assert result["extraction_confidence"]["items_table"] == 0.85
    assert len(result["items"]) == 1

def test_clean_thai_number_mixed():
    assert clean_thai_number("๑,250.๕0") == 1250.5

def test_orchestrator_primary_success():
    class DummyHighConfidencePrimaryStrategy(ExtractionStrategy):
        def extract(self, pdf_path, **kwargs):
            item = ProcurementItem(
                line_no=1, 
                item_code="", 
                description="Primary Item", 
                quantity=1.0, unit="pc", 
                unit_price_estimate=10.0, 
                total_price_estimate=10.0
                )
            return ExtractionResult(
                items=[item], 
                confidence=0.95, 
                method_used="pdfplumber"
                )
            
    primary = DummyHighConfidencePrimaryStrategy()
    orchestrator = TORExtractorOrchestrator(primary_strategy=primary)
    result = orchestrator.execute_extraction("dummy.pdf")

    assert "pdfplumber" in result["extraction_method_used"][0]
    assert result["extraction_confidence"]["items_table"] == 0.95

def test_procurement_item_schema_validation():
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        ProcurementItem(
            line_no="abc", 
            item_code="", 
            description="", 
            quantity="xyz", 
            unit="", 
            unit_price_estimate=0, 
            total_price_estimate=0
            )

def test_orchestrator_fallback_fails():
    primary = DummyLowConfidenceStrategy()
    fallback = DummyLowConfidenceStrategy() # returns 0.4

    orchestrator = TORExtractorOrchestrator(
        primary_strategy=primary, 
        fallback_strategy=fallback
        )
    result = orchestrator.execute_extraction("dummy.pdf")

    assert result["extraction_confidence"]["items_table"] == 0.4
    assert "pdfplumber" in result["extraction_method_used"][0]
