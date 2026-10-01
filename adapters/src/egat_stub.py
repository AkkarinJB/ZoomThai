from typing import List
from datetime import datetime
from .interface import AdapterInterface, Announcement

class EGATAdapterStub(AdapterInterface):
    """
    EGAT Adapter Stub demonstrating how the AdapterInterface is reused
    for another agency with completely different HTML structures.
    """
    
    def fetch_list_page(self, url: str) -> str:
        return "<html><body><div class='egat-bids'>EGAT MOCK HTML</div></body></html>"
            
    def parse_list_page(self, html: str) -> List[Announcement]:
        return [
            Announcement(
                id="EGAT-12345",
                agency="EGAT",
                title="Mock EGAT Procurement for Transformers",
                method="e-bidding",
                fiscal_year=2567,
                budget_amount=2000000.00,
                submission_deadline=datetime(2024, 1, 15, 12, 0),
                tor_pdf_url="https://egat.co.th/tor-12345.pdf"
            )
        ]
        
    def download_attachment(self, url: str) -> bytes:
        return b"%PDF-1.4 EGAT mock pdf content"
