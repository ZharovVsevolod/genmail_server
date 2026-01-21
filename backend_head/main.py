from dotenv import load_dotenv
load_dotenv()

import uvicorn

from backend_head.src.api.api_main import app
from gm_services.gm_services.config import Settings


if __name__ == "__main__":
    uvicorn.run(
        app = app, 
        host = Settings.api.host, 
        port = Settings.api.port
    )