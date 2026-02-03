from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import ForeignKey, DateTime, Index
from data_info_handler.document_handler.models.base import Base
import uuid
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime
from sqlalchemy import func
from uuid import uuid4


class File(Base):
    __tablename__ = "files"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[str | None] = mapped_column(index=True)
    name: Mapped[str | None] = mapped_column(nullable=False)
    md5sum: Mapped[bytes | None] = mapped_column(
        ForeignKey("data.md5sum", ondelete="RESTRICT"),
        nullable=True,
    )
    meta: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    __table_args__ = (Index("user_id__md5sum", "user_id", "md5sum"),)
