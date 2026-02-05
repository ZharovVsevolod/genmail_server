from dotenv import load_dotenv
load_dotenv()

import uvicorn

from src.api import app
from gm_services.config import Settings


if __name__ == "__main__":
    uvicorn.run(
        app = app, 
        host = Settings.api.retriever.host, 
        port = Settings.api.retriever.port
    )