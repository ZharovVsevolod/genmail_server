from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes.ws_handle.ws_api import websocket_router
from .routes.files_interaction import file_router
from .routes.chats import chats_router
from .routes.plibrary import plibrary_router


app = FastAPI()
app.include_router(file_router)
app.include_router(chats_router)
app.include_router(plibrary_router)
app.include_router(websocket_router)

#-------------------------------------------
# React could connect to FastApi WebSocket 
# if some ports will be open along with CORS
# https://fastapi.tiangolo.com/tutorial/cors/#use-corsmiddleware
#-------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)
# ------------------------------------------


@app.get("/")
def read_root():
    """Check connection"""
    return {"message": "Wake up, Neo"}


@app.get("/health")
def check_health():
    """Health check"""
    return {"message": "healthy"}