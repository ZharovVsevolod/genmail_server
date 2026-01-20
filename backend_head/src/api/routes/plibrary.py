from fastapi import APIRouter
from ...head import HEAD

# Main prompt library recordings router
plibrary_router = APIRouter()

# --------------------------------
# Add new prompt to user's library
# --------------------------------
@plibrary_router.get("/plibrary/add")
async def add_prompt_to_library(user_id: str, prompt: str, name: str) -> dict[str, str]:
    prompt_id = HEAD.add_prompt_library(user_id, prompt, name)

    return {
        "message": f"Prompt {prompt_id} with name {name} was added",
        "prompt_id": prompt_id
    }


# ----------------------------------------
# Update existing prompt in user's library
# ----------------------------------------
@plibrary_router.get("/plibrary/update")
async def update_prompt_to_library(prompt_id: str, prompt: str, name: str) -> dict[str, str]:
    prompt_id = HEAD.update_prompt_library(prompt_id, prompt, name)

    return {"message": f"Prompt {prompt_id} was updated"}


# --------------------------
# Delete prompt from library
# --------------------------
@plibrary_router.get("/plibrary/delete")
async def delete_prompt_in_library(prompt_id: str) -> dict[str, str]:
    HEAD.delete_prompt_library(prompt_id)

    return {"message": f"Prompt {prompt_id} was deleted"}


# ------------------------------------
# List of all promps of user's library
# ------------------------------------
@plibrary_router.get("/plibrary/list")
async def get_prompt_library(user_id: str) -> dict[str, list[dict[str, str]]]:
    """
    Returns
    -------
    prompt_library: dict[str, list[dict[str, str]]]
        List of prompt library belongs to `user_id`.
        Dictionary has this structure:
        ```
        {
            "prompt_library": [
                {
                    "prompt_id": "id of recording",
                    "name": "name of this prompt",
                    "prompt": "text of this prompt"
                }
            ]
        }
        ```
    """
    prompt_library = HEAD.get_prompt_library(user_id)

    return {"prompt_library": prompt_library}