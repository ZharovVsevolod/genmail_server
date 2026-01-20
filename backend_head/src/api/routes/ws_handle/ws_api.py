import ast
from fastapi import APIRouter
from .ws_head import WSHead

from fastapi import WebSocket

import logging
logger = logging.getLogger(__name__)


websocket_router = APIRouter()

@websocket_router.websocket("/ws/chat/")
async def websocket_endpoint(websocket: WebSocket):
    # Handshake - make a connection
    await websocket.accept()
    logger.info("Websocket connection established")

    # Create main WebSocket control head
    ws_head = WSHead(websocket)

    # User's authentification
    while True:
        # Here is where frontend should send to backend user's id and pass
        logger.info("Waiting for frontend auth data...")
        # -------
        # Get data from the frontend
        data = await websocket.receive_text()
        # Transform raw json string to python dictionary
        data: dict[str, str] = ast.literal_eval(data)
        # Get the credentials
        if data.get("action") == "AUTH":
            user_id = data.get("user_id")
            user_password = data.get("user_password")

        logger.info("Have gotten auth data for %s", user_id)
        
        # Check if user's credentials is legit and link to this WSHead
        is_check_fine = await ws_head.register_user(user_id, user_password)

        if is_check_fine:
            logger.info("Everything is fine, login and pass matched")
            break

        logger.info("Login or pass didn't match")

    # Conversation loop
    while True:
        # Get data from the frontend
        data = await websocket.receive_text()
        # Transform raw json string to python dictionary
        data = ast.literal_eval(data)
        # Proceed this data
        await ws_head.proceed_recieved_data(data)