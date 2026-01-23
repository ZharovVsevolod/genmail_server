import json
from langchain_core.messages import messages_from_dict

from gm_services.database.vectorstore import OpenSearchConnection
from gm_services.common import cut_thinking_part_of_message, generate_hex
from gm_services.config import Settings

from langchain_core.messages import BaseMessage
from typing import Any, Literal

import logging
logger = logging.getLogger(__name__)


HISTORY_MESSAGE_TYPE = Literal["dict", "langchain", "api"]


class OpenSearchChatHandler(OpenSearchConnection):
    def __init__(self):
        super().__init__()

    # ---------------
    # Message history
    # ---------------
    def _transform_messages(
        self,
        messages: list[dict[str, Any]], 
        mode: HISTORY_MESSAGE_TYPE
    ) -> list[dict[str, Any]] | list[BaseMessage]:
        # Get the right form of items
        match mode:
            case "dict":
                # item is already dict - there is no need in anything
                pass

            case "langchain":
                messages = messages_from_dict(messages)

            case "api":
                transformed_messages = []
                for message in messages:
                    # Actual message
                    message_to_send = message["data"]["content"]

                    # Rating transform from digit to string
                    api_rating = message["data"]["additional_kwargs"]["rating"]
                    if api_rating == 1:
                        api_rating = "like"
                    if api_rating == -1:
                        api_rating = "dislike"
                    
                    # Sender transform from ai/human to names
                    if message["data"]["type"] == "ai":
                        sender = Settings.web.run_name
                        # Cut thinking part if ai type
                        if Settings.models.thinking_mode:
                            message_to_send = cut_thinking_part_of_message(
                                message = message_to_send
                            )
                    
                    else:
                        sender = "Вы"


                    msg = {
                        "id": message["data"]["id"],
                        "sender": sender,
                        "message": message_to_send,
                        "message_id": message["data"]["id"],
                        "rating": api_rating
                    }
                    transformed_messages.append(msg)
                
                # Backwards compatibility
                messages = transformed_messages
        
        return messages


    def get_messages(
        self, 
        session_id: str,
        mode: HISTORY_MESSAGE_TYPE = "dict"
    ) -> list[dict[str, Any]] | list[BaseMessage]:
        """Get the messages by the session id"""
        # This function was gotten from 
        # > langchain_elasticsearch.chat_history.ElasticsearchChatMessageHistory.get_messages()
        # with small adjustments, like:
        #     - added message id to ["data"]["id"]
        # 
        search_after: dict[str, Any] = {}
        items = []

        while True:
            try:
                result = self.client.search(
                    index = Settings.services.vectorbase.history_index,
                    query = {"term": {"session_id": session_id}},
                    sort = "created_at:asc",
                    size = 100,
                    **search_after,
                )
            except Exception as err:
                logger.error("Could not retrieve messages from OpenSearch: %s", err)
                raise err

            if result and len(result["hits"]["hits"]) > 0:
                for document in result["hits"]["hits"]:
                    # Actual langchain history
                    item = json.loads(document["_source"]["history"])
                    
                    # Message metadata
                    item["data"]["id"] = document["_id"] # Add message id
                    item["data"]["additional_kwargs"]["rating"] = document.get("rating", None)

                    items.append(item)
                search_after = {"search_after": result["hits"]["hits"][-1]["sort"]}
            else:
                break
        
        items = self._transform_messages(items, mode)
        
        return items


    def get_message_by_id(
        self,
        session_id: str,
        message_id: str,
        mode: HISTORY_MESSAGE_TYPE = "dict"
    ) -> list[dict[str, Any]] | list[BaseMessage] | None:
        """
        Returns
        -------
        message: list[dict[str, Any]] | list[BaseMessage] | None
            Message that matched with provided `message_id`. Type based on `mode` parameter.  
            Could be *None* if there were no matched messages.
        """
        messages = self.get_messages(session_id, mode)

        result = None
        for message in messages:
            if message["data"]["id"] == message_id:
                result = message
                break
        
        if result is None:
            logger.exception("There is no message with that message_id: %s", message_id)
            return None
        
        result = self._transform_messages(messages=[result], mode=mode)[0]
        
        return result


    def get_last_message_id(self, session_id: str) -> str:
       return self.get_messages(session_id)[-1]["data"]["id"]
    

    def update_langchain_message(
        self, 
        message_id: str, 
        parameter_name: str, 
        parameter_value: Any
    ) -> None:
        """Update parameter in history.additional_kwargs"""
        self.client.update(
            index = Settings.services.vectorbase.history_index,
            id = message_id,
            doc = {parameter_name: parameter_value}
        )
    

    # ------------
    # User's chats
    # ------------
    def add_chat_id(
        self, 
        user_id: str, 
        session_id: str, 
        session_name: str = "Название чата"
    ) -> None:
        recording = {
            "user_id": user_id,
            "session_name": session_name
        }

        self.client.create(
            index = Settings.services.vectorbase.user_chats,
            id = session_id,
            document = recording
        )
    
    
    def update_chat_id(
        self,
        session_id: str,
        session_name: str
    ) -> None:
        self.client.update(
            index = Settings.services.vectorbase.user_chats,
            id = session_id,
            doc = {
                "session_name": session_name
            }
        )
    
    
    def get_chat_ids(self, user_id: str) -> list[dict[str, str]] | None:
        """
        Returns
        -------
        user_chats: list[dict[str, str]]
            List of user chats belongs to `user_id`.
            Dictionary has this structure:
            ```
            [
                {
                    "session_id": "name of session",
                    "name: "name of session"
                }
            ]
            ```
        """
        try:
            # Find 100 records of saved session_id for current user_id
            result = self.client.search(
                index = Settings.services.vectorbase.user_chats,
                query = {"term": {"user_id": user_id}},
                size = 100
            )
        except Exception as err:
            logger.exception("Could not find any session_id for user_id = %", user_id)
            logger.error(err)
            raise err
        
        if result and len(result["hits"]["hits"]) > 0:
            result = result["hits"]["hits"]

            user_chats = []
            for record in result:
                user_chats.append({
                    "session_id": record["_id"],
                    "name": record["_source"]["session_name"]
                })
                
            return user_chats

        return None
    
    def delete_chat_id(self, session_id: str) -> None:
        try:
            self.client.delete(
                index = Settings.services.vectorbase.user_chats,
                id = session_id
            )
        except:
            logger.info("There is no chat with session_id = %s", session_id)
            pass
    

    # --------------
    # Prompt library
    # --------------
    def add_prompt_library(self, user_id: str, prompt: str, name: str) -> str:
        """
        Return an id of this prompt recording in library
        """
        prompt_id = generate_hex(8)
        recording = {
            "user_id": user_id,
            "name": name,
            "prompt": prompt
        }

        self.client.create(
            index = Settings.services.vectorbase.prompt_library,
            id = prompt_id,
            document = recording
        )

        return prompt_id


    def get_prompt_library(self, user_id: str) -> list[dict[str, str]]:
        """
        Returns
        -------
        prompt_library: list[dict[str, str]]
            List of prompt library belongs to `user_id`.
            Dictionary has this structure:
            ```
            [
                {
                    "prompt_id": "id of recording",
                    "name": "name of this prompt",
                    "prompt": "text of this prompt"
                }
            ]
            ```
        """
        try:
            # Find 100 records of saved prompts for current user_id
            result = self.client.search(
                index = Settings.services.vectorbase.prompt_library,
                query = {"term": {"user_id": user_id}},
                size = 100
            )
        except Exception as err:
            logger.info("Could not find any saved prompts for user_id = %s", user_id)
            logger.info(err)
            return []
        
        if result and len(result["hits"]["hits"]) > 0:
            result = result["hits"]["hits"]

            prompt_library = []
            for record in result:
                prompt_library.append({
                    "prompt_id": record["_id"],
                    "name": record["_source"]["name"],
                    "prompt": record["_source"]["prompt"]
                })
                
            return prompt_library

        return []


    def delete_prompt_library(self, prompt_id: str) -> None:
        try:
            self.client.delete(
                index = Settings.services.vectorbase.prompt_library,
                id = prompt_id
            )
        except:
            # If there is an error - there is no recording with this id
            # So we just log it, we can't delete anythings with this id
            logger.info("There is no prompt with id = %s in prompt library", prompt_id)
            pass
    
    
    def update_prompt_library(self, prompt_id: str, prompt: str, name: str) -> None:
        self.client.update(
            index = Settings.services.vectorbase.prompt_library,
            id = prompt_id,
            doc = {
                "name": name,
                "prompt": prompt
            }
        )
