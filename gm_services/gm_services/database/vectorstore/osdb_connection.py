import os
from uuid import uuid4
from opensearchpy import OpenSearch
from langchain_community.vectorstores import OpenSearchVectorSearch

from ...common import generate_hex
from ...schemas.understanding import DocumentView

from langchain_core.documents import Document
from ...neural.models.embeddings import EmbeddingsCall
from ...config import Settings, EMBEDDINGS_MODEL_TYPE
from typing import Any

import logging
logger = logging.getLogger(__name__)


class BaseOpenSearchConnection:
    def __init__(
        self, 
        embeddings_model_name: EMBEDDINGS_MODEL_TYPE | None = None
    ) -> None:
        # Compatibility layer
        address = Settings.services.vectorbase.base_url.split("//")[-1]
        [host, port] = address.split(":")
        available_hosts = [{"host": host, "port": port}]

        auth = (
            os.environ["OPENSEARCH_LOGIN"], 
            os.environ["OPENSEARCH_PASSWORD"]
        )

        self.client = OpenSearch(
            hosts = available_hosts,
            http_compress = True, # enables gzip compression for request bodies
            http_auth = auth,
            use_ssl = True,
            verify_certs = False,
            ssl_assert_hostname = host,
            ssl_show_warn = False
        )

        # Because of implementation of original `OpenSearchVectorSearch` class,
        # that is connecting to OpenSearch database with the same credentials and
        # we can't just provide to it original OpenSearch client, we have here two options:
        # 1) make custom OpenSearchVectorSearch with __init__ to be rewritten;
        # 2) here, is OpenSearchConnection, make connection again with the same credits;
        # 3) revalue OpenSearch client inside the new Langchain class here, after initialization.
        # We choose 3nd option
        if embeddings_model_name is None:
            embeddings_model_name = Settings.models.embeddings
        embeddings = EmbeddingsCall(model_name = embeddings_model_name)


        # OpenSearch (or specific Langchain version of connection to it) couldn't handle
        # the size of a vector to be created. So we need to manually (?!) set it and pray
        # that size wouldn't be overfitted. Or I have no idea what's this about, haven't I?
        self.max_vector_size = 4000

        self.vectorstore = OpenSearchVectorSearch(
            opensearch_url = Settings.services.vectorbase.base_url,
            index_name = Settings.services.vectorbase.indexes.documents,
            embedding_function = embeddings,
            engine = "lucene", # Need to set up manually because of depricated default engine
            bulk_size = self.max_vector_size
        )

        # Set the proper OpenSearch client
        self.vectorstore.client = self.client


    @staticmethod
    def _create_uuids(n: int) -> list[str]:
        uuids = [str(uuid4()) for _ in range(n)]
        return uuids

    def delete_index(self, index_name: str) -> None:
        self.client.indices.delete(index = index_name)
    
    def add_documents(
        self, 
        docs: list[Document] | list[dict],
        index_name: str | None = None
    ) -> None:
        """
        Add document to VectorStore

        Documents could be Langchain type for retriever, or just a dict for
        any other cases.

        Arguments
        ---------
        docs: list[Document] | list[dict]
            Documents that needed to be added to VectorStore index.  
            Could be:
                - Langchain Document (for retriever)
                - Python Dict (for other needs)
        
        index_name: str | None = None
            If this documents *not* for a retriever, need to specify to what index
            we need to add this documents.  
            Defaults to *None* (documents _are_ for retriever by default)
        """
        uuids = self._create_uuids(len(docs))

        if index_name is None:    
            self.vectorstore.add_documents(documents = docs, ids = uuids)
        
        else:
            # Create index if doesn't exist
            if not self.client.indices.exists(index = index_name):
                self.client.indices.create(index = index_name)
            
            # One by one put documents to this index
            for i, doc in enumerate(docs):
                self.client.index(
                    index = index_name,
                    id = uuids[i],
                    body = doc
                )
    
    def update_document(
        self, 
        index_name: str, 
        doc_id: str, 
        doc_body: dict[str, Any]
    ) -> None:
        self.client.update(
            index = index_name,
            id = doc_id,
            body = doc_body
        )


# Here we share some methods for multiple blocks
class OpenSearchConnection(BaseOpenSearchConnection):
    def __init__(
        self, 
        embeddings_model_name: EMBEDDINGS_MODEL_TYPE | None = None
    ) -> None:
        super().__init__(embeddings_model_name)

    # ------------------
    # Save document data
    # ------------------
    def add_extracted_info(self, session_id: str, extracted: DocumentView) -> None:
        # Make DocumentView dict-type
        extracted_dict = extracted.model_dump(mode="python")
        # Add session_id parameter
        extracted_dict["session_id"] = session_id
        # Create a record to the database
        self.client.create(
            index=Settings.services.vectorbase.indexes.documents,
            id=generate_hex(8),
            document=extracted_dict,
        )

    def _find_extracted_docview_with_metadata(self, session_id: str) -> dict | None:
        try:
            # Find a record of DocumentView for session_id
            result = self.client.search(
                index=Settings.services.vectorbase.indexes.documents,
                query={"term": {"session_id": session_id}},
                size=1,
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
                index=Settings.services.vectorbase.indexes.documents, id=extracted_id
            )
        except:
            # If we can't delete - there is no recording to delete
            # So we just log it, we can't delete anythings with this id
            logger.info(
                "There is no extracted info for this session_id = %s", session_id
            )
            pass
