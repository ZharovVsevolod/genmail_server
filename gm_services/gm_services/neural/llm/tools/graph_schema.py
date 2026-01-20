from langchain_core.tools import StructuredTool

from langchain_core.runnables import RunnableConfig
from typing import Literal, get_args


graph_schema_name_typing = Literal["get_graph_schema"]
graph_schema_name = "".join(get_args(graph_schema_name_typing))
graph_schema_description = """Get the full schema of graph database, which contains nodes, objects, relations, etc.
Everything you will need if you need to create a Cypher query to graph database.
You should call this tool if you need to generate Cypher query.
"""


def get_graph_schema(config: RunnableConfig) -> dict[str, str]:
    """Get a schema of the graph database"""
    answer = config["configurable"]["graphbase"].get_full_schema()
    return answer



get_graph_schema_tool = StructuredTool.from_function(
    func = get_graph_schema,
    name = graph_schema_name,
    description = graph_schema_description,
    return_direct = True,
    response_format = "content"
)