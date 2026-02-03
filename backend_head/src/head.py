import asyncio
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from .mail.understand import PromptRunner
from .mail.formalize import DocumentFormalizer
from gm_services.clients import DocumentHandlerClient
from gm_services.neural.llm import LLModelShell
from gm_services.neural.llm.tools import MainToolkit, ToolCallingRunnable
from .db_handle.osdb_chat import OpenSearchChatHandler
from .db_handle.history import get_session_history
from gm_services.database.tablestore import PGHandler
from gm_services.common import load_prompt, cut_thinking_part_of_message, unmark
from gm_services.schemas.document_handler import TranscriptionStatusEnum
from gm_services.config import Settings

from gm_services.schemas.extraction import ExtractedDocument
from gm_services.schemas.document_handler import TranscriptionResponse
from gm_services.schemas.understanding import DocumentView
from .db_handle.osdb_chat import HISTORY_MESSAGE_TYPE
from gm_services.database.tablestore.table_schemas.user import User
from gm_services.neural.llm.tools.tool_interface import TOOL_NAMES
from langchain_core.messages import BaseMessage
from fastapi import UploadFile
from typing import Literal, Any

from dotenv import load_dotenv
load_dotenv()

import logging
logger = logging.getLogger(__name__)


RUNNALE_TYPES = Literal["default", "mail"]


