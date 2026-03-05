import io
from typing import Dict, Tuple

import pypdf

from ..utils.helpers import PDFTypeError


class PDFParser:
    def __init__(self, min_text_length: int = 50):
        self.min_text_length = min_text_length
    
    def parse(self, file_content: bytes) -> Tuple[str, Dict]:
        """
        解析PDF文件
        
        Args:
            file_content: PDF文件内容
            
        Returns:
            (提取的文本, 元数据)
            
        Raises:
            PDFTypeError: 如果不是文本型PDF或解析失败
        """
        try:
            pdf_reader = pypdf.PdfReader(io.BytesIO(file_content))
            
            if not self._is_text_pdf(pdf_reader):
                raise PDFTypeError(
                    "仅支持文本型PDF文件。您上传的PDF可能是扫描件或图片型PDF，"
                    "请上传可复制文字的PDF文件。"
                )
            
            text = ""
            metadata = {
                'page_count': len(pdf_reader.pages),
                'title': '',
                'author': ''
            }
            
            if pdf_reader.metadata:
                metadata['title'] = pdf_reader.metadata.get('/Title', '') or ''
                metadata['author'] = pdf_reader.metadata.get('/Author', '') or ''
            
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            return text, metadata
            
        except PDFTypeError:
            raise
        except Exception as e:
            raise PDFTypeError(f"PDF文件读取失败: {str(e)}")
    
    def _is_text_pdf(self, pdf_reader) -> bool:
        """
        检查是否为文本型PDF
        """
        if len(pdf_reader.pages) > 0:
            text = pdf_reader.pages[0].extract_text()
            if text and len(text.strip()) >= self.min_text_length:
                return True
        return False
    
    def get_page_count(self, file_content: bytes) -> int:
        """
        获取PDF页数
        """
        try:
            pdf_reader = pypdf.PdfReader(io.BytesIO(file_content))
            return len(pdf_reader.pages)
        except Exception:
            return 0
    
    def extract_page(self, file_content: bytes, page_number: int) -> str:
        """
        提取指定页面的文本
        """
        try:
            pdf_reader = pypdf.PdfReader(io.BytesIO(file_content))
            if 0 <= page_number < len(pdf_reader.pages):
                return pdf_reader.pages[page_number].extract_text() or ""
            return ""
        except Exception:
            return ""


pdf_parser = PDFParser()

def get_pdf_parser() -> PDFParser:
    return pdf_parser
