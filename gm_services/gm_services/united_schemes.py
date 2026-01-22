from pydantic import BaseModel
from typing import Literal

# ------------------------
# Mail generation scenario
# ------------------------
# Extraction

PARSING_METHODS = Literal[
    "ocr", "docx", "none"
]  # none is for no parsing (of text, for example)

class Page(BaseModel):
    number: int
    text: str

class ExtractedDocument(BaseModel):
    pages: list[Page]
    metadata: dict = {} # source

    def to_str(self) -> str:
        result = "\n".join([page.text for page in self.pages])
        return result


# Understanding
DOCUMENT_TYPE = Literal["inner", "outer"]

class DocumentView(BaseModel):
    doc_type: DOCUMENT_TYPE
    text: str
    theme: str
    summary: str
    author: str
    number: str
    date: str
    metadata: dict = {} # source

    @property
    def doc_type_rus(self):
        return "Внутреннее письмо" if self.doc_type == "inner" else "Внешнее письмо"

    def to_dict(self) -> dict[str, str]:
        result = {
            "Тип": self.doc_type_rus,
            "Номер": self.number,
            "Дата": self.date,
            "Автор": self.author,
            "Тема": self.theme,
            "Суммаризация": self.summary,
            "text": self.text,
            "metadata": self.metadata
        }
        return result

    def to_str(self) -> str:
        result = f"Тип: {self.doc_type_rus}\nТема: {self.theme}\nСуммаризация: {self.summary}\nАвтор: {self.author}"
        return result


# Generation
class BaseGenerationBody(BaseModel):
    letter_body: str
    history: list