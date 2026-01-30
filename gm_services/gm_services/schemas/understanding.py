from typing import Literal
from pydantic import BaseModel

DOCUMENT_TYPE = Literal["inner", "outer"]


class DocumentView(BaseModel):
    doc_type: DOCUMENT_TYPE
    text: str
    theme: str
    summary: str
    author: str
    number: str
    date: str
    metadata: dict = {}  # source

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
            "metadata": self.metadata,
        }
        return result

    def to_str(self) -> str:
        result = f"Тип: {self.doc_type_rus}\nТема: {self.theme}\nСуммаризация: {self.summary}\nАвтор: {self.author}"
        return result
