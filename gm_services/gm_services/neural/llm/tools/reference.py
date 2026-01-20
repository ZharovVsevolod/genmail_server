from pydantic import BaseModel, Field

from langchain_core.tools import StructuredTool

from langchain_core.runnables import RunnableConfig
from typing import Literal, get_args


reference_name_typing = Literal["get_reference"]
reference_name = "".join(get_args(reference_name_typing))
reference_description = """Get a reference text for generation.
Useful when a user asked for text generation, and you need a reference for more rich context view.
"""


class ReferenceInput(BaseModel):
    query: str = Field(description = "Theme of answer, reference text you are looking for")


def get_reference(query: str, config: RunnableConfig) -> str:
    """Execute the user's query"""
    some_reference = config["configurable"]["vectorbase"].similarity_search(
        query = query, 
        return_format = "str",
        filter_type = "source",
        what_to_filter = "reference"
    )
    return some_reference



reference_info_tool = StructuredTool.from_function(
    func = get_reference,
    name = reference_name,
    description = reference_description,
    args_schema = ReferenceInput,
    return_direct = True,
    response_format = "content"
)