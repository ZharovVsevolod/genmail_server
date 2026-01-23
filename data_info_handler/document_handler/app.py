import logging
from fastapi import FastAPI
from data_info_handler.document_handler.routes import reader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(reader.router, prefix="/reader")
