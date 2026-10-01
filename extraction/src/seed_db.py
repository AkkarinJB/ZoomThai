import os
import uuid
from config import settings
from google.genai import Client
import psycopg2
from extractors.plumber import PlumberExtractionStrategy
from extractors.gemini import VLMExtractionStrategy
from orchestrator import TORExtractorOrchestrator

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """ฟังก์ชันสำหรับตัดแบ่งข้อความยาวๆ เป็นชิ้นย่อยๆ (Chunks)"""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def process_and_store_vectors(announcement_id: str, full_text: str, vlm_client: Client):
    print(f"กำลังสร้าง Vector Embeddings สำหรับประกาศ: {announcement_id}...")
    chunks = chunk_text(full_text)
    print(f"แบ่งข้อความได้ทั้งหมด {len(chunks)} ชิ้น (Chunks)")

    db_url = os.getenv("DATABASE_URL", "postgresql://admin:password@localhost:5432/zoomthai")
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()

    try:
        for index, chunk in enumerate(chunks):
            chunk_id = f"{announcement_id}-chunk-{index}-{uuid.uuid4().hex[:6]}"

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
                ON CONFLICT (id) DO UPDATE 
                SET content = EXCLUDED.content, embedding = EXCLUDED.embedding;
                """,
                (chunk_id, announcement_id, chunk, vector_str)
            )
        
        conn.commit()
        print(" บันทึกข้อมูล Vector ลงตาราง document_chunks สำเร็จเรียบร้อย!")

    except Exception as e:
        conn.rollback()
        print(f" เกิดข้อผิดพลาดในการบันทึก Vector: {e}")
    finally:
        cursor.close()
        conn.close()

def main():
    if not settings.API_KEY:
        print("Error: GEMINI_API_KEY not found in .env file")
        return

    vlm_client = Client(api_key=settings.API_KEY)
    
    plumber_strategy = PlumberExtractionStrategy()
    gemini_strategy = VLMExtractionStrategy(vlm_client)
    
    extractor = TORExtractorOrchestrator(
        primary_strategy=plumber_strategy,
        fallback_strategy=gemini_strategy,
        threshold=settings.CONFIDENCE_THRESHOLD
    )
    
    pdf_path = "fixtures/tor_samples/PEA-TDDP.2(A)-082-2564.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at {pdf_path}")
        return
        
    print(f"Executing extraction on: {pdf_path}")
    result = extractor.execute_extraction(pdf_path)
    
    print("\n--- Result ---")
    print(f"Method Used: {result['extraction_method_used']}")
    print(f"Confidence: {result['extraction_confidence']['items_table']}")
    print(f"Number of Items Found: {len(result['items'])} items")

    
    if not result.get('items'):
        print("Mocking items due to VLM failure...")
        result['items'] = [{
            "description": "22 kV XLPE Power Cable, 500 sq.mm.",
            "quantity": 270.0,
            "unit": "m",
            "unit_price_estimate": 1000.0,
            "total_price_estimate": 270000.0
        }]

    announcement_id = "PEA-TDDP.2(A)-082/2564" 
    
    full_text = f" {announcement_id} "
    for item in result.get('items', []):
        full_text += f"รายการ: {item.get('description', '')} จำนวน: {item.get('quantity', '')} {item.get('unit', '')} "

    if full_text.strip():
        process_and_store_vectors(announcement_id, full_text, vlm_client)

if __name__ == "__main__":
    main()