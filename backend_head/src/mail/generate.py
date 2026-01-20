from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from .schemas_mail import BaseGenerationBody
from ..config import Settings

from langchain_core.messages import BaseMessage
from ..neural import MLModelShell
from .schemas_mail import DocumentView
from ..services.databases.vectorstore.elastic_connection import ElasticHandler
from typing import List, Literal

class HistoryMessage(BaseModel):
    type: Literal["system", "ai", "human"]
    message: str


def add_history(
    user_message: str,
    llm_message: str,
    history: list[BaseMessage]
) -> list[BaseMessage]:
    history += [HumanMessage(user_message), AIMessage(llm_message)]
    return history


def original_history_convertion(history: list[BaseMessage]) -> list[HistoryMessage]:
    converted = []

    if history != []:
        for message in history:
            if type(message) is SystemMessage:
                message_type = "system"
            if type(message) is AIMessage:
                message_type = "ai"
            if type(message) is HumanMessage:
                message_type = "human"

            msg = HistoryMessage(
                type = message_type, 
                message = message.content
            )
            converted.append(msg)
    
    return converted


def database_history_convertion(history: list[HistoryMessage]) -> list[BaseMessage]:
    converted = []

    if history != []:
        for message in history:
            match message.type:
                case "system":
                    msg = SystemMessage(message.message)

                case "ai":
                    msg = AIMessage(message.message)

                case "human":
                    msg = HumanMessage(message.message)

            converted.append(msg)
    
    return converted

class Chat:
    def __init__(
        self, 
        model: MLModelShell,
        vector_base: ElasticHandler, 
    ):
        self.model = model
        self.vector_base = vector_base
        self.prompt_path = Settings.models.full_prompts_path

    def _messages_with_history(
        self,
        query: str,
        system_prompt: str,
        history: list[BaseMessage] | None
    ) -> list[BaseMessage]:
        prompt = ChatPromptTemplate([
            ("placeholder", "{conversation}"),
            ("user", query)
        ])

        messages = prompt.invoke({
            "query": query, 
            "conversation": history
        })

        messages = [SystemMessage(system_prompt)] + messages.to_messages()
        return messages
    

    def create_system_prompt(
        self, 
        context: DocumentView, 
        retrieved_context: str | None = None
    ) -> str:
        prompt_name = "dialog_for_runnable.md"
        system_prompt = self.load_prompt(self.prompt_path + prompt_name)

        system_prompt = system_prompt.format(
            information = context.to_str(),
            retrieved_context = str(retrieved_context)
        )
        return system_prompt


    def run(self,
            user_query: str,
            context: DocumentView,
            dialog_history: List
    ) -> BaseGenerationBody:
        history = []
        if dialog_history is None:
            retrieved_context = self.similarity_search(query=context.theme)
            if retrieved_context is not None:
                prompt = "dialog_with_retrieve.md"
            else:
                prompt = "dialog.md"
            system_prompt_template = self.load_prompt(self.prompt_path + prompt)

            if retrieved_context is not None:
                system_prompt = system_prompt_template.replace("{retrieved_context}", retrieved_context)
        
            system_prompt = system_prompt.replace("{theme}", context.theme)
            system_prompt = system_prompt.replace("{summary}", context.summary)
            messages = [SystemMessage(system_prompt), HumanMessage(user_query)]
        else:
            history = database_history_convertion(dialog_history)
            messages = self._messages_with_history(user_query, system_prompt, history)

        response = self.model.llm_answer(
            messages=messages,
            llm_answer_parser="json"
        )
        llm_message = response['letter_body']
        # if len(history):
        history = add_history(user_query, llm_message, history)
        
        return BaseGenerationBody(letter_body=llm_message, history=history)
    
    
    def similarity_search(self, query: str) -> str:
        found_documents = self.vector_base.similarity_search(
            query = query,
            return_format = "str"
        )
        return found_documents


    def load_prompt(self, path_to_prompt: str) -> str:
        with open(path_to_prompt, encoding = "utf-8") as file:
            result = file.read()
        
        return result

