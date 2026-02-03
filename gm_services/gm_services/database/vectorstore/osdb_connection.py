import os
from opensearchpy import OpenSearch
from langchain_community.vectorstores import OpenSearchVectorSearch

from ...neural.models.embeddings import EmbeddingsCall
from ...config import Settings, EMBEDDINGS_MODEL_TYPE


class OpenSearchConnection:
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
        # 2) here, is OpenSearchConnection, make connection again with the same credits.
        # We choose 2nd option
        if embeddings_model_name is None:
            embeddings_model_name = Settings.models.embeddings
        embeddings = EmbeddingsCall(model_name = embeddings_model_name)

        self.vectorstore = OpenSearchVectorSearch(
            opensearch_url = Settings.services.vectorbase.base_url,
            index_name = Settings.services.vectorbase.indexes.documents,
            embedding_function = embeddings
        )
