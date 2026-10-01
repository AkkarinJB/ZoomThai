from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class Announcement(BaseModel):
    id: str
    agency: str
    title: str
    method: str
    fiscal_year: int
    budget_amount: Optional[float]
    submission_deadline: Optional[datetime]
    tor_pdf_url: Optional[str]

class AdapterInterface(ABC):
    """
    Adapter Interface for government procurement sites.
    Separates fetching, parsing list pages, and extracting documents.
    """
    
    @abstractmethod
    def fetch_list_page(self, url: str) -> str:
        """Fetches the raw HTML of the list page."""
        pass
        
    @abstractmethod
    def parse_list_page(self, html: str) -> List[Announcement]:
        """Parses the raw HTML and extracts procurement announcements."""
        pass

    @abstractmethod
    def download_attachment(self, url: str) -> bytes:
        """Downloads the TOR PDF or associated attachment."""
        pass
