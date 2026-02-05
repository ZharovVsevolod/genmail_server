from pydantic import BaseModel, Field

from langchain_core.tools import StructuredTool

from langchain_core.runnables import RunnableConfig
from typing import Literal, get_args


knowledge_name_typing = Literal["get_knowledge"]
knowledge_name = "".join(get_args(knowledge_name_typing))
knowledge_description = """Get a knowledge text from inner database with question-answering and knowledge bases. 
Useful when user asked any questions.
"""


class KnowledgeInput(BaseModel):
    query: str = Field(description = "Theme of answer, knowledge text you are looking for")


def get_knowledge(query: str, config: RunnableConfig) -> str:
    """Execute the user's query"""
    some_knowledge = config["configurable"]["retriever"].similarity_search(
        query = query, 
        return_format = "str",
        filter_type = "source",
        what_to_filter = "knowledge"
    )
    return some_knowledge



knowledge_info_tool = StructuredTool.from_function(
    func = get_knowledge,
    name = knowledge_name,
    description = knowledge_description,
    args_schema = KnowledgeInput,
    return_direct = True,
    response_format = "content"
)