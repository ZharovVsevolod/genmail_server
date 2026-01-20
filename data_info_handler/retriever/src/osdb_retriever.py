from uuid import uuid4

from gm_services.gm_services.database.vectorstore import OpenSearchConnection
from gm_services.gm_services.common import generate_hex
from gm_services.gm_services.united_schemes import DocumentView
from gm_services.gm_services.config import Settings

from langchain_core.vectorstores import VectorStoreRetriever
from langchain_core.documents import Document
from typing import Literal

import logging
logger = logging.getLogger(__name__)


FILTER_TYPES = Literal["source"]
RETURN_DOCUMETNS_RETURN_TYPE = Literal["str"]


class OpenSearchRetriever(OpenSearchConnection):
    def __init__(self):
        super().__init__()
    

    # ------------------
    # Retrieve Documents
    # ------------------
    def _create_uuids(self, n: int) -> list[str]:
        uuids = [str(uuid4()) for _ in range(n)]
        return uuids


    def _create_filter(self, filter_type: FILTER_TYPES, what_to_filter: str) -> list[dict]:
        match filter_type:
            case "source":
                actual_filter = [{"term": {"metadata.source.keyword": what_to_filter}}]
            
            case _:
                actual_filter = None
        
        return actual_filter
    

    def _format_documents(
        self,
        docs: list[Document],
        dtype: RETURN_DOCUMETNS_RETURN_TYPE
    ) -> str:
        match dtype:
            case "str":
                # Get a string text from documents
                docs_text = [doc.page_content for doc in docs]
                # Combine this texts in one string
                docs_str = "\n\n**Следующий документ**\n".join(docs_text)
        
        return docs_str
    
    
    def add_documents(self, docs: list[Document]) -> None:
        uuids = self._create_uuids(len(docs))
        self.vectorstore.add_documents(documents=docs, ids=uuids)


    def delete_index(self, index_name: str) -> None:
        self.client.indices.delete(index=index_name)
    

    def similarity_search(
        self, 
        query: str, 
        k: int = 3,
        filter_type: FILTER_TYPES | None = None,
        what_to_filter: str | None = None,
        return_format: RETURN_DOCUMETNS_RETURN_TYPE | None = None
    ) -> list[Document]:
        # Formalize filter to needed format
        actual_filter = self._create_filter(filter_type, what_to_filter)
        logger.info("Similarity search")

        found_documents = self.vectorstore.similarity_search(
            query = query,
            k = k,
            filter = actual_filter
        )

        if return_format is not None:
            found_documents = self._format_documents(
                docs = found_documents, 
                dtype = return_format
            )

        return found_documents
    

    def get_retriever(self, threshold: float = 0.2) -> VectorStoreRetriever:
        retriever = self.vectorstore.as_retriever(
            search_type = "similarity_score_threshold", 
            search_kwargs = {"score_threshold": threshold}
        )
        return retriever
    
    # ------------------
    # Save document data
    # ------------------
    def add_extracted_info(self, session_id: str, extracted: DocumentView) -> None:
        # Make DocumentView dict-type
        extracted_dict = extracted.model_dump(mode = "python")
        # Add session_id parameter
        extracted_dict["session_id"] = session_id
        # Create a record to the database
        self.client.create(
            index = Settings.services.vectorbase.documentview_index,
            id = generate_hex(8),
            document = extracted_dict
        )
    

    def _find_extracted_docview_with_metadata(self, session_id: str) -> dict | None:
        try:
            # Find a record of DocumentView for session_id
            result = self.client.search(
                index = Settings.services.vectorbase.documentview_index,
                query = {"term": {"session_id": session_id}},
                size = 1
            )
        # There are may be no documents
        except Exception:
            return None

        if result and len(result["hits"]["hits"]) > 0:
            extracted_dict = result["hits"]["hits"][0]
            return extracted_dict

        return None
    

    def get_extracted_info(self, session_id: str) -> DocumentView | None:
        """Get the saved DocumentView by session_id

        Return None if there is no matching DocumentView
        """
        extracted_dict = self._find_extracted_docview_with_metadata(session_id)
        if extracted_dict is not None:
            extracted_dict = extracted_dict["_source"]
            extracted = DocumentView(**extracted_dict)
            return extracted
        
        return None

    
    def delete_extracted_info(self, session_id: str) -> None:
        extracted_dict = self._find_extracted_docview_with_metadata(session_id)
        try:
            extracted_id = extracted_dict["_id"]

            self.client.delete(
                index = Settings.services.vectorbase.documentview_index,
                id = extracted_id
            )
        except:
            # If we can't delete - there is no recording to delete
            # So we just log it, we can't delete anythings with this id
            logger.info("There is no extracted info for this session_id = %s", session_id)
            pass