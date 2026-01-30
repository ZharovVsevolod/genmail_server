from pydantic import BaseModel, UUID4, AwareDatetime, field_validator, ValidationError
from enum import Enum


class UploadResponse(BaseModel):
    id: UUID4
    user_id: str
    name: str
    md5sum: str  # hex
    meta: dict

    created_at: AwareDatetime
    deleted_at: AwareDatetime | None

    @field_validator("md5sum", mode="before")
    @classmethod
    def serialize_categories(cls, md5sum):
        match md5sum:
            case bytes():
                return md5sum.hex()
            case str():
                return md5sum
            case _:
                raise ValidationError(f"Can't convert {type(md5sum)} to hex")


class FilterMetadataRequest(BaseModel):
    meta: tuple[str]


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
    meta: dict
