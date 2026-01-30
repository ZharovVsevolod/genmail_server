from langchain_core.messages import SystemMessage, HumanMessage

from gm_services.schemas.understanding import DocumentView
from gm_services.common import load_prompt
from gm_services.config import Settings

from gm_services.schemas.extraction import ExtractedDocument
from gm_services.neural.llm import LLModelShell
from typing import List, Literal

import logging
logger = logging.getLogger(__name__)


AVAILABLE_TASKS = Literal[
    "TextAnalyze"
]


class PromptRunner:
    """
    Universal runner for LLM. Depenends of task, load needed .md prompt from 
    prompt storage, parse additional information and user's phrase.
    """

    def __init__(
        self, 
        model: LLModelShell,
        prompt_storage: str = Settings.models.full_prompts_path
    ):
        self.model = model
        self.prompt_storage = prompt_storage


    def _get_prompt_from_task(self, task: AVAILABLE_TASKS) -> str:
        match task:
            case "TextAnalyze":
                prompt_path = self.prompt_storage + "text_analisys.md"
                system_prompt = load_prompt(prompt_path)
        
        return system_prompt
    

    def text_analize(
        self,
        system_prompt: str,
        contexts: List[ExtractedDocument]
    ) -> List[DocumentView]:
        required_keys = ["doc_type", "theme", "summary", "author", "number", "date"]
        default_values = {
            "doc_type": "inner",
            "theme": "unknown", 
            "summary": "No summary available",
            "author": "There is no author",
            "number": "There is no number",
            "date": "There is no date"
        }

        context_data = "\n\n".join([doc.to_str() for doc in contexts])

        messages = [SystemMessage(system_prompt), HumanMessage(context_data)]
        response = self.model.llm_answer(
            messages=messages,
            llm_answer_parser="json"
        )
        logger.info("Document summarization: %s", response)

        if not isinstance(response, dict):
            logger.warning("Response is not a dictionary, using default values: %s", response)
            response = default_values.copy()
        else:
            for key in required_keys:
                if key not in response or not response[key]:
                    logger.warning("Missing or empty key '%s', using default", key)
                    response[key] = default_values[key]
        
        try:
            return DocumentView(
                doc_type = response["doc_type"],
                text = context_data,
                theme = response["theme"],
                summary = response["summary"],
                author = response["author"],
                number = response["number"],
                date = response["date"],
                metadata = contexts[0].metadata,
            )
        except Exception as e:
            logger.exception("Error creating DocumentView: %s", e)
    

    def run(
        self,
        task: AVAILABLE_TASKS,
        document_context: List[ExtractedDocument] | None = None
    ) -> str | List[DocumentView]:
        """
        Run LLM with system prompt of current task

        Tasks
        -----
        - `TextAnalyze`: Get some information from given document
        (like date, number, author, main theme of text, etc.)
        
            
        Arguments
        ---------
        task: str
            What task to perfom
        
        document_context: List[ExtractedDocument] | None = None
            Parameter for `TextAnalyze`: text that LLM will search in

        
        Returns
        -------
        result: str | List[DocumentView]
            LLM's formatted answer. Answer's type depends on task
        """
        system_prompt = self._get_prompt_from_task(task)

        match task:
            case "TextAnalyze":
                result = self.text_analize(
                    system_prompt = system_prompt,
                    contexts = document_context
                )
        
        return result