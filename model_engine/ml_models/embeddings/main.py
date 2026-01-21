import uvicorn

from src.api import app
from gm_services.gm_services.config import Settings


if __name__ == "__main__":
    uvicorn.run(
        app = app, 
        host = ..., 
        port = ...
    )