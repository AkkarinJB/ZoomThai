#!/usr/bin/env python3
"""
ZoomThai Seed Script
Runs automatically via Docker Compose after DB is ready.
Seeds the database with fixture data including vector embeddings.
Requires GEMINI_API_KEY and DATABASE_URL environment variables.
"""

import os
import sys
import time
import psycopg2
import hashlib
from google.genai import Client

DATABASE_URL = os.environ.get("DATABASE_URL", "postgres://admin:password@db:5432/zoomthai")
API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("API_KEY")

# Parse DATABASE_URL for psycopg2
def parse_db_url(url: str) -> dict:
    url = url.replace("postgres://", "").replace("postgresql://", "")
    user_pass, rest = url.split("@")
    user, password = user_pass.split(":")
    host_port_db = rest.split("/")
    db = host_port_db[1]
    host_port = host_port_db[0].split(":")
    host = host_port[0]
    port = int(host_port[1]) if len(host_port) > 1 else 5432
    return {"user": user, "password": password, "host": host, "port": port, "dbname": db}

def wait_for_db(params: dict, retries: int = 20) -> psycopg2.extensions.connection:
    for i in range(retries):
        try:
            conn = psycopg2.connect(**params)
            print("[seed] DB connected")
            return conn
        except Exception as e:
            print(f"[seed] Waiting for DB ({i+1}/{retries}): {e}")
            time.sleep(3)
    raise RuntimeError("Could not connect to DB after multiple retries")

def embed(client: Client, text: str) -> list[float]:
    resp = client.models.embed_content(model="gemini-embedding-001", contents=text)
    return resp.embeddings[0].values

def chunk_id(ann_id: str, suffix: str) -> str:
    return f"{ann_id}-{suffix}-{hashlib.md5((ann_id + suffix).encode()).hexdigest()[:6]}"

def already_seeded(cursor) -> bool:
    cursor.execute("SELECT COUNT(*) FROM procurement_announcements WHERE announcement_id = 'PEA-TDDP.2(A)-082/2564'")
    return cursor.fetchone()[0] > 0

