import os
import sys
# Add parent dir to path to import adapters
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../adapters')))

import psycopg2
import uuid
from google.genai import Client
from config import settings
from extractors.plumber import PlumberExtractionStrategy
from extractors.gemini import VLMExtractionStrategy
from orchestrator import TORExtractorOrchestrator
from pea import PEAAdapter

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def process_and_store_vectors(announcement_id: str, full_text: str, vlm_client: Client, cursor):
    print(f"สร้าง Vector Embeddings...")
    chunks = chunk_text(full_text)
    
    for index, chunk in enumerate(chunks):
        chunk_id = f"{announcement_id}-chunk-{index}-{uuid.uuid4().hex[:6]}"
        try:
            response = vlm_client.models.embed_content(
                model="gemini-embedding-001", 
                contents=chunk
            )
            vector_values = response.embeddings[0].values
            vector_str = f"[{','.join(map(str, vector_values))}]"

            cursor.execute(
                """
                INSERT INTO document_chunks (id, announcement_id, content, embedding)
                VALUES (%s, %s, %s, %s::vector)
                ON CONFLICT (id) DO NOTHING;
                """,
                (chunk_id, announcement_id, chunk, vector_str)
            )
        except Exception as e:
            print(f"   [Error] Embedding: {e}")

def main():
    print("Scraping")
    
    adapter = PEAAdapter()
    html_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../fixtures/pea_list_page.html'))
    
    html_content = adapter.fetch_list_page(html_path)
    announcements = adapter.parse_list_page(html_content)
    
    print(f"เจอประกาศจัดซื้อจัดจ้างทั้งหมด {len(announcements)} รายการ!")
    
    db_url = os.getenv("DATABASE_URL", "postgresql://admin:password@localhost:5432/zoomthai")
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    
    if not settings.API_KEY:
        print("Error: GEMINI_API_KEY not found")
        return
        
    vlm_client = Client(api_key=settings.API_KEY)
    
    extractor = TORExtractorOrchestrator(
        primary_strategy=PlumberExtractionStrategy(),
        fallback_strategy=VLMExtractionStrategy(vlm_client),
        threshold=0.8
    )
    
    total_items = 0
    
    for ann in announcements:
        print(f"\nกำลังประมวลผลประกาศ: {ann.id} - {ann.title}")
        
        cursor.execute("""
            INSERT INTO procurement_announcements (announcement_id, agency, title, method, budget_amount)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (announcement_id) DO NOTHING
        """, (ann.id, ann.agency, ann.title, ann.method, ann.budget_amount))
        
        pdf_filename = ann.tor_pdf_url.split('/')[-1] if ann.tor_pdf_url else None
        pdf_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f'../fixtures/tor_samples/{pdf_filename}'))
        
        full_text = f"ประกาศ {ann.id} {ann.title} "
        
        if pdf_filename and os.path.exists(pdf_path):
            print(f"   พบไฟล์ PDF ท้องถิ่น: {pdf_path}")
            print(f"   เริ่มกระบวนการสกัดข้อมูล (Plumber -> VLM)...")
            
            result = extractor.execute_extraction(pdf_path)
            items = result.get('items', [])
            
            print(f"   สกัดรายการสำเร็จ {len(items)} รายการ (ด้วยวิธี {result.get('extraction_method_used')})")
            
            for idx, item in enumerate(items):
                cursor.execute("""
                    INSERT INTO procurement_items (announcement_id, line_no, item_code, description, quantity, unit, unit_price_estimate, total_price_estimate)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    ann.id, 
                    item.get('line_no', idx + 1), 
                    item.get('item_code'), 
                    item.get('description'), 
                    item.get('quantity'), 
                    item.get('unit'), 
                    item.get('unit_price_estimate'), 
                    item.get('total_price_estimate')
                ))
                full_text += f"รายการ: {item.get('description')} จำนวน: {item.get('quantity')} {item.get('unit')} "
                total_items += 1
                
        else:
            print(f"   ไม่พบไฟล์ PDF ข้ามการสกัดตาราง (อัปโหลด PDF ไว้ที่ {pdf_path} เพื่อทดสอบของจริง)")
            
        process_and_store_vectors(ann.id, full_text, vlm_client, cursor)
        conn.commit()
            
    cursor.close()
    conn.close()
    
    print(f"\nเสร็จสิ้นกระบวนการจำลองเหมือนจริง! บันทึกข้อมูลพัสดุสำเร็จ {total_items} รายการ")

if __name__ == "__main__":
    main()
