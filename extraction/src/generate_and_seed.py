import os
import uuid
import random
from fpdf import FPDF
import psycopg2
from extractors.plumber import PlumberExtractionStrategy
from orchestrator import TORExtractorOrchestrator
from config import settings
from google.genai import Client
import time

def create_mock_pdf(filename, ann_id):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 12) # Use Helvetica as we don't have Thai font loaded, use english text for mock
    pdf.cell(0, 10, f"Terms of Reference (TOR): {ann_id}", 0, 1, 'C')
    pdf.ln(10)
    
    # Table Header
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(20, 10, "No.", 1)
    pdf.cell(30, 10, "Item Code", 1)
    pdf.cell(60, 10, "Description", 1)
    pdf.cell(20, 10, "Qty", 1)
    pdf.cell(20, 10, "Unit", 1)
    pdf.cell(20, 10, "Price", 1)
    pdf.cell(20, 10, "Total", 1)
    pdf.ln()
    
    pdf.set_font("Helvetica", "", 9)
    items_count = random.randint(20, 35)
    
    generated_text = f"Announcement {ann_id}. "
    for i in range(1, items_count + 1):
        qty = random.randint(10, 500)
        price = random.randint(100, 5000)
        total = qty * price
        
        pdf.cell(20, 10, str(i), 1)
        pdf.cell(30, 10, f"ITM-{i:03d}", 1)
        pdf.cell(60, 10, f"Equipment Type {random.randint(1, 99)} Model X", 1)
        pdf.cell(20, 10, str(qty), 1)
        pdf.cell(20, 10, "pcs", 1)
        pdf.cell(20, 10, str(price), 1)
        pdf.cell(20, 10, str(total), 1)
        pdf.ln()
        
        generated_text += f"Item {i} Equipment Type Model X Qty {qty} Price {price} Total {total}. "
        
    pdf.output(filename)
    return generated_text

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def main():
    print("🚀 เริ่มกระบวนการจำลองข้อมูลขนาดใหญ่ (100 โครงการ / หลักพันพัสดุ)")
    db_url = os.getenv("DATABASE_URL", "postgresql://admin:password@localhost:5432/zoomthai")
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    
    vlm_client = Client(api_key=settings.API_KEY)
    
    os.makedirs("fixtures/bulk", exist_ok=True)
    
    total_items_inserted = 0
    
    for i in range(1, 101):
        ann_id = f"PEA-BULK-{i:03d}"
        pdf_path = f"fixtures/bulk/{ann_id}.pdf"
        
        # 1. Generate Announcement
        budget = random.randint(1000000, 50000000)
        cursor.execute("""
            INSERT INTO procurement_announcements (announcement_id, agency, title, method, budget_amount)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (announcement_id) DO NOTHING
        """, (ann_id, "PEA", f"โครงการจัดซื้ออุปกรณ์ล็อตใหญ่ ชุดที่ {i}", "e-bidding", budget))
        
        # 2. Create PDF with Text
        full_text = create_mock_pdf(pdf_path, ann_id)
        
        # 3. Extract using Plumber (No VLM needed since it's pure text!)
        plumber = PlumberExtractionStrategy()
        result = plumber.extract(pdf_path)
        
        # 4. Insert Items
        for item in result.items:
            cursor.execute("""
                INSERT INTO procurement_items (announcement_id, line_no, item_code, description, quantity, unit, unit_price_estimate, total_price_estimate)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (ann_id, item.line_no, item.item_code, item.description, item.quantity, item.unit, item.unit_price_estimate, item.total_price_estimate))
            total_items_inserted += 1
            
        # 5. Embeddings (We will only embed 1 chunk per announcement to save time/API quota)
        chunk = full_text[:500]
        chunk_id = f"{ann_id}-chunk-0"
        try:
            resp = vlm_client.models.embed_content(model="gemini-embedding-001", contents=chunk)
            vec = f"[{','.join(map(str, resp.embeddings[0].values))}]"
            cursor.execute("""
                INSERT INTO document_chunks (id, announcement_id, content, embedding)
                VALUES (%s, %s, %s, %s::vector)
                ON CONFLICT (id) DO NOTHING
            """, (chunk_id, ann_id, chunk, vec))
        except Exception as e:
            print(f"Embedding error: {e}")
            
        if i % 10 == 0:
            print(f"✅ ประมวลผลไปแล้ว {i} ไฟล์ (รวม {total_items_inserted} รายการ)")
            time.sleep(2) # Prevent rate limits
            
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"🎉 เสร็จสิ้น! สกัดและบันทึกข้อมูลสำเร็จ {total_items_inserted} รายการ จาก 100 ไฟล์")

if __name__ == "__main__":
    main()