def main():
    if not API_KEY:
        print("[seed] ERROR: GEMINI_API_KEY is not set. Skipping seeding.")
        sys.exit(0)

    params = parse_db_url(DATABASE_URL)
    conn = wait_for_db(params)
    cursor = conn.cursor()

    # Fix schema: ensure vector column is 3072-dim
    cursor.execute("ALTER TABLE document_chunks ALTER COLUMN embedding TYPE vector(3072)")
    conn.commit()

    if already_seeded(cursor):
        print("[seed] Data already exists. Skipping.")
        cursor.close()
        conn.close()
        sys.exit(0)

    print("[seed] Starting data seeding...")
    client = Client(api_key=API_KEY)

    # ── Announcements ─────────────────────────────────────────────────
    announcements = [
        ("PEA-TDDP.2(A)-082/2564", "PEA", "จัดซื้ออุปกรณ์สายไฟ สำหรับใช้งานที่สถานีไฟฟ้านครราชสีมา 8",
         "e-bidding", 2564, 12500000.00, "2021-09-15"),
        ("PEA-M(G)-138/2564", "PEA", "จัดซื้อวัตถุดิบรองกลุ่มที่ 4 ให้แผนกโรงงานผลิตภัณฑ์คอนกรีต",
         "e-bidding", 2564, 8750000.00, None),
        ("PEA-SMC-CM-08-2020", "PEA", "งานจ้างจัดหาพร้อมติดตั้งอุปกรณ์ควบคุมในระบบจำหน่าย",
         "e-bidding", 2563, 45000000.00, None),
        ("PEA-NE-2567-015", "PEA", "จัดซื้อหม้อแปลงไฟฟ้า 22 kV ขนาด 100-1000 kVA",
         "e-bidding", 2567, 35000000.00, None),
        ("PEA-SE-2567-022", "PEA", "งานจ้างก่อสร้างสายส่ง 115 kV สถานีไฟฟ้าบ้านบึง-ศรีราชา",
         "e-bidding", 2567, 280000000.00, None),
    ]
    cursor.executemany("""
        INSERT INTO procurement_announcements
            (announcement_id, agency, title, method, fiscal_year, budget_amount, submission_deadline)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (announcement_id) DO NOTHING
    """, announcements)
    conn.commit()
    print(f"[seed] Inserted {len(announcements)} announcements")

    # ── Procurement Items ──────────────────────────────────────────────
    items = [
        ("PEA-TDDP.2(A)-082/2564", 1, "22 kV XLPE Power Cable, 500 sq.mm.",    270.0,  "m.", None,  None),
        ("PEA-TDDP.2(A)-082/2564", 2, "22 kV XLPE Power Cable, 400 sq.mm.",   3670.0,  "m.", None,  None),
        ("PEA-TDDP.2(A)-082/2564", 3, "22 kV XLPE Power Cable, 240 sq.mm.",    190.0,  "m.", None,  None),
        ("PEA-TDDP.2(A)-082/2564", 4, "22 kV XLPE Power Cable, 95 sq.mm.",      80.0,  "m.", None,  None),
        ("PEA-TDDP.2(A)-082/2564", 5, "LV, Cable 750 V, 1x6 sq.mm.",           500.0,  "m.", None,  None),
        ("PEA-TDDP.2(A)-082/2564", 6, "LV, Cable 750 V, 1x10 sq.mm.",          250.0,  "m.", None,  None),
        ("PEA-TDDP.2(A)-082/2564", 7, "LV, Cable NYY 1x16 sq.mm.",             300.0,  "m.", None,  None),
        ("PEA-TDDP.2(A)-082/2564", 8, "LV, Cable NYY 1x200 sq.mm.",            750.0,  "m.", None,  None),
        ("PEA-TDDP.2(A)-082/2564", 9,
         "22 kV XLPE Power Cable, 50 sq.mm. stranded aluminum",                5000.0,  "m.", 145.0, 725000.0),
    ]
    cursor.executemany("""
        INSERT INTO procurement_items
            (announcement_id, line_no, description, quantity, unit, unit_price_estimate, total_price_estimate)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, items)
    conn.commit()
    print(f"[seed] Inserted {len(items)} procurement items")

    # ── Document Chunks with Embeddings ────────────────────────────────
    chunks = [
        ("PEA-TDDP.2(A)-082/2564", "ann-summary",
         "ประกาศ PEA-TDDP.2(A)-082/2564 จัดซื้ออุปกรณ์สายไฟ สำหรับใช้งานที่สถานีไฟฟ้านครราชสีมา 8 "
         "วิธีจัดซื้อ: e-bidding งบประมาณ: 12,500,000 บาท วันยื่นซอง: 15 กันยายน 2564 "
         "สายไฟ 50 sq.mm. ราคาต่อหน่วย: 145 บาท จำนวน: 5000 เมตร ราคารวม: 725,000 บาท"),
        ("PEA-TDDP.2(A)-082/2564", "items-detail",
         "ประกาศ PEA-TDDP.2(A)-082/2564 รายการพัสดุ: "
         "22 kV XLPE Power Cable 500 sq.mm. จำนวน 270 m. | "
         "22 kV XLPE Power Cable 400 sq.mm. จำนวน 3670 m. | "
         "22 kV XLPE Power Cable 240 sq.mm. จำนวน 190 m. | "
         "22 kV XLPE Power Cable 95 sq.mm. จำนวน 80 m. | "
         "22 kV XLPE Power Cable 50 sq.mm. stranded aluminum จำนวน 5000 m. ราคาต่อหน่วย 145 บาท ราคารวม 725000 บาท | "
         "LV Cable 750V 1x6 sq.mm. 500 m. | LV Cable 750V 1x10 sq.mm. 250 m. | "
         "LV Cable NYY 1x16 sq.mm. 300 m. | LV Cable NYY 1x200 sq.mm. 750 m."),
        ("PEA-M(G)-138/2564", "ann-summary",
         "ประกาศ PEA-M(G)-138/2564 จัดซื้อวัตถุดิบรองกลุ่มที่ 4 ให้แผนกโรงงานผลิตภัณฑ์คอนกรีต "
         "วิธีจัดซื้อ: e-bidding งบประมาณ: 8,750,000 บาท"),
        ("PEA-SMC-CM-08-2020", "ann-summary",
         "ประกาศ PEA-SMC-CM-08-2020 งานจ้างจัดหาพร้อมติดตั้งอุปกรณ์ควบคุมในระบบจำหน่าย "
         "วิธีจัดซื้อ: e-bidding งบประมาณ: 45,000,000 บาท"),
        ("PEA-NE-2567-015", "ann-summary",
         "ประกาศ PEA-NE-2567-015 จัดซื้อหม้อแปลงไฟฟ้า 22 kV ขนาด 100-1000 kVA "
         "วิธีจัดซื้อ: e-bidding งบประมาณ: 35,000,000 บาท"),
    ]

    for ann_id, suffix, content in chunks:
        cid = chunk_id(ann_id, suffix)
        print(f"[seed] Embedding chunk: {cid}")
        try:
            vector = embed(client, content)
            vec_str = "[" + ",".join(str(v) for v in vector) + "]"
            cursor.execute("""
                INSERT INTO document_chunks (id, announcement_id, content, embedding)
                VALUES (%s, %s, %s, %s::vector)
                ON CONFLICT (id) DO NOTHING
            """, (cid, ann_id, content, vec_str))
            conn.commit()
        except Exception as e:
            print(f"[seed] Embedding error for {cid}: {e}")
        time.sleep(1)  # avoid rate limit

    print("[seed] Seeding complete!")
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
