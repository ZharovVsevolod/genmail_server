from typing import Literal


API_MESSAGE_TYPE = Literal[
    "SUMMARY", 
    "QUERY", 
    "FORMALIZE", 
    "CREATE",
    "LOAD_CHAT",
    "RATE"
]


SEND_EVENTS_TYPES = Literal[
    "on_parser_start", # Create a new message placeholder
    "on_parser_stream", # Add to a message text
    "document_extraction", # Started document extraction
    "document_summarization", # Started document summarization
    "summary", # Send full document summary
    "thinking_start", # Start a model thinking part
    "thinking_end", # End a model thinking part
    "on_generation_end", # End of generation - send an id of full message
    "download", # Send file for download
    "chat_creation", # Send new session_id for created chat,
    "auth_error" # On user's authentification error
]
EVENT_NEW_MESSAGE = "on_parser_start"
EVENT_ADD_TEXT_TO_MESSAGE = "on_parser_stream"
EVENT_STARTED_DOCUMENT_EXTRACTION = "document_extraction"
EVENT_STARTED_DOCUMENT_SUMMARIZATION = "document_summarization"
EVENT_SEND_SUMMARY = "summary"
EVENT_THINKING_START = "thinking_start"
EVENT_THINKING_END = "thinking_end"
EVENT_GENERATION_END = "on_generation_end"
EVENT_SEND_FILENAME_FOR_DOWNLOAD = "download"
EVENT_SEND_NEW_CHAT_ID = "chat_creation"
EVENT_SEND_PREVIOUS_CHAT_HISTORY = "chat_load"
EVENT_AUTH_SUCCESS =  "auth_success"
EVENT_AUTH_ERROR = "auth_error"

CUSTOM_EVENT_NAME = "on_custom_event"


RATING_TYPE = Literal["like", "dislike"]