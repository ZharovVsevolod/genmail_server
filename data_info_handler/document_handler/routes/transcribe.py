from fastapi import APIRouter, HTTPException
from gm_services.schemas.document_handler import (
    TranscriptionResponse,
    FilterMetadataRequest,
    TranscriptionStatusEnum,
    TransriptionStatusResponse,
)
from uuid import UUID, uuid4
from data_info_handler.document_handler.services.reader_tasks import reader_task
from data_info_handler.document_handler.models import dbutils
from logging import getLogger

logger = getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=TransriptionStatusResponse)
async def post_task(user_id: str, file_id: UUID):
    if not dbutils.does_user_id_own_file_id(user_id, file_id):
        raise HTTPException(403, "Forbidden")

    logger.info("Getting md5sum by file_id %s", file_id)
    md5sum = dbutils.get_md5sum_by_id(file_id)
    if md5sum is None:
        logger.warning("No md5sum for file %s", file_id)
        raise HTTPException(500, f"No data for file {file_id}")

    task_id = uuid4()
    dbutils.create_transcription_task(task_id, md5sum)
    reader_task.apply_async(args=[file_id, md5sum], task_id=str(task_id))

    logger.info("Created task %s", task_id)

    status = dbutils.get_transcription_task_status(task_id)
    if not status:
        logger.error("Can't retrieve status for task %s", task_id)
        raise HTTPException(500, f"No status for task {task_id}")

    updated_at = dbutils.get_transcription_task_updated_at(task_id)
    if not updated_at:
        logger.error("Can't retrieve updated_at for task %s", task_id)
        raise HTTPException(500, f"No updated_at for task {task_id}")

    return TransriptionStatusResponse(id=task_id, status=status, updated_at=updated_at)


@router.get("/status", response_model=TransriptionStatusResponse)
async def get_status(id: UUID):
    status = dbutils.get_transcription_task_status(id)
    if status is None:
        raise HTTPException(404, "No such task")

    updated_at = dbutils.get_transcription_task_updated_at(id)
    if updated_at is None:
        raise HTTPException(500, "Can't fetch updated_at")

    return TransriptionStatusResponse(id=id, status=status, updated_at=updated_at)


@router.post("/meta/", response_model=TranscriptionResponse)
async def get_meta(id: UUID, body: FilterMetadataRequest | None = None):
    status = dbutils.get_transcription_task_status(id)
    if status is None:
        raise HTTPException(404, "No such task")

    if status not in (
        TranscriptionStatusEnum.SUCCESS.value,
        TranscriptionStatusEnum.ERROR.value,
    ):
        raise HTTPException(400, "Not ready yet")

    method = dbutils.get_transcription_task_method(id)
    if method is None:
        raise HTTPException(500, "No method for task")

    meta = dbutils.get_transcription_task_meta(id)
    if body is None:
        meta = {key: meta[key] for key in meta if key in meta}
        return TranscriptionResponse(
            id=id, status=status, method=method, meta=meta, content={}
        )

    content = dbutils.get_transcription_task_content(id)
    if content is None:
        raise HTTPException(500, "Content is None")

    return TranscriptionResponse(
        id=id, status=status, method=method, meta=meta, content=content
    )
