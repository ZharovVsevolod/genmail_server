import logging
from fastapi import FastAPI
from data_info_handler.document_handler.routes import reader
from data_info_handler.document_handler.models import data, files, transcriptions
from data_info_handler.document_handler.models.base import Base, engine
from contextlib import asynccontextmanager


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Creating tables")
    Base.metadata.create_all(engine)
    logger.info("Created tables")
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(reader.router, prefix="/reader")
