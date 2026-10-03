import json
import pdfplumber
from extractors.base import ExtractionStrategy
from schemas import ExtractionResult, ProcurementItem

class VLMExtractionStrategy(ExtractionStrategy):
    def __init__(self, vlm_client):
        self.client = vlm_client

    def extract(self, pdf_path: str, **kwargs) -> ExtractionResult:
        print("VLM Starting...")
        target_pages = kwargs.get('target_pages', [3, 4])
        
        try:
            all_extracted_items = []
            
            with pdfplumber.open(pdf_path) as pdf:
                for page_index, page in enumerate(pdf.pages):
                    print(f"กำลังให้ VLM อ่านหน้า {page_index + 1}...")
                    pil_image = page.to_image(resolution=200).original

                    prompt = """
                    คุณคือผู้เชี่ยวชาญด้านการสกัดข้อมูลเอกสารจัดซื้อจัดจ้างภาครัฐของไทย
                    หน้าที่ของคุณคือดึงข้อมูล "ตารางรายการพัสดุ" จากรูปภาพเอกสารนี้
                    
                    กรุณาส่งคืนผลลัพธ์เป็น JSON Array ที่มีโครงสร้างแบบนี้เท่านั้น ห้ามมีข้อความอธิบายอื่นปน:
                    [
                      {
                        "line_no": 1,
                        "item_code": "รหัสพัสดุ (ถ้ามี)",
                        "description": "ชื่อหรือรายละเอียดพัสดุ",
                        "quantity": 10.0,
                        "unit": "หน่วยนับ",
                        "unit_price_estimate": 100.0,
                        "total_price_estimate": 1000.0
                      }
                    ]
                    ถ้าหน้าไหนไม่มีตารางพัสดุ ให้คืนค่าเป็น [] (Empty Array)
                    ตรวจสอบให้แน่ใจว่าผลลัพธ์เป็น JSON ที่ถูกต้อง (Valid JSON) เท่านั้น
                    """
                    
                    response = self.client.models.generate_content(
                        model='gemini-3.5-flash-lite', 
                        contents=[prompt, pil_image]
                    )
                    
                    raw_text = response.text.strip()
                    if raw_text.startswith("```json"):
                        raw_text = raw_text[7:-3].strip()
                    elif raw_text.startswith("```"):
                        raw_text = raw_text[3:-3].strip()
                        
                    try:
                        extracted_data = json.loads(raw_text)
                        for item in extracted_data:
                            all_extracted_items.append(ProcurementItem(**item))
                    except Exception as e:
                        print(f"JSON Parse Error: {e} | Raw: {raw_text}")
                        pass
            
            print(f"VLM สกัดข้อมูลสำเร็จ: พบ {len(all_extracted_items)} รายการจากทุกหน้า")
            
            return ExtractionResult(
                items=all_extracted_items,
                confidence=0.85,
                method_used="vlm_fallback"
            )
            
        except Exception as e:
            print(f"VLM Error: {e}")
            return ExtractionResult(
                items=[],
                confidence=0.0,
                method_used="vlm_fallback_failed"
            )