class Head:
    def __init__(self):
        # LLM
        self.model = LLModelShell(Settings.models.llm)

        # Databases
        self.vector_base = OpenSearchChatHandler()
        self.tablestore = PGHandler()

        # Inner modules
        self.document_handler = DocumentHandlerClient()
        self.promptrunner = PromptRunner(model = self.model)
        self.formalizer = DocumentFormalizer(
            model = self.model, 
            tablestore = self.tablestore
        )

        # Tools
        self.toolkit = MainToolkit()
        logger.info("Main Backend Head loaded")


    # --------------
    # Mirror methods
    # --------------
    # User
    def find_user(self, user_id: str) -> User | None:
        """Return `User` if there is a match, or `None` if nothing was found"""
        return self.tablestore.find_user(user_id)
    
    def check_password(self, user_id: str, user_password: str) -> bool:
        return self.tablestore.check_password(user_id, user_password)


    # TODO
    # Retrieval
    def similarity_search(self, query: str) -> str:
        pass
    
    
    # Message history
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
        return self.vector_base.get_message_by_id(session_id, message_id, mode)
    
    def get_last_message_id(self, session_id: str) -> str:
        return self.vector_base.get_last_message_id(session_id)
    
    def get_messages(
        self, 
        session_id: str,
        mode: HISTORY_MESSAGE_TYPE = "dict"
    ) -> list[dict[str, Any]] | list[BaseMessage]:
        return self.vector_base.get_messages(session_id, mode)

    def update_langchain_message(
        self, 
        message_id: str, 
        parameter_name: str, 
        parameter_value: Any
    ) -> None:
        """Update parameter in history.additional_kwargs"""
        self.vector_base.update_langchain_message(message_id, parameter_name, parameter_value)
    

    # Document extraction
    def remove_document_session_id_placeholder(
        self, 
        user_id: str, 
        session_id: str
    ) -> None:
        """
        Replace a document session_id placeholder with valid session_id value
        
        **Comment**: This is needed to be done because when new documents are uploaded there is
        no actual session_id in exist, because new session starts right after user's click,
        and value could not be created at this point. So document firstly registrated with user_id and
        DOCUMENT_SESSION_ID_PLACEHOLDER and then we must replace it with a real value once we got to the point
        where it matters
        """
        self.vector_base.remove_document_session_id_placeholder(user_id, session_id)
    

    # TODO
    # This will be another module, not self.vectorbase
    def add_extracted_info(self, session_id: str, extracted: DocumentView) -> None:
        self.vector_base.add_extracted_info(session_id, extracted)
        pass

    
    # TODO
    def get_extracted_info(self, session_id: str) -> DocumentView | None:
        """Get the saved DocumentView by session_id

        Return None if there is no matching DocumentView
        """
        # return self.vector_base.get_extracted_info(session_id)
        pass

    
    # TODO
    def delete_extracted_info(self, session_id: str) -> None:
        # self.vector_base.delete_extracted_info(session_id)
        pass

    
    # User's chats
    def add_chat_id(
        self, 
        user_id: str, 
        session_id: str, 
        session_name: str = "Название чата"
    ) -> None:
        self.vector_base.add_chat_id(user_id, session_id, session_name)
    
    def update_chat_id(
        self,
        session_id: str,
        session_name: str
    ) -> None:
        self.vector_base.update_chat_id(session_id, session_name)
    
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
        return self.vector_base.get_chat_ids(user_id)
    
    def delete_chat_id(self, session_id: str) -> None:
        self.vector_base.delete_chat_id(session_id)
    

    # User's prompt library
    def add_prompt_library(self, user_id: str, prompt: str, name: str) -> str:
        """
        Return an id of this prompt recording in library
        """
        return self.vector_base.add_prompt_library(user_id, prompt, name)

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
        return self.vector_base.get_prompt_library(user_id)
    
    def delete_prompt_library(self, prompt_id: str) -> None:
        self.vector_base.delete_prompt_library(prompt_id)
    
    def update_prompt_library(self, prompt_id: str, prompt: str, name: str) -> None:
        self.vector_base.update_prompt_library(prompt_id, prompt, name)
    
    # ----------------
    # ----------------
    # ----------------
    
    async def files_upload(
        self, 
        files: list[UploadFile],
        user_id: str,
        session_id: str
    ) -> None:
        "Upload multiple files, register them to user and current session_id"
        document_ids = []
        for file in files:
            # Upload file to database
            document_info = await self.document_handler.files_upload(
                user_id = user_id,
                file_data = file.file,
                content_type = file.content_type,
                filename = file.filename
            )
            document_ids.append(document_info.id)

        # Connect this documents to chat
        self.vector_base.add_docs_to_chat(
            doc_ids = document_ids,
            user_id = user_id,
            session_id = session_id
        )

    
    async def extract_text(self, user_id: str, session_id: str) -> list[ExtractedDocument]:
        extracted_texts = []

        doc_ids = self.vector_base.get_doc_ids_of_chat(session_id)
        for doc_id in doc_ids:
            task = await self.document_handler.create_transcribe_task(user_id, doc_id)

            while True:
                status = await self.document_handler.get_status(task.id)
                if status.status == TranscriptionStatusEnum.SUCCESS:
                    extracted_text: TranscriptionResponse = await self.document_handler.get_meta(task.id)
                    extracted_texts.append(ExtractedDocument.model_validate(extracted_text.content))
                    break
                else:
                    asyncio.sleep(5.0) # Wait for 5 seconds for the next ask

        return extracted_texts
    

    def llm_get_info_from_text(self, extracted: list[ExtractedDocument]) -> list[DocumentView]:
        result = self.promptrunner.run(
            task = "TextAnalyze",
            document_context = extracted
        )
        logger.info("LLM get some information from text")
        return result

    
    def proceed(self, folder_path: str) -> list[DocumentView]:
        extracted = self.extract_text(folder_path)
        result = self.llm_get_info_from_text(extracted)
        return result
    

    def _prepare_text(self, session_id: str, message_id: str) -> str:
        # Load the text of message from vectorbase
        text = self.get_message_by_id(session_id, message_id)
        text: str = text["data"]["content"]

        # Cut the think part if there is any
        if "<think>" in text:
            text = cut_thinking_part_of_message(text)
        
        # Get rid of markdown markup
        text = unmark(text)
        
        return text


    def formalize(
        self, 
        session_id: str, 
        user_id: str,
        message_id: str | None = None
    ) -> str:
        """
        Returns
        -------
        final_name: str
            Name of generated file
        """
        # Set the last message if there is no provided message_id
        if message_id is None:
            message_id = self.get_last_message_id(session_id)
        
        text = self._prepare_text(session_id, message_id)

        user = self.find_user(user_id)
        
        # Actually formalization module work
        docname = self.formalizer.formalize(
            user = user,
            document_info = self.get_extracted_info(session_id),
            text = text,
            doc_type = "docx",
            random_name = False
        )
        # Return the name of file
        return docname
    

    # ----------------------------
    # Runnable for token streaming
    # ----------------------------
    def create_runnable_chain(
        self,
        mode: RUNNALE_TYPES,
        # Parameters for mail mode
        context: DocumentView | None = None,
        # Tools if needed
        tools: Literal["all"] | list[TOOL_NAMES] | None = None
    ) -> RunnableWithMessageHistory:
        """Set runnable chain of langchain for token streaming"""
        # Load the right system prompt
        match mode:
            case "default":
                system = load_prompt("default.md", default_path = True)

            case "mail":
                system = load_prompt("runnable_dialog.md", default_path = True)
                system = system + context.to_str()

        prompt = ChatPromptTemplate.from_messages([
            ("system", system),
            MessagesPlaceholder(variable_name="history"),
            ("user", "{input}")
        ])

        # Bind tools if needed
        if tools is None:
            llm = self.model.llm
            chain = prompt | llm
            # Get the String parser with run name - because of token streaming in Web interface
            str_parser = StrOutputParser().with_config({"run_name": Settings.web.run_name})
            chain = chain | str_parser
        
        else:
            llm = self.model._llm_with_tools(tools)
            tool_calling_runnable = ToolCallingRunnable(
                llm = llm, 
                toolkit = self.toolkit
            ).with_config({"run_name": Settings.web.run_name})
            chain = prompt | tool_calling_runnable


        # Set the final runnable chain
        runnable = RunnableWithMessageHistory(
            runnable = chain,
            get_session_history = get_session_history,
            input_messages_key = "input",
            history_messages_key = "history"
        )
        return runnable



# ----------------------
# Head instance creation
# ----------------------
# Because of multiple links to the same head from different files
# here is presented a united instance of Head class
HEAD = Head()