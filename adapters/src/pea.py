from bs4 import BeautifulSoup
from typing import List
from datetime import datetime
from .interface import AdapterInterface, Announcement
import re

class PEAAdapter(AdapterInterface):
    """
    PEA Adapter for scraping bidding.pea.co.th
    """
    
    def fetch_list_page(self, url: str) -> str:
        with open(url, 'r', encoding='utf-8') as f:
            return f.read()
            
    def parse_list_page(self, html: str) -> List[Announcement]:
        soup = BeautifulSoup(html, 'html.parser')
        announcements = []
        
        table = soup.find('table', class_='views-table')
        if not table:
            table = soup.find('table')
            
        if not table:
            return []

        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if not cols or len(cols) < 5:
                continue
            
            try:
                announcement_id = cols[1].text.strip()
                title = cols[2].text.strip()
                method = "e-bidding"
                
                budget_text = cols[3].text.strip().replace(',', '')
                budget_amount = float(budget_text) if budget_text.replace('.', '', 1).isdigit() else None
                
                deadline_text = cols[5].text.strip()
                submission_deadline = None
                try:
                    # '15/09/2564'
                    parts = deadline_text.split('/')
                    if len(parts) == 3:
                        day = int(parts[0])
                        month = int(parts[1])
                        year = int(parts[2]) - 543
                        submission_deadline = datetime(year, month, day)
                except ValueError:
                    pass
                
                tor_link_tag = row.find('a', class_='tor-download')
                tor_pdf_url = tor_link_tag['href'] if tor_link_tag else None

                announcement = Announcement(
                    id=announcement_id,
                    agency="PEA",
                    title=title,
                    method=method,
                    fiscal_year=int(parts[2]) if submission_deadline else datetime.now().year + 543,
                    budget_amount=budget_amount,
                    submission_deadline=submission_deadline,
                    tor_pdf_url=tor_pdf_url
                )
                announcements.append(announcement)
            except Exception as e:
                print(f"Error parsing row: {e}")
                continue
            except Exception as e:
                print(f"Error parsing row: {e}")
                continue
                print(f"Error parsing row: {e}")
                continue
            
        return announcements
        
    def download_attachment(self, url: str) -> bytes:
        # Mock download attachment logic
        # In a real scenario, this would be requests.get(url).content
        return b"%PDF-1.4 mock pdf content"
