import uvicorn
from data_info_handler.document_handler.app import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
