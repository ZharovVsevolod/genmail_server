from gm_services.database.vectorstore import OpenSearchConnection
from gm_services.schemas.retriever_schemas import (
    RetrieverAnswer, 
    RetrievedDocument
)

from langchain_core.documents import Document
from gm_services.schemas.retriever_schemas import FILTER_TYPES

import logging
logger = logging.getLogger(__name__)


class OpenSearchRetriever(OpenSearchConnection):
    def __init__(self):
        super().__init__()

    def _create_filter(
        self, 
        filter_type: FILTER_TYPES,
        what_to_filter: str
    ) -> list[dict]:
        match filter_type:
            case "source":
                actual_filter = [{
                    "term": {
                        "metadata.source.keyword": what_to_filter
                    }
                }]

            case _:
                actual_filter = None

        return actual_filter

    def _format_documents(
        self, 
        docs: list[Document],
        query: str,
        rephrased_query: str | None = None
    ) -> RetrieverAnswer:
        if rephrased_query is None:
            rephrased_query = query
        
        context = [
            RetrievedDocument(
                page_content = doc.page_content,
                docname = doc.metadata.get("docname", None),
                source = doc.metadata.get("source", None)
            ) for doc in docs
        ]
        
        result = RetrieverAnswer(
            query = query,
            rephrased_query = rephrased_query,
            context = context
        )
        return result


    def similarity_search(
        self,
        query: str,
        k: int = 3,
        filter_type: FILTER_TYPES | None = None,
        what_to_filter: str | None = None,
    ) -> RetrieverAnswer:
        # Formalize filter to needed format
        actual_filter = self._create_filter(filter_type, what_to_filter)

        logger.info("Similarity search")
        found_documents = self.vectorstore.similarity_search(
            query = query, 
            k = k, 
            filter = actual_filter
        )
        logger.info("Found %s close documents", str(len(found_documents)))

        found_documents = self._format_documents(found_documents)
        return found_documents



MAIN_RETRIEVER = OpenSearchRetriever()