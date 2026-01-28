from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import ForeignKey, DateTime
from data_info_handler.document_handler.models.base import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
from sqlalchemy import func


class File(Base):
    __tablename__ = "files"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    user_id: Mapped[str | None] = mapped_column(index=True)
    name: Mapped[str | None] = mapped_column(nullable=False)
    md5sum: Mapped[bytes | None] = mapped_column(ForeignKey("data.md5sum"), nullable=True)
    meta: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=False,
    )
