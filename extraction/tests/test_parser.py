import pytest
from unittest.mock import patch, MagicMock
from src.pdf_parser import clean_thai_number, TORExtractor

def test_clean_thai_number_normal():
    assert clean_thai_number("1,250,000.00") == 1250000.0

def test_clean_thai_number_thai_digits():
    assert clean_thai_number("๑,๒๕๐.๕๐") == 1250.5

def test_clean_thai_number_invalid_or_empty():
    assert clean_thai_number("") == 0.0
    assert clean_thai_number("-") == 0.0

@patch("src.pdf_parser.pdfplumber.open")  
def test_extractor_low_confidence_structure(mock_pdfplumber_open):
    mock_pdf = MagicMock()
    mock_pdfplumber_open.return_value.__enter__.return_value = mock_pdf

    extractor = TORExtractor()
    
    extractor._calculate_table_confidence = lambda tables: 0.4
    
    extractor._fallback_to_vlm = lambda *args, **kwargs: {
        "items": [{"line_no": 1, "description": "Test Item"}], 
        "confidence": 0.85
    }
    
    result = extractor.extract_document("dummy_path.pdf")
    
    assert "vlm_fallback" in result["extraction_method_used"][0]
    assert result["extraction_confidence"]["items_table"] == 0.85
    assert len(result["items"]) == 1


