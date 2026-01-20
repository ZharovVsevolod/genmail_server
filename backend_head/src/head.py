from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from .mail.extract import Extractor
from .mail.understand import PromptRunner
from .mail.generate import Chat
from .mail.formalize import DocumentFormalizer
from .neural.model import MLModelShell
from .neural.tools import MainToolkit, ToolCallingRunnable
from .services.databases.vectorstore import ElasticHandler
from .services.databases.vectorstore.history import get_session_history
from .services.databases.graphstore import Neo4jHandler
from .services.databases.tablestore import PGHandler
from .common import load_prompt, cut_thinking_part_of_message, unmark
from .config import Settings

from .mail.schemas_mail import DocumentView, ExtractedDocument
from .services.databases.vectorstore.elastic_connection import HISTORY_MESSAGE_TYPE
from .services.databases.tablestore.table_schemas.user import User
from .neural.tools.tool_interface import TOOL_NAMES
from langchain_core.messages import BaseMessage
from typing import Literal, Any

from dotenv import load_dotenv
load_dotenv()

import logging
logger = logging.getLogger(__name__)


RUNNALE_TYPES = Literal["default", "mail"]


class Head:
    def __init__(self):
        # LLM
        self.model = MLModelShell(
            embeddings_name=Settings.models.embeddings,
            llm_name=Settings.models.llm,
            device=Settings.system.device
        )
        logger.info("Connection established with LLM")

        # Services
        self.vector_base = ElasticHandler(model_shell=self.model)
        self.graph_base = Neo4jHandler(driver = "langchain", model = self.model)
        self.tablestore = PGHandler()

        # Inner modules
        self.extractor = Extractor()
        self.promptrunner = PromptRunner(model=self.model)
        self.chat = Chat(model=self.model, vector_base=self.vector_base)
        self.formalizer = DocumentFormalizer(
            model = self.model, 
            graph = self.graph_base,
            tablestore = self.tablestore
        )
        logger.info("Mail Head loaded")

        # Tools
        self.toolkit = MainToolkit()


    # --------------
    # Mirror methods
    # --------------
    def find_user(self, user_id: str) -> User | None:
        """Return `User` if there is a match, or `None` if nothing was found"""
        return self.tablestore.find_user(user_id)
    
    def check_password(self, user_id: str, user_password: str) -> bool:
        return self.tablestore.check_password(user_id, user_password)


    def similarity_search(self, query: str) -> str:
        return self.chat.similarity_search(query)
    

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
    

    def add_extracted_info(self, session_id: str, extracted: DocumentView) -> None:
        self.vector_base.add_extracted_info(session_id, extracted)
    
    def get_extracted_info(self, session_id: str) -> DocumentView | None:
        """Get the saved DocumentView by session_id

        Return None if there is no matching DocumentView
        """
        return self.vector_base.get_extracted_info(session_id)
    
    def delete_extracted_info(self, session_id: str) -> None:
        self.vector_base.delete_extracted_info(session_id)
    

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
    

    def extract_text(self, folder_path: str) -> list[ExtractedDocument]:
        logger.info("Path where documents that need to be procced: %s", folder_path)
        try:
            extracted = self.extractor.extract_from_folder(folder_path)
        except Exception as e:
            logger.exception("Error: %s", e)
        
        logger.info("Extracted text: %s", extracted)
        return extracted
    

    def llm_get_info_from_text(self, extracted: list[ExtractedDocument]) -> list[DocumentView]:
        result = self.promptrunner.run(contexts=extracted)
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