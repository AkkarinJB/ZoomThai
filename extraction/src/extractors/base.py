from abc import ABC, abstractmethod
from schemas import ExtractionResult

class ExtractionStrategy(ABC):
    @abstractmethod
    def extract(self, pdf_path: str, **kwargs) -> ExtractionResult:
        """Method หลักที่ทุก Strategy ต้องประมวลผลและคืนค่าเป็น ExtractionResult"""
        pass