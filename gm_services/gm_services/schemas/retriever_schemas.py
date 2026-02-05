from pydantic import BaseModel

from typing import Literal

FILTER_TYPES = Literal["source"]
RETURN_DOCUMETNS_RETURN_TYPE = Literal["api", "str", "langchain"]


class RetrievedDocument:
    page_content: str
    docname: str
    source: str | None

class RetrieverAnswer(BaseModel):
    query: str
    rephrased_query: str
    context: list[RetrievedDocument]
