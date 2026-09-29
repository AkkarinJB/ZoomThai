import psycopg2
from datetime import datetime
from pdf_parser import TORExtractor

DB_URL = "postgresql://admin:password@localhost:5432/zoomthai"

def seed_data():
    print("1. กำลังสกัดข้อมูลจาก PDF...")
    extractor = TORExtractor()
    
    pdf_path = "fixtures/tor_samples/PEA-TDDP.2(A)-082-2564.pdf"
    
    try:
        result = extractor.extract_document(pdf_path)
        print(f"สกัดได้ {len(result['items'])} รายการ confidence: {result['extraction_confidence']['items_table']})")
    except Exception as e:
        print(f"ไม่สามารถอ่าน PDF ได้ : {e}")
        return  
    #test
    announcement_id = "PEA-TDDP.2(A)-082/2564"
    
    print("2. กำลังเชื่อมต่อ Database...")
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()

    try:
        print("3. กำลังบันทึกข้อมูลส่วนหัวประกาศ...")
        cursor.execute("""
            INSERT INTO procurement_announcements 
            (announcement_id, agency, title, method, fiscal_year, budget_amount, submission_deadline)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (announcement_id) DO NOTHING;
        """, (
            announcement_id, 
            "PEA", 
            "จัดซื้ออุปกรณ์สายไฟ สำหรับใช้งานที่สถานีไฟฟ้านครราชสีมา 8", 
            "e-bidding", 
            2564, 
            12500000.00, 
            datetime.fromisoformat("2021-09-15T16:30:00+07:00")
        ))

        print("4. กำลังบันทึกข้อมูลตารางพัสดุ...")
        for item in result["items"]:
            cursor.execute("""
                INSERT INTO procurement_items 
                (announcement_id, line_no, item_code, description, quantity, unit, unit_price_estimate, total_price_estimate)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """, (
                announcement_id,
                item["line_no"],
                item.get("item_code", ""),
                item["description"],
                item["quantity"],
                item["unit"],
                item["unit_price_estimate"],
                item["total_price_estimate"]
            ))

        conn.commit()
        print("บันทึกข้อมูลสำเร็จทั้งหมด!")
    except Exception as e:
        conn.rollback()
        print(f"Database error: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    seed_data()