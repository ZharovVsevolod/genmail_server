import httpx
from gm_services.config import Settings

from langchain_core.documents import Document
from ..schemas.retriever_schemas import (
    FILTER_TYPES, 
    RETURN_DOCUMETNS_RETURN_TYPE,
    RetrieverAnswer
)


class RetrieverClient:
    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url = Settings.services.retriever.base_url
        )

    
    def _format_documents(
        self, 
        docs: RetrieverAnswer, 
        dtype: RETURN_DOCUMETNS_RETURN_TYPE
    ) -> str | list[Document]:
        match dtype:
            case "str":
                # Get a string text from documents
                docs_text = [doc.page_content for doc in docs.context]
                # Combine this texts in one string
                documents = "\n\n**Следующий документ**\n".join(docs_text)
            
            case "langchain":
                documents = [
                    Document(
                        page_content = doc.page_content,
                        metadata = {
                            "source": doc.filter if doc.filter else "all",
                            "docname": doc.docname
                        }
                    )
                    for doc in docs.context
                ]

        return documents


    async def similarity_search(
        self,
        query: str,
        k: int = 3,
        filter_type: FILTER_TYPES | None = None,
        what_to_filter: str | None = None,
        return_format: RETURN_DOCUMETNS_RETURN_TYPE | None = None,
    ) -> RetrieverAnswer | list[str] | list[Document]:
        params = {
            "query": query,
            "k": k,
            "filter_type": filter_type,
            "what_to_filter": what_to_filter
        }
        r = await self.client.get("/retrieve", params = params)
        r.raise_for_status()
        found_documents = RetrieverAnswer.model_validate(r.json())

        if return_format is not None:
            found_documents = self._format_documents(
                docs = found_documents, 
                dtype = return_format
            )

        return found_documents