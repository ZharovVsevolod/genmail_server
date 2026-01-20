from dotenv import load_dotenv
load_dotenv()

import uvicorn

from src.api.api_activation import app
from gm_services.gm_services.config import Settings


if __name__ == "__main__":
    uvicorn.run(
        app = app, 
        host = Settings.api.host, 
        port = Settings.api.port
    )