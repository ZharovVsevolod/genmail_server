from .events_typing import (
    EVENT_NEW_MESSAGE,
    EVENT_ADD_TEXT_TO_MESSAGE,
    EVENT_STARTED_DOCUMENT_EXTRACTION,
    EVENT_STARTED_DOCUMENT_SUMMARIZATION,
    EVENT_SEND_SUMMARY,
    EVENT_THINKING_START,
    EVENT_THINKING_END,
    EVENT_GENERATION_END,
    EVENT_SEND_FILENAME_FOR_DOWNLOAD,
    EVENT_SEND_NEW_CHAT_ID,
    EVENT_SEND_PREVIOUS_CHAT_HISTORY,
    CUSTOM_EVENT_NAME,
    RATING_TYPE,
    EVENT_AUTH_ERROR,
    EVENT_AUTH_SUCCESS
)
from ....head import HEAD
from gm_services.common import generate_hex, to_json_safe
from gm_services.neural.llm.chain_config import make_config_for_chain
from gm_services.neural.llm.custom_parsers import chain_stream_parser, is_think_continue
from gm_services.config import Settings

from fastapi import WebSocket
from langchain_core.runnables.history import RunnableWithMessageHistory
from .events_typing import API_MESSAGE_TYPE
from gm_services.united_schemes import DocumentView

import logging
logger = logging.getLogger(__name__)


# Messages
WAIT_FOR_DOCUMENT_PREPARATION = "Документ готовится..."
GENERAL_INNER_SEARCH_TOOL = "Ищу во внутренних базах..."
REFERENCE_TOOL = "Ищу референс для ответа..."


