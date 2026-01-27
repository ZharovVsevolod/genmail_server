import os
from pathlib import Path

from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered

from gm_services.schemas.extraction import ExtractedDocument, Page
from gm_services.common import load_prompt, load_docx_text, delete_file

from gm_services.config import DEVICE_TYPE
from typing import List, Optional

import logging
logger = logging.getLogger(__name__)


# Supported file extension for text extraction
EXTENSIONS_FOR_OCR = [".pdf", ".png", ".jpg", ".jpeg"]
EXTENSIONS_FOR_TEXT = [".txt", ".md"]
EXTENSIONS_FOR_DOCX = [".docx", ".doc"]


class Extractor:
    def __init__(
        self,
        device: DEVICE_TYPE | None = None
    ) -> None:
        self.converter = PdfConverter(
            artifact_dict=create_model_dict(device=device),
        )
    
    
    def process_single_document(self, file_path: str) -> Optional[ExtractedDocument]:
        try:
            rendered = self.converter(file_path)
            text, _, images = text_from_rendered(rendered)
            
            pages = [Page(number=1, text=text)]
            
            metadata = {
                "source": file_path,
                "filename": os.path.basename(file_path),
                "file_size": os.path.getsize(file_path),
                "file_extension": Path(file_path).suffix.lower()
            }
            return ExtractedDocument(pages=pages, metadata=metadata)
        except Exception as e:
            logger.exception("Ошибка при обработке файла %s: %s", file_path, e)
            return None
    

    def extract_from_folder(self, folder_path: str) -> List[ExtractedDocument]:
        extracted_documents = []
        
        # Check if file is even exists
        if not os.path.exists(folder_path):
            raise ValueError(f"Папка {folder_path} не существует")

        if not os.path.isdir(folder_path):
            raise ValueError(f"{folder_path} не является папкой")
        
        supported_extensions = EXTENSIONS_FOR_OCR + EXTENSIONS_FOR_TEXT + EXTENSIONS_FOR_DOCX
        
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            
            if os.path.isfile(file_path):
                file_extension = Path(file_path).suffix.lower()

                if file_extension in supported_extensions:
                    logger.info("Обработка файла: %s", filename)

                    # Text file format - just load text
                    if file_extension in EXTENSIONS_FOR_TEXT:
                        text = load_prompt(file_path)
                        extracted_doc = ExtractedDocument(
                            pages = [Page(
                                number = 1,
                                text = text
                            )]
                        )
                    
                    # PDF format or image - OCR process
                    if file_extension in EXTENSIONS_FOR_OCR:
                        extracted_doc = self.process_single_document(file_path)
                    
                    # Docx/doc container - load via python-docx
                    if file_extension in EXTENSIONS_FOR_DOCX:
                        text = load_docx_text(file_path)
                        extracted_doc = ExtractedDocument(
                            pages = [Page(
                                number = 1,
                                text = text
                            )]
                        )
                    
                    # If there are any extracted text - append to result
                    if extracted_doc:
                        extracted_documents.append(extracted_doc)
                    
                    # After extraction - delete file
                    delete_file(file_path)
        
        return extracted_documents



if __name__ == "__main__":
    extractor = Extractor()
    
    # Обработка всех документов в папке
    folder_path = "data/documents_v2"  # Укажите путь до вашей папки
    try:
        results = extractor.extract_from_folder(folder_path)
        
        print(f"Обработано документов: {len(results)}")
        for i, doc in enumerate(results):
            print(f"Документ {i+1}:")
            print(f"  Файл: {doc.metadata.get('filename')}")
            print(f"  Кол-во страниц: {len(doc.pages)}")
            print(f"  Текст первой страницы (первые 100 символов): {doc.pages[0].text[:200]}...")
            print("-" * 50)
            
    except Exception as e:
        print(f"Ошибка: {e}")