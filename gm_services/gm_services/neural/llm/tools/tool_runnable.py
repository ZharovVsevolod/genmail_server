from langchain_core.messages import BaseMessage, AIMessage, ToolMessage
from langchain_core.runnables import Runnable
from langchain_core.runnables.config import RunnableConfig
from langchain_core.callbacks.manager import adispatch_custom_event

from .tool_interface import MainToolkit

from langchain_openai import ChatOpenAI
from langchain_core.messages.ai import AIMessageChunk
from langchain_core.prompt_values import ChatPromptValue
from collections.abc import AsyncIterator
from langchain_core.runnables.schema import StreamEvent
from typing import Any, Optional

import logging
logger = logging.getLogger(__name__)


class ToolCallingRunnable(Runnable):
    """
    A Runnable for streaming llm's asnwer AND properly invoke tools if needed
    """

    def __init__(
        self, 
        llm: ChatOpenAI, 
        toolkit: MainToolkit,
        compatibility_stroutput: bool = False
    ) -> None:
        self.llm = llm
        self.toolkit = toolkit
        self.compatibility_stroutput = compatibility_stroutput


    async def _acall_tool(
        self,
        tool_call: dict[str, Any],
        config: RunnableConfig
    ) -> ToolMessage:
        """Call a tool using the MainToolkit, async-safe."""
        try:
            tool = self.toolkit.get_tool(tool_call["name"])

            # Find out if tool could be ivoke asynchonically
            if hasattr(tool, "ainvoke"):
                tool_result = await tool.ainvoke(tool_call["args"], config)
            # If it can't - we could just call it in usual form
            else:
                tool_result = tool.invoke(tool_call["args"], config)

            # Because we want ToolMessage as a return, we must be sure
            # that it is in this format
            if not isinstance(tool_result, ToolMessage):
                # If not - we will format output result intp ToolMessage
                tool_result = ToolMessage(
                    tool_call_id=tool_call["id"],
                    name=tool_call["name"],
                    content=str(tool_result),
                )

            logger.info("Tool result: %s", tool_result)
            return tool_result

        except Exception as e:
            content = f"Error executing tool '{tool_call.get('name')}': {e}"
            logger.exception(content)
            return ToolMessage(
                tool_call_id=tool_call.get("id", "unknown"),
                name=tool_call.get("name", "unknown"),
                content=content,
            )


    async def astream(
        self, 
        input: list[BaseMessage] | ChatPromptValue, 
        config: Optional[RunnableConfig] = None
    ) -> AsyncIterator[StreamEvent] | AIMessage:
        """
        Stream model tokens, detect tool calls, and handle them recursively.
        """
        # Initialize variable for final message
        # With this `ai_message` we will check if there is a need for tool call
        # Also it will contain the full message that will be need for history saving module
        ai_message: Optional[AIMessage] = None

        # Stream LLM tokens
        async for event in self.llm.astream_events(input, config=config):
            match event["event"]:
                case "on_chat_model_start":
                    continue
                
                # Send just a text for StrOutputParser
                case "on_chat_model_stream":
                    if self.compatibility_stroutput:
                        yield event["data"]["chunk"]
                    else:
                        yield event
                
                # Capture a final message with full context from the last event
                case "on_chat_model_end":
                    ai_message = event["data"]["output"]
                
                # Otherwise - nothing, just go on
                case _:
                    continue

        logger.info("AI message after stream before tool calling: %s", ai_message)

        # If there are tool calls - execute it
        if ai_message.tool_calls:
            tool_messages: list[ToolMessage] = []

            for tool_call in ai_message.tool_calls:
                logger.info("Executing tool: %s, args: %s", tool_call['name'], tool_call['args'])

                # Send a runnable message that tool is calling now
                if not self.compatibility_stroutput:
                    await adispatch_custom_event(
                        name = "tool_call_start",
                        data = {"name": tool_call["name"]}
                    )

                tool_msg = await self._acall_tool(tool_call, config)
                tool_messages.append(tool_msg)

                # Send a message that tool work was done
                if not self.compatibility_stroutput:
                    await adispatch_custom_event(
                        name = "tool_call_end",
                        data = {"name": tool_call["name"]}
                    )

            # Feed results back into the LLM (recurse)
            if type(input) is ChatPromptValue:
                next_input = input.to_messages()
            else:
                next_input = input


            next_input.append(ai_message)
            next_input.extend(tool_messages)
            ai_message = None

            async for sub_event in self.astream(next_input, config=config):
                yield sub_event
        
        # Return the final message for a history saving
        if ai_message is not None: # If it is None - then it's not final message
            # Unwrap nested event dict if present
            if (
                isinstance(ai_message, dict) and 
                "data" in ai_message and 
                "output" in ai_message["data"]
            ):
                ai_message = ai_message["data"]["output"]

            # If it’s a chunk, convert to AIMessage
            if isinstance(ai_message, AIMessageChunk):
                ai_message = AIMessage(ai_message.content)
            else:
                pass
            
            # If compatibility layer - save message
            if self.compatibility_stroutput:
                # Save this final message for further return to history saving block
                self._final_ai_message = ai_message
                logger.info("Final SELF AI message: %s", self._final_ai_message)
            
            # else - just yield it
            else:
                yield ai_message


    async def ainvoke(self, input, config=None):
        """Async ainvoke for self.astream call in loop
        
        Also handles the full final message for history saving
        """
        # Stream content generation
        async for chunk in self.astream(input, config=config):
            pass
        
        # If compatibility layer - return final result
        if not self.compatibility_stroutput:
            final_ai_message = getattr(self, "_last_ai_message", None)
            logger.info("Final AI message: %s", final_ai_message)
            return final_ai_message


    def invoke(
        self, 
        input: list[BaseMessage], 
        config: Optional[RunnableConfig] = None
    ):
        """Sync wrapper for compatibility."""
        import asyncio
        return asyncio.run(self.ainvoke(input, config))