class WSHead:
    def __init__(self, websocket: WebSocket) -> None:
        self.websocket = websocket

        # Placeholders
        self.user_id: str | None = None
        self.username: str | None = None
        self.session_id: str | None = None
        self.config: dict | None = None
        self.runnable: RunnableWithMessageHistory | None = None
    

    async def _send_new_message(self, message: str) -> str:
        """
        Send a new message to chat.

        Returns
        -------
        run_id: str
            id of this message. 
            It may be use for change or add to it new phrases in future
        """
        new_run_id = generate_hex(8)
        await self.websocket.send_json({
            "event": EVENT_NEW_MESSAGE,
            "run_id": new_run_id,
            "name": Settings.web.run_name
        })
        await self.websocket.send_json({
            "event": EVENT_ADD_TEXT_TO_MESSAGE,
            "run_id": new_run_id,
            "name": Settings.web.run_name,
            "data": {"chunk": message}
        })

        return new_run_id
    

    async def _make_summary(self, folder_path: str) -> None:
        """
        Make a summary of documents (get a path to folder) 
            and send messages to front of how it is going
        """
        summary_run_id = generate_hex(8)
        # Send that document extraction process started
        await self.websocket.send_json({
            "event": EVENT_STARTED_DOCUMENT_EXTRACTION,
            "name": Settings.web.run_name,
            "run_id": summary_run_id
        })
        # Actually start extraction
        extracted_text = HEAD.extract_text(folder_path)

        # Send that document summarization process started
        await self.websocket.send_json({
            "event": EVENT_STARTED_DOCUMENT_SUMMARIZATION,
            "name": Settings.web.run_name,
            "run_id": summary_run_id
        })
        # Actually start summarization
        documents_view: DocumentView = HEAD.llm_get_info_from_text(extracted_text)
        documents_view_dict = documents_view.to_dict()
        
        # Save what we extracted
        HEAD.add_extracted_info(self.session_id, documents_view)

        # Delete unnecessary for now parameters
        del documents_view_dict["text"]
        del documents_view_dict["metadata"]

        # Send back the extracted information
        text_info = {
            "event": EVENT_SEND_SUMMARY,
            "name": Settings.web.run_name,
            "data": documents_view_dict,
            "run_id": summary_run_id
        }
        await self.websocket.send_json(text_info)
    

    async def _make_formalization(self, message_id: str) -> None:
        """
        Formalize message (of message_id) to final document
            and send a path to this document for further download
        """
        # Backward compatibility
        if message_id == "None":
            message_id = None

        # Send a message that we are making a document
        await self._send_new_message(WAIT_FOR_DOCUMENT_PREPARATION)

        # Formalize
        filename = HEAD.formalize(self.session_id, self.user_id, message_id)
        chunk = {
            "event": EVENT_SEND_FILENAME_FOR_DOWNLOAD, 
            "name": Settings.web.run_name,
            "filename": filename
        }
        await self.websocket.send_json(chunk)

    
    def _set_runnable_chain(self) -> None:
        """Define and prepare runnable for a new run"""
        # If there is an extracted info - we have a scenario with mail
        # otherwise - we use default scenario (mainly QA)
        if HEAD.get_extracted_info(self.session_id) is None:
            mode = "default"
            # Helper for tool calling
            if Settings.models.tools:
                need_tools = ["get_knowledge"]
            else:
                need_tools = None
            
            # Prepare runnable for generating part
            self.runnable = HEAD.create_runnable_chain(
                mode = mode,
                tools = need_tools
            )
        
        else:
            mode = "mail"
            # Helper for tool calling
            if Settings.models.tools:
                need_tools = ["get_reference", "graph_search"]
            else:
                need_tools = None
            
            # Prepare runnable for generating part
            self.runnable = HEAD.create_runnable_chain(
                mode = mode,
                context = HEAD.get_extracted_info(self.session_id),
                tools = need_tools
            )
    

    async def _handle_custom_events(
        self, 
        chunk: dict, 
        current_id: str,
        thinking: bool
    ) -> tuple[bool, bool]:
        """
        If there is `on_custom_event` event - we give some control to inner modules. 

        And we don't want to show user inner processes. Just inform him.
        
        Returns
        -------
        result: tuple[bool bool]
            Tuple of `custom_event_continue` and `thinking`
        
            `custom_event_continue`: bool
                - If True - a custom event (tools) in control, 
                    red lite for sending chunks to front.  
                - If False - custom events don't get control, 
                    green lite for sending chunks to front.
            
            `thinking`: bool
                If thinking was set manually to True or stayed the same
        """
        custom_event: bool = True

        # Start of tool - start of custom_event
        if chunk["name"] == "tool_call_start":
            # Switch some parameters
            custom_event = True
            if Settings.models.thinking_mode:
                thinking = True

            # Tool of searching data in Neo4j with inner LLM call
            if chunk["data"]["name"] in ["graph_search", "get_knowledge"]:
                # Send to created message bubble (on current_id)
                await self.websocket.send_json({
                    "event": EVENT_ADD_TEXT_TO_MESSAGE,
                    "run_id": current_id,
                    "name": Settings.web.run_name,
                    "data": {"chunk": GENERAL_INNER_SEARCH_TOOL}
                })
            
            # Tool of getting reference data in Vectorstore
            if chunk["data"]["name"] == "get_reference":
                # Send to created message bubble (on current_id)
                await self.websocket.send_json({
                    "event": EVENT_ADD_TEXT_TO_MESSAGE,
                    "run_id": current_id,
                    "name": Settings.web.run_name,
                    "data": {"chunk": REFERENCE_TOOL}
                })


        # End of tool - end of custom event
        if chunk["name"] == "tool_call_end":
            custom_event = False
        
        return custom_event, thinking


    async def _run_generation(self, input_message: str) -> None:
        """General LLM run and sending chunks from LLM to front"""
        # Some parameters for generation 
        thinking = True if Settings.models.thinking_mode else False
        custom_event = False
        current_id = None

        # Actual stream
        async for chunk in self.runnable.astream_events(
            {"input": input_message},
            version = "v2",
            config = self.config
        ):
            # Backward compatibility with tool calling runnable
            if Settings.models.tools:
                chunk = chain_stream_parser(chunk)
            chunk = to_json_safe(chunk)

            # Custom event handler
            # If there is `on_custom_event` event - we give some control
            # to inner modules. We need to handle it correctly
            if chunk["event"] == CUSTOM_EVENT_NAME:
                custom_event, thinking = await self._handle_custom_events(
                    chunk = chunk, 
                    current_id = current_id, 
                    thinking = thinking
                )

            # LLM output send
            # If there is a custom_event - do nothing, we just pass
            # Otherwise we send to frontend LLM output
            if not custom_event:
                match chunk["event"]:                        
                    # Creation of message bubble
                    case "on_parser_start":
                        current_id = chunk["run_id"]
                        await self.websocket.send_json(chunk)

                        if Settings.models.thinking_mode:
                            thinking = True
                            await self.websocket.send_json({
                                "event": EVENT_THINKING_START,
                                "run_id": chunk["run_id"],
                                "name": chunk["name"]
                            })

                    # Token stream
                    case "on_parser_stream":
                        # Do not send chunks until the thinking is over
                        if thinking:
                            thinking = is_think_continue(chunk["data"]["chunk"])
                            if thinking is False:
                                await self.websocket.send_json({
                                    "event": EVENT_THINKING_END,
                                    "run_id": chunk["run_id"],
                                    "name": chunk["name"]
                                })
                        
                        else:
                            await self.websocket.send_json(chunk)

        # After all generation, send the id of the final last message
        await self.websocket.send_json({
            "event": EVENT_GENERATION_END,
            "run_id": chunk["run_id"],
            "name": Settings.web.run_name,
            "message_id": HEAD.get_last_message_id(self.session_id)
        })
    

    def _update_rating(
        self, 
        message_id: str, 
        rating: RATING_TYPE | None
    ) -> None:
        """Update message rating parameter when user send us this information"""
        logger.info("Update rating called. Rating: %s, id: %s", rating, message_id)

        # Transform string rating type to int
        rating_int = 0
        match rating:
            case "like":
                rating_int = 1
            case "dislike":
                rating_int = -1
            case _:
                pass
        
        # Update rating value
        HEAD.update_langchain_message(
            message_id = message_id, 
            parameter_name = "rating",
            parameter_value = rating_int
        )
    

    async def register_user(self, user_id: str, password: str) -> bool:
        """
        Check user's credentials and link him to this handle.
        
        If user's credentials wasn't legit, send to Frontend error message.

        Returns
        -------
        is_check_fine: bool
            `True`, if user was found and password is legit. `False` otherwise.
        """
        user = HEAD.find_user(user_id)
        
        # Send error message if we didn't find the user by login
        if user is None:
            await self.websocket.send_json({
                "event": EVENT_AUTH_ERROR,
                "state": "error",
                "message": "user_not_found"
            })
            return False
        
        else:
            # Check password
            is_check_fine = HEAD.check_password(user.key_id, password)

            if is_check_fine:
                self.user_id = user.key_id
                self.username = user.name
                # Send message that everything is alright
                await self.websocket.send_json({
                    "event": EVENT_AUTH_SUCCESS,
                    "state": "success",
                    "message": "pass",
                    "user_id": user.key_id,
                    "user_name": user.name
                })
            
            else:
                # Send message that password didn't match
                await self.websocket.send_json({
                    "event": EVENT_AUTH_ERROR,
                    "state": "error",
                    "message": "password_didnt_match"
                })
            
            return is_check_fine
        

    def _update_conversation(self, session_id: str) -> None:
        """Gracefully update all settings for current session_id"""
        self.session_id = session_id

        self.config = make_config_for_chain(
            session_id = self.session_id,
            graphbase = HEAD.graph_base,
            vectorbase = HEAD.vector_base
        )
    

    async def _load_previous_chat(self, session_id: str) -> None:
        """Load previos chat and send old chat history to frontend"""
        self._update_conversation(session_id)

        messages = HEAD.get_messages(self.session_id, mode = "api")
        await self.websocket.send_json({
            "event": EVENT_SEND_PREVIOUS_CHAT_HISTORY,
            "session_id": self.session_id,
            "history": messages
        })

    # -----
    

    async def create_conversation(self) -> None:
        """Create new conversation (chat) with user"""
        session_id = generate_hex()
        HEAD.add_chat_id(self.user_id, session_id)

        self._update_conversation(session_id)

        # Send to Frontend that we created new session (chat)
        await self.websocket.send_json({
            "event": EVENT_SEND_NEW_CHAT_ID,
            "session_id": self.session_id
        })
    

    async def proceed_recieved_data(self, data: dict[str, str]) -> None:
        """
        Main proceed method.

        Matching an action type from a frontend and do whatever it need to do.
        """
        message_type: API_MESSAGE_TYPE = data["action"]

        match message_type:
            case "SUMMARY":
                # If self.session_id is None - there is no active conversation
                if self.session_id is None:
                    self.create_conversation()
                await self._make_summary(Settings.docs.full_mail_path)

            case "QUERY":
                # If self.session_id is None - there is no active conversation
                if self.session_id is None:
                    self.create_conversation()
                self._set_runnable_chain()
                message = data["message"]
                await self._run_generation(message)

            case "FORMALIZE":
                message_id = data["message_id"]
                await self._make_formalization(message_id)

            case "CREATE":
                await self.create_conversation()
            
            case "LOAD_CHAT":
                session_id = data["session_id"]
                await self._load_previous_chat(session_id)

            case "RATE":
                message_id = data["message_id"]
                rating = data.get("rating", None)
                self._update_rating(message_id, rating)