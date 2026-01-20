from fastapi import APIRouter
from ...head import HEAD

# Main chat recordings router
chats_router = APIRouter()

# --------------------
# Add new chat of user
# --------------------
@chats_router.get("/chat/add")
async def add_chat_list(user_id: str, session_id: str, chat_name: str) -> dict[str, str]:
    HEAD.add_chat_id(user_id, session_id, chat_name)

    return {"message": f"Chat {session_id} with name {chat_name} was added"}


# -----------
# Delete chat
# -----------
@chats_router.get("/chat/delete")
async def delete_chat_list(session_id: str) -> dict:
    HEAD.delete_chat_id(session_id)

    return {"message": f"Chat {session_id} was deleted"}


# -----------------------
# Message history of chat
# -----------------------
@chats_router.get("/chat/history")
async def get_chat_history(session_id: str) -> dict[str, list[dict]]:
    """
    Returns
    -------
    history: dict[str, list[dict]]
        History has this structure:
        ```json
        {
            "history": [
                {
                    "id": string,
                    "sender": "ai or human",
                    "message": "message content",
                    "message_id": "what id message has in database",
                    "rating": "like, dislike or null";
                }
            ]
        }
        ```
    """
    # Get the full history
    messages = HEAD.get_messages(session_id, mode = "api")

    return {"history": messages}


# -------------------------
# List of all chats of user
# -------------------------
@chats_router.get("/chat/list")
async def get_chat_list(user_id: str) -> dict[str, list[dict]]:
    """
    Returns
    -------
    result: dict[str, list[dict]]
        Result looks like this:
        ```json
        {
            "chat_list": [
                {
                    "session_id": "name of session",
                    "name: "name of session"
                }
            ]
        }
        ```
    """
    chat_list = HEAD.get_chat_ids(user_id)

    return {"chat_list": chat_list}


# ------------------
# Update chat's name
# ------------------
@chats_router.get("/chat/update")
async def update_chat(session_id: str, session_name: str) -> dict[str, str]:
    HEAD.update_chat_id(session_id, session_name)
    return {"message": f"Chat's name of {session_id} was updated"}