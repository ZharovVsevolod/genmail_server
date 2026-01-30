from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import ForeignKey, DateTime
from data_info_handler.document_handler.models.base import Base
import uuid
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from sqlalchemy import func
from uuid import uuid4


class Transcription(Base):
    __tablename__ = "transcriptions"
    id: Mapped[uuid.UUID] = mapped_column(
        nullable=False, primary_key=True, default=uuid4
    )
    status: Mapped[str]
    md5sum: Mapped[bytes] = mapped_column(
        ForeignKey("data.md5sum", ondelete="CASCADE"), index=True
    )
    method: Mapped[str | None]
    content: Mapped[dict] = mapped_column(JSONB, default="{}")
    meta: Mapped[dict] = mapped_column(JSONB, default="{}")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=False,
    )
