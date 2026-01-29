from hashlib import md5
from data_info_handler.document_handler.models.data import Data
from data_info_handler.document_handler.models.files import File
from data_info_handler.document_handler.models.transcriptions import Transcription
from uuid import UUID
from datetime import datetime
from data_info_handler.document_handler.models.base import pg_handler
from sqlalchemy import select, func
from gm_services.schemas.document_handler import UploadResponse, TranscriptionStatusEnum


def add_data(file_data: bytes, content_type: str) -> bytes:
    md5sum = md5(file_data)
    with pg_handler.get_session() as session:
        existing_data = session.get(Data, md5sum.digest())
    if existing_data is not None:
        return md5sum.digest()

    data = Data(
        md5sum=md5sum.digest(),
        data=file_data,
        file_type=content_type,
        size_bytes=len(file_data),
    )
    with pg_handler.get_session() as session:
        session.add(data)

    return md5sum.digest()


def add_file(user_id: str, filename: str, md5sum: bytes) -> tuple[UUID, datetime]:
    file = File(user_id=user_id, name=filename, md5sum=md5sum, meta={})
    with pg_handler.get_session() as session:
        session.add(file)
        session.flush()
        session.refresh(file)
        return file.id, file.created_at


def does_user_id_own_file_id(user_id: str, file_id: UUID) -> bool:
    with pg_handler.get_session() as session:
        existing_file = session.get(File, file_id)
        return (
            existing_file.deleted_at is None and existing_file.user_id == user_id
            if existing_file
            else False
        )


def does_user_id_own_md5sum(user_id: str, md5sum: bytes) -> bool:
    with pg_handler.get_session() as session:
        stmt = select(File).where(File.user_id == user_id and File.md5sum == md5sum)
        existing_file = session.execute(stmt).scalar_one_or_none()
        return existing_file is not None and existing_file.deleted_at is None


def get_md5sum_by_id(file_id: UUID) -> bytes | None:
    with pg_handler.get_session() as session:
        existing_file = session.get(File, file_id)
        return (
            existing_file.md5sum
            if existing_file and existing_file.deleted_at is None
            else None
        )


def get_data_by_md5sum(md5sum: bytes) -> bytes | None:
    with pg_handler.get_session() as session:
        existing_data = session.get(Data, md5sum)
        return existing_data.data if existing_data else None


def get_upload_response_by_id(file_id: UUID) -> UploadResponse | None:
    with pg_handler.get_session() as session:
        existing_file = session.get(File, file_id)
        return (
            UploadResponse.model_validate(
                existing_file, from_attributes=True, extra="ignore"
            )
            if existing_file and existing_file.deleted_at is None
            else None
        )


def delete_file_id(file_id: UUID) -> bool:
    with pg_handler.get_session() as session:
        existing_file = session.get(File, file_id)
        if existing_file is None or existing_file.deleted_at is not None:
            return False
        existing_file.deleted_at = func.now()
    return True


def create_transcription_task(id: UUID, md5sum: bytes):
    with pg_handler.get_session() as session:
        t = Transcription(
            id=id, status=TranscriptionStatusEnum.IN_QUEUE.value, md5sum=md5sum
        )
        session.add(t)


def set_transcription_task_status(id: UUID, new_status: str) -> bool:
    with pg_handler.get_session() as session:
        existing_task = session.get(Transcription, id)
        if existing_task is None:
            return False
        existing_task.status = new_status
    return True


def get_transcription_task_status(id: UUID) -> str | None:
    with pg_handler.get_session() as session:
        existing_task = session.get(Transcription, id)
        return None if existing_task is None else existing_task.status


def get_transcription_content_type_by_md5sum(md5sum: bytes) -> str | None:
    with pg_handler.get_session() as session:
        existing_data = session.get(Data, md5sum)
        return existing_data.file_type if existing_data else None


def set_transcription_task_content(id: UUID, content: dict) -> bool:
    with pg_handler.get_session() as session:
        existing_task = session.get(Transcription, id)
        if existing_task is None:
            return False
        existing_task.content = content
        return True


def get_transcription_task_updated_at(id: UUID) -> datetime | None:
    with pg_handler.get_session() as session:
        existing_task = session.get(Transcription, id)
        return existing_task.updated_at if existing_task else None


def get_transcription_task_method(id: UUID) -> str | None:
    with pg_handler.get_session() as session:
        existing_task = session.get(Transcription, id)
        return existing_task.method if existing_task else None


def get_transcription_task_meta(id: UUID) -> dict:
    with pg_handler.get_session() as session:
        existing_task = session.get(Transcription, id)
        return existing_task.meta if existing_task else dict()


def get_transcription_task_content(id: UUID) -> dict | None:
    with pg_handler.get_session() as session:
        existing_task = session.get(Transcription, id)
        return existing_task.content if existing_task else None
