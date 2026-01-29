from hashlib import md5
from data_info_handler.document_handler.models.data import Data
from data_info_handler.document_handler.models.files import File
from uuid import UUID
from datetime import datetime
from data_info_handler.document_handler.models.base import pg_handler
from sqlalchemy import select


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
        return existing_file.user_id == user_id if existing_file else False


def does_user_id_own_md5sum(user_id: str, md5sum: bytes) -> bool:
    with pg_handler.get_session() as session:
        stmt = select(File).where(File.user_id == user_id and File.md5sum == md5sum)
        existing_file = session.execute(stmt).scalar_one_or_none()
        return existing_file is not None


def get_md5sum_by_id(file_id: UUID) -> bytes | None:
    with pg_handler.get_session() as session:
        existing_file = session.get(File, file_id)
        return existing_file.md5sum if existing_file else None


def get_data_by_md5sum(md5sum: bytes) -> bytes | None:
    with pg_handler.get_session() as session:
        existing_data = session.get(Data, md5sum)
        return existing_data.data if existing_data else None
