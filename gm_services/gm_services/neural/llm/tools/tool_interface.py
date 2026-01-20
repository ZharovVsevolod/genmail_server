from langchain_core.messages import ToolMessage

from .graph_search import (
    graph_search_tool, 
    graph_search_name, 
    graph_search_name_typing
)
from .reference import (
    reference_info_tool,
    reference_name,
    reference_name_typing
)
from .knowledge_retrieve import (
    knowledge_info_tool,
    knowledge_name,
    knowledge_name_typing
)

from langchain_core.runnables import RunnableConfig
from langchain_core.messages.tool import ToolCall
from langchain_core.tools import StructuredTool
from typing import Literal

import logging
logger = logging.getLogger(__name__)


TOOL_NAMES = Literal[
    graph_search_name_typing,
    reference_name_typing,
    knowledge_name_typing
]


class MainToolkit:
    def __init__(self):
        self.tools = {
            graph_search_name: graph_search_tool,
            reference_name: reference_info_tool,
            knowledge_name: knowledge_info_tool
        }
    

    def get_tool(self, tool_name: str) -> StructuredTool:
        return self.tools[tool_name]
    

    def call_tool(
        self, 
        tool_call: ToolCall,
        config: RunnableConfig
    ) -> ToolMessage:
        # Get the actual tool answer
        logger.info("Invoke tool: %s, args: %s", tool_call['name'], tool_call['args'])
        tool_result = self.get_tool(tool_call["name"]).invoke(tool_call["args"], config)
        logger.info("Tool result: %s", tool_result)
        
        # Convert tool answer to right type
        if not isinstance(tool_result, ToolMessage):
            tool_result = ToolMessage(
                tool_call_id = tool_call["id"],
                name = tool_call["name"],
                content = str(tool_result),
            )
        
        return tool_result


    def get_tools(
        self, 
        which: Literal["all"] | list[TOOL_NAMES] = "all"
    ) -> list[StructuredTool]:
        if which == "all":
            tools = [self.tools[key] for key in self.tools.keys()]
        
        else:
            tools = []
            for tool_name in which:
                tools.append(self.get_tool(tool_name))
        
        return tools

