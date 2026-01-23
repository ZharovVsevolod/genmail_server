from fastapi import APIRouter, UploadFile, HTTPException

from gm_services.united_schemes import ExtractedDocument, PARSING_METHODS

from data_info_handler.document_handler.services.reader import Reader
from pathlib import Path


router = APIRouter()


def generate_metadata(file: UploadFile) -> dict[str, str | int]:
    if not file.filename or not file.size:
        raise HTTPException(500, {"error": "No filename or size retrieved from file"})

    return {
        "source": __name__,
        "filename": file.filename,
        "file_size": file.size,
        "file_extension": Path(file.filename).suffix.lower(),
    }


@router.post("/", response_model=ExtractedDocument)
async def read(parsing_method: PARSING_METHODS, file: UploadFile):
    data = await file.read()
    page = Reader.read(data, parsing_method)
    return ExtractedDocument(
        pages=[] if page is None else [page],
        metadata=generate_metadata(file),
    )
