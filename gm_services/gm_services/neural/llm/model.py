import ast

from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI

from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers.json import JsonOutputParser
from langchain_core.output_parsers import StrOutputParser

from .tools import MainToolkit
from ..common import cut_thinking_part_of_message
from ..config import Settings

from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableConfig
from .tools.tool_interface import TOOL_NAMES
from ..config import (
    EMBEDDINGS_MODEL_TYPE,
    LLM_MODEL_TYPE,
    DEVICE_TYPE,
    LLM_ANSWER_PARSER_TYPE
)
from typing import Literal

import logging
logger = logging.getLogger(__name__)


ERROR_MESSAGE = """Извините, что-то пошло не так. 
Пожалуйста, переформулируйте Ваш ответ или перезагрузите страницу."""


class MLModelShell:
    def __init__(
        self,
        embeddings_name: EMBEDDINGS_MODEL_TYPE,
        llm_name: LLM_MODEL_TYPE,
        device: DEVICE_TYPE | None = None
    ) -> None:
        if device is None:
            device = Settings.system.device

        self.embeddings = self._init_embeddings(embeddings_name, device)
        if Settings.system.server:
            self.llm = self._init_llm_model(llm_name)
        else:
            self.llm = self._init_llm_model_local(llm_name)
        self.toolkit = self._init_toolkit()
    

    def _init_llm_model(self, llm_name: LLM_MODEL_TYPE) -> ChatOpenAI:
        model_path = self._match_model_path(llm_name)
        llm = ChatOpenAI(
            model = model_path,
            api_key = "EMPTY",
            base_url = Settings.services.llm_engine.base_url,
            temperature = 0.6,
            top_p = 0.95
        )
        return llm
    

    def _init_llm_model_local(self, llm_name: LLM_MODEL_TYPE):
        from langchain_ollama import ChatOllama
        llm = ChatOllama(
            model = llm_name,
            temperature = 0.6,
            top_p = 0.95,
            top_k = 20
        )
        return llm


    def _match_model_path(
        self, 
        model_name: LLM_MODEL_TYPE | EMBEDDINGS_MODEL_TYPE
    ) -> str:
        match model_name:
            # LLM_MODEL_TYPE
            case "qwen3:14b":
                model_path = "Qwen/Qwen3-14B"

            case "qwen3:8b":
                model_path = "Qwen/Qwen3-8B"
            
            case "qwen3:1.7b":
                model_path = "Qwen/Qwen3-1.7B"
            
            case "qwen3:4b":
                model_path = "Qwen/Qwen3-4B"
            
            # EMBEDDINGS_MODEL_TYPE
            case "FRIDA":
                model_path = "ai-forever/FRIDA"
            
            case "e5-large":
                model_path = "intfloat/multilingual-e5-large-instruct"
        
        return model_path


    def _init_embeddings(
        self, 
        embeddings_name: EMBEDDINGS_MODEL_TYPE,
        device: DEVICE_TYPE
    ) -> HuggingFaceEmbeddings:
        """Get an embeddings model"""
        embeddings_path = self._match_model_path(embeddings_name)
        embeddings = HuggingFaceEmbeddings(
            model_name = embeddings_path, 
            model_kwargs = {"device": device}
        )
        return embeddings
    

    def _init_toolkit(self):
        return MainToolkit()
    

    def _llm_with_tools(self, tools: Literal["all"] | list[TOOL_NAMES]):
        llm = self.llm.bind_tools(self.toolkit.get_tools(tools), tool_choice="auto")
        return llm
    

    def _parse_answer(
        self,
        answer: BaseMessage,
        llm_answer_parser: LLM_ANSWER_PARSER_TYPE
    ) -> BaseMessage | str | dict[str, str]:
        match llm_answer_parser:
            case  "none":
                pass

            case "json":
                parser = JsonOutputParser()
                try:
                    answer = parser.invoke(answer)
                except Exception as error:
                    logger.exception(error)
                    logger.info("Trying to parse with `ast` python module")
                    # Try parsing as Python literal if JSON fails
                    try:
                        answer = ast.literal_eval(answer.content)
                    except Exception as error:
                        logger.exception(error)
                        answer = ERROR_MESSAGE
            
            case "string":
                parser = StrOutputParser()
                answer = parser.invoke(answer)
            
        return answer


    def get_emdeddings(self) -> HuggingFaceEmbeddings:
        return self.embeddings
    

    def llm_answer(
        self, 
        messages: list[BaseMessage] | str | list[str],
        llm_answer_parser: LLM_ANSWER_PARSER_TYPE = "none",
        disable_thinking: bool = Settings.models.thinking_mode,
        tools: Literal["all"] | list[TOOL_NAMES] | None = None,
        config: RunnableConfig | None = None
    ) -> BaseMessage | str | dict[str, str]: # depends on an output parser
        # Message type
        if type(messages) is str:
            messages = [HumanMessage(messages)]
        
        if tools is None:
            llm = self.llm
        else:
            llm = self._llm_with_tools(tools)
        
        # Try to get the answer - if there are no errors appear
        try:
            # Loop for tool calling
            while True:
                # LLM call
                answer: AIMessage = llm.invoke(messages, config)
                logger.info("LLM's answer: %s", answer)

                # Escape of loop - if there is no tool calling
                if answer.tool_calls == []:
                    break
                
                # Otherwise - get the tool's answers and go to the second cycle
                tools_answers = []
                for tool_calling in answer.tool_calls:
                    tool_answer = self.toolkit.call_tool(tool_calling, config)
                    tools_answers.append(tool_answer)
                            
                messages.append(answer)
                messages.extend(tools_answers)


            # Remove thinking part of model's asnwer - if it's exists
            if disable_thinking:
                answer = AIMessage(cut_thinking_part_of_message(answer.content))
                logger.info("LLM answer after cutting the thinking part: %s", answer)

            # Output parser
            answer = self._parse_answer(answer, llm_answer_parser)
            logger.info("LLM's answer after parser: %s", answer)
        
        # If they are - show the error message
        except Exception as error:
            logger.exception(error)
            answer = ERROR_MESSAGE

        return answer