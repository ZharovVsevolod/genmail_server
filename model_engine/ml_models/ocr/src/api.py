import logging

from fastapi import FastAPI
from pydantic import BaseModel

from .ocr import OCRHandler

logger = logging.getLogger(__name__)

logger.info("Initializing OCR handler")
OCR_MODEL = OCRHandler()
logger.info("OCR handler was initialized")

app = FastAPI()


class OCRRequest(BaseModel):
    input_path: str
    prompt: str | None = None
    recursive: bool = False


@app.post("/ocr")
async def ocr_path(request: OCRRequest) -> dict[str, list[dict[str, str | None]]]:
    """
    OCR files via vLLM OpenAI-compatible API

    Arguments
    ---------
    input_path: str
        Path to the file or folder on server
    
    prompt: str | None
        Optional prompt for model (uses default if omitted)

    recursive: bool
        Read subfolders when input_path is a directory
    
    Returns
    -------
    result: dict[str, list[dict[str, str | None]]]
        {"results": list_of_file_results}
    """
    results = OCR_MODEL.process_path(
        input_path = request.input_path,
        prompt = request.prompt,
        recursive = request.recursive
    )
    return {"results": results}


@app.get("/")
def read_root():
    """Check connection"""
    return {"message": "Wake up, Samurai!"}


@app.get("/health")
def check_health():
    """Health check"""
    return {"message": "healthy"}