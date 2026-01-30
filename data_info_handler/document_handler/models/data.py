from sqlalchemy.orm import mapped_column, Mapped
from data_info_handler.document_handler.models.base import Base
from sqlalchemy.dialects.postgresql import BYTEA


class Data(Base):
    __tablename__ = "data"
    md5sum: Mapped[bytes] = mapped_column(BYTEA(16), primary_key=True)
    data: Mapped[bytes] = mapped_column(BYTEA)
    file_type: Mapped[str]
    size_bytes: Mapped[int]
