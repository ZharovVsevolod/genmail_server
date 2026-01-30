from fastapi import APIRouter, UploadFile, HTTPException, Response
from gm_services.schemas.document_handler import UploadResponse, FilterMetadataRequest
from data_info_handler.document_handler.models import dbutils
from logging import getLogger
from uuid import UUID
from typing import cast

logger = getLogger(__name__)

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_file(user_id: str, file: UploadFile) -> UploadResponse:
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
        meta={},
        created_at=created_at,
        deleted_at=None,
    )


@router.post("/data")
async def get_data(user_id: str, id: UUID | None = None, md5sum: str | None = None):
    if id is None and md5sum is None:
        raise HTTPException(400, "id or md5sum must be specified")

    if id:
        if not dbutils.does_user_id_own_file_id(user_id, id):
            raise HTTPException(403, "Forbidden")

        md5sum_from_db = dbutils.get_md5sum_by_id(id)
        if md5sum_from_db is None:
            logger.error(
                "User %s owns file %s, but can't retrieve it's md5sum", user_id, id
            )
            raise HTTPException(500, "Can't retrieve file with such id")

        data = dbutils.get_data_by_md5sum(md5sum_from_db)
        if not data:
            logger.error(
                "Can't find data for id=%s, md5sum=%s", id, md5sum_from_db.hex()
            )
            raise HTTPException(500, "Can't get data for this file")

        return Response(data, media_type="binary/octet-stream")

    md5sum = cast(str, md5sum)  # From here, only md5sum is specified
    try:
        md5_bytes = bytes.fromhex(md5sum)
    except ValueError as e:
        raise HTTPException(400, "Invalid md5 hex") from e

    if len(md5_bytes) != 16:
        raise HTTPException(400, "Invalid md5 hex")

    if not dbutils.does_user_id_own_md5sum(user_id, md5_bytes):
        raise HTTPException(403, "Forbidden")

    data = dbutils.get_data_by_md5sum(md5_bytes)
    if data is None:
        logger.error(
            "User %s owns file with md5sum %s, but can't retrieve it's data",
            user_id,
            md5sum,
        )
        raise HTTPException(500, "Can't retrieve file data")

    return Response(data, media_type="binary/octet-stream")


@router.post("/", response_model=UploadResponse)
async def get_file(user_id: str, id: UUID, body: FilterMetadataRequest | None = None):
    if not dbutils.does_user_id_own_file_id(user_id, id):
        raise HTTPException(403, "Forbidden")

    file_upload_response = dbutils.get_upload_response_by_id(id)
    if file_upload_response is None:
        logger.error("User %s owns file %s, but can't retrieve file", user_id, id)
        raise HTTPException(500, "Can't get file info")

    if body is not None:
        file_upload_response.meta = {
            key: file_upload_response.meta[key]
            for key in body.meta
            if key in file_upload_response.meta
        }

    return file_upload_response


@router.delete("/", status_code=200)
async def delete_file(user_id: str, id: UUID):
    if not dbutils.does_user_id_own_file_id(user_id, id):
        raise HTTPException(403, "Forbidden")

    dbutils.delete_file_id(id)
