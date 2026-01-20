from pydantic import BaseModel, Field

from langchain_core.tools import StructuredTool

from langchain_core.runnables import RunnableConfig
from typing import Literal, get_args


graph_search_name_typing = Literal["graph_search"]
graph_search_name = "".join(get_args(graph_search_name_typing))
graph_search_description = """Execute the user's query for getting information from Neo4j database. 
Use it when user is asking you for find some information about people, organizations, positions, projects.
"""


class GraphSearchInput(BaseModel):
    query: str = Field(description = "The query in Russian for Neo4j graph database execution")


def graph_search(query: str, config: RunnableConfig) -> str | Literal["Invalid Cypher syntax"]:
    """Execute the user's query"""
    answer = config["configurable"]["graphbase"].llm_find_in_graph(query)
    return answer



graph_search_tool = StructuredTool.from_function(
    func = graph_search,
    name = graph_search_name,
    description = graph_search_description,
    args_schema = GraphSearchInput,
    return_direct = True,
    response_format = "content"
)