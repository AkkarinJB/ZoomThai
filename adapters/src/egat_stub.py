from typing import List
from .interface import AdapterInterface, Announcement
import datetime

class EGATAdapterStub(AdapterInterface):
    def fetch_list_page(self, url: str) -> str:
        return "<html>EGAT Stub HTML</html>"
        
    def parse_list_page(self, html: str) -> List[Announcement]:
        return [Announcement(id="EGAT-12345", agency="EGAT", title="Stub", method="e-bidding", fiscal_year=2024, budget_amount=2000000.00, submission_deadline=datetime.datetime(2024, 1, 1), tor_pdf_url="https://egat.co.th/tor-12345.pdf")]
        
    def download_attachment(self, url: str) -> bytes:
        return b""
