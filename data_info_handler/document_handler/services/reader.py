from io import BytesIO
import docx

from gm_services.config import Settings
from gm_services.schemas.extraction import PARSING_METHODS, Page
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered

import logging

logger = logging.getLogger(__name__)


class Reader:
    converter = PdfConverter(
        artifact_dict=create_model_dict(device=Settings.system.device)
    )

    def __init__(self):
        raise TypeError(f"{self.__class__.__name__} is non-initable")

    @staticmethod
    def detect_method(content_type: str) -> PARSING_METHODS:
        if content_type.startswith("text/"):
            return "none"
        if content_type == "application/msword":
            return "docx"
        return "ocr"

    @classmethod
    def read(cls, data: bytes, method: PARSING_METHODS) -> Page | None:
        match method:
            case "ocr":
                return cls._ocr(data)
            case "docx":
                return cls._docx(data)
            case "none":
                return cls._none(data)
            case _:
                raise TypeError(f"{method} is not supported")

    @classmethod
    def _ocr(cls, data: bytes) -> Page | None:
        data_io = BytesIO(data)
        try:
            rendered = cls.converter(data_io)
            text, _, images = text_from_rendered(rendered)
        except Exception as e:
            logger.exception("Exception while reading OCR data: %s", e)
            return None

        if text is None:
            return None
        return Page(number=1, text=text)

    @staticmethod
    def _docx(data: bytes) -> Page | None:
        data_io = BytesIO(data)
        try:
            document = docx.Document(data_io)
        except Exception as e:
            logger.exception("Exception while reading docx data: %s", e)
            return None
        text = "\n".join(paragraph.text for paragraph in document.paragraphs)
        return Page(number=1, text=text)

    @staticmethod
    def _none(data: bytes) -> Page | None:
        try:
            text = data.decode()
        except UnicodeDecodeError as e:
            logger.exception("Exception while decoding text data: %s", e)
            return None
        return Page(number=1, text=text)
