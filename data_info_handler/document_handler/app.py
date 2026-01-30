import logging
from fastapi import FastAPI
from data_info_handler.document_handler.routes import files, transcribe
from data_info_handler.document_handler.models.base import pg_handler
from contextlib import asynccontextmanager


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Creating tables")
    pg_handler.create_tables()
    logger.info("Created tables")
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(files.router, prefix="/files")
app.include_router(transcribe.router, prefix="/transcribe")
