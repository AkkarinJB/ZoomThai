def clean_thai_number(text: str) -> float:
    """แปลงตัวเลขไทยเป็นอารบิก ลบลูกน้ำ และแปลงเป็น float"""
    if not text or not isinstance(text, str):
        return 0.0
    
    thai_to_arabic = str.maketrans('๐๑๒๓๔๕๖๗๘๙', '0123456789')
    cleaned_text = text.translate(thai_to_arabic)
    cleaned_text = cleaned_text.replace(',', '').strip()
    
    try:
        return float(cleaned_text)
    except ValueError:
        return 0.0