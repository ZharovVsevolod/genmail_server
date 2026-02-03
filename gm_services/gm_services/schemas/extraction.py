from pydantic import BaseModel
from typing import Literal


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