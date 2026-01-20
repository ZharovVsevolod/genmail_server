from langchain_core.messages import SystemMessage, HumanMessage

from .schemas_mail import DocumentView
from ..common import load_prompt
from ..config import Settings

from .schemas_mail import ExtractedDocument
from ..neural.model import MLModelShell
from typing import List

import logging
logger = logging.getLogger(__name__)


class PromptRunner:
    """
    Универсальный раннер: грузит .md-промпт, подставляет поля и текст пользователя,
    вызывает shell.llm_answer, возвращает dict с JSON-результатом.
    """

    def __init__(
        self, 
        model: MLModelShell, 
        task: str = "text_analisys.md"
    ):
        self.model = model
        prompt_path = Settings.models.full_prompts_path + task
        self.system_prompt = load_prompt(prompt_path)


    def run(self,
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

        messages = [SystemMessage(self.system_prompt), HumanMessage(context_data)]
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