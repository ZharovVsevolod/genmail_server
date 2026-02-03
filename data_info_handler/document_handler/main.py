import uvicorn
from data_info_handler.document_handler.app import app
from gm_services.config import Settings

if __name__ == "__main__":
    uvicorn.run(
        app = app, 
        host = Settings.api.document_handler.host, 
        port = Settings.api.document_handler.port
    )
