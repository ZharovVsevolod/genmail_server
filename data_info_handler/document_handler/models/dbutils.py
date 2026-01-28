from sqlalchemy.orm import Session
from hashlib import md5
from data_info_handler.document_handler.models.data import Data
from data_info_handler.document_handler.models.files import File
from uuid import UUID
from datetime import datetime
from data_info_handler.document_handler.models.base import pg_handler


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


def add_file(user_id: str, filename: str, md5sum: str) -> tuple[UUID, datetime]:
    file = File(user_id=user_id, name=filename, md5sum=md5sum, meta={})
    with pg_handler.get_session() as session:
        session.add(file)
        session.flush()
        session.refresh(file)
        return file.id, file.created_at
