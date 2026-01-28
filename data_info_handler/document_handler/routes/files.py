from fastapi import APIRouter, UploadFile, HTTPException
from gm_services.schemas.document_handler import UploadResponse
from data_info_handler.document_handler.models import dbutils

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload(user_id: str, file: UploadFile) -> UploadResponse:
    if not file.filename:
        raise HTTPException(400, "Filename must be specified")
    if not file.content_type:
        raise HTTPException(400, "Content-Type must be specified")

    file_data = await file.read()
    md5sum = dbutils.add_data(file_data, file.content_type)
    file_id, created_at = dbutils.add_file(user_id, file.filename, md5sum=md5sum)

    return UploadResponse(
        id=file_id,
        user_id=user_id,
        name=file.filename,
        md5sum=md5sum.hex(),
        metadata={},
        created_at=created_at,
        deleted_at=None,
    )
