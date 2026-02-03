import json
from time import time
from langchain_core.messages import message_to_dict

from .langchain_chat_history import OpenSearchChatMessageHistory
from gm_services.database.vectorstore import OpenSearchConnection
from gm_services.config import Settings

from langchain_core.messages import BaseMessage

import logging
logger = logging.getLogger(__name__)


class OpenSearchChatMessageHistoryWithParameters(OpenSearchChatMessageHistory):
    """
    Inherited custom class to add new parameters when saving message with 
    Langchain RunnableWithMessageHistory.
    
    So we can add addtional parameters that are needed to be save with message
    """
    def add_message(self, message: BaseMessage, rating: int = 0):
        """
        Add messages to the chat session in Elasticsearch
        
        Rewritten method from super().add_message()
        """
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
                # Parameters below were added
                # ---------------------------
                "rating": rating 
                # ---------------------------
            },
            refresh=True,
        )
        logger.info("Messages added to OpenSearch.")



def get_session_history(session_id) -> OpenSearchChatMessageHistoryWithParameters:
    client = OpenSearchConnection()

    # Actual MessageHistory class
    history = OpenSearchChatMessageHistoryWithParameters(
        es_connection = client.client,
        index = Settings.services.vectorbase.indexes.message_history, 
        session_id = session_id,
        esnsure_ascii = False
    )
    return history