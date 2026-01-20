from langchain_core.messages.ai import AIMessageChunk


def chain_stream_parser(chunk):
    """Transform LLM stream events to parser-like ones."""
    match chunk["event"]:
        case "on_chat_model_start":
            return {
                **chunk,
                "event": "on_parser_start",
                "data": {"chunk": None},
            }

        case "on_chat_model_stream":
            ai_message = chunk["data"].get("chunk")
            if isinstance(ai_message, AIMessageChunk):
                text = ai_message.content or ""
                result = {
                    "event": "on_parser_stream",
                    "data": {"chunk": text},
                    "run_id": chunk.get("run_id"),
                    "metadata": chunk.get("metadata", {}),
                    "name": chunk.get("name"),
                    "tags": chunk.get("tags", []),
                    "parent_ids": chunk.get("parent_ids", []),
                }
                return result
    
    # Return unchanged event if not handled
    return chunk


def is_think_continue(data_chunk: str) -> bool:
    """Check if data chunk contains token that shows that thinking part is over
    
    Return *True* if thinking is continue and not over yet.\n
    Return *False* if thinking is over (end of thinking token was found)
    """
    if "</think>" in data_chunk:
        return False
    else:
        return True
