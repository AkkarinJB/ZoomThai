import pytest
from datetime import datetime
from src.pea import PEAAdapter
from src.egat_stub import EGATAdapterStub

def test_egat_stub_returns_announcement():
    adapter = EGATAdapterStub()
    html = adapter.fetch_list_page("http://mock.egat.com")
    announcements = adapter.parse_list_page(html)
    
    assert len(announcements) == 1
    ann = announcements[0]
    assert ann.agency == "EGAT"
    assert ann.id == "EGAT-12345"
    assert ann.budget_amount == 2000000.00
    assert ann.method == "e-bidding"
    assert ann.tor_pdf_url == "https://egat.co.th/tor-12345.pdf"

def test_pea_parser():
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    fixture_path = os.path.join(base_dir, "fixtures", "pea_list_page.html")
    
    adapter = PEAAdapter()
    html = adapter.fetch_list_page(fixture_path)
    announcements = adapter.parse_list_page(html)
    
    assert len(announcements) > 0
    ann = announcements[0]
    assert ann.agency == "PEA"
    assert ann.id == "PEA-TDDP.2(A)-082/2564"
    assert ann.title == "จัดซื้ออุปกรณ์สายไฟ สำหรับใช้งานที่สถานีไฟฟ้านครราชสีมา 8"
    assert ann.budget_amount == 12500000.00
    assert ann.tor_pdf_url == "tor_samples/PEA-TDDP.2(A)-082-2564.pdf"
    assert ann.submission_deadline == datetime(2021, 9, 15, 0, 0)

def test_pea_parser_empty():
    mock_html = "<html><body>No tables here!</body></html>"
    adapter = PEAAdapter()
    announcements = adapter.parse_list_page(mock_html)
    
    assert len(announcements) == 0
