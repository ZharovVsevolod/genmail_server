# Got some code from here:
# https://github.com/opensearch-project/opensearch-py/issues/701
# and made some modifications:
# - now we can provide existing OpenSearch connection in init
# - get_messages method for compatibility

from time import time
from typing import List, Optional
import json

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import (
    BaseMessage,
    message_to_dict,
    messages_from_dict,
)

from opensearchpy import OpenSearch

import logging
logger = logging.getLogger(__name__)


class OpenSearchChatMessageHistory(BaseChatMessageHistory):
    """Chat message history that stores history in OpenSearch.

    Args:
        index (str): Name of the index to use.
        session_id (str): Arbitrary key that is used to store the messages
            of a single chat session.
        opensearch_connection (Optional[OpenSearch]): Existing connection to OpenSearch.
            Defaults to None.
        opensearch_url (Optional[str]): URL of the OpenSearch instance to connect to.
            Defaults to "http://localhost:9200".
        ensure_ascii (Optional[bool]): Used to escape ASCII symbols in json.dumps.
            Defaults to True.
    """

    def __init__(
        self,
        index: str,
        session_id: str,
        opensearch_connection: Optional[OpenSearch] = None,
        opensearch_url: Optional[str] = "http://localhost:9200",
        ensure_ascii: Optional[bool] = True,
    ) -> None:
        super().__init__()
        logger.info("Initializing the OpenSearchChatMessageHistory class.")
        self.index: str = index
        self.session_id: str = session_id
        self.ensure_ascii: bool = ensure_ascii

        if opensearch_connection is not None:
            self.client = opensearch_connection
        else:
            self.client: OpenSearch = OpenSearch([opensearch_url])

        if self.client.indices.exists(index=index):
            logger.info(
                f"Chat history index '{index}' already exists, skipping creation."
            )
        else:
            logger.info(f"Creating index '{index}' for storing chat history.")
            self.client.indices.create(
                index=index,
                body={
                    "mappings": {
                        "properties": {
                            "session_id": {"type": "keyword"},
                            "created_at": {"type": "date"},
                            "history": {"type": "text"},
                        }
                    }
                },
            )
        logger.info("OpenSearchChatMessageHistory class initialized successfully.")

    @property
    def messages(self) -> List[BaseMessage]:
        """Retrieve the messages from OpenSearch."""
        logger.info("Loading messages from OpenSearch to buffer.")
        result = self.client.search(
            index=self.index,
            body={
                "query": {
                    "term": {
                        "session_id": self.session_id
                    }
                }
            },
            sort="created_at:asc",
        )

        items = [
            json.loads(document["_source"]["history"])
            for document in result.get("hits", {}).get("hits", [])
        ] if result else []

        logger.info("Messages loaded from OpenSearch to buffer.")
        return [messages_from_dict(item) for item in items]
    
    def get_messages(self) -> List[BaseMessage]:
        return self.messages

    def add_message(self, message: BaseMessage) -> None:
        """Add a message to the chat session in OpenSearch."""
        logger.info("Adding messages to OpenSearch.")
        self.client.index(
            index=self.index,
            body={
                "session_id": self.session_id,
                "created_at": round(time() * 1000),
                "history": json.dumps(
                    message_to_dict(message),
                    ensure_ascii=self.ensure_ascii,
                ),
            },
            refresh=True,
        )
        logger.info("Messages added to OpenSearch.")

    def clear(self) -> None:
        """Clear session memory in OpenSearch."""
        logger.info("Purging data in OpenSearch started.")
        self.client.delete_by_query(
            index=self.index,
            body={
                "query": {
                    "term": {
                        "session_id": self.session_id
                        }
                    }
                },
            refresh=True,
        )
        logger.info("OpenSearch data purged.")