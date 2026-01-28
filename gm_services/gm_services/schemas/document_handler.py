from pydantic import BaseModel, UUID4, AwareDatetime
from enum import Enum


class UploadResponse(BaseModel):
    id: UUID4
    user_id: str
    name: str
    md5sum: str  # hex
    metadata: dict

    created_at: AwareDatetime
    deleted_at: AwareDatetime | None


class FilterMetadataRequest(BaseModel):
    metadata: tuple[str]


class TranscriptionStatusEnum(Enum):
    IN_QUEUE = "IN_QUEUE"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"


class TransriptionStatusResponse(BaseModel):
    id: UUID4
    status: str
    updated_at: AwareDatetime


class TranscriptionResponse(BaseModel):
    id: UUID4
    status: str
    method: str
    content: dict
    metadata: dict
