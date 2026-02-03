import httpx

import gm_services.schemas.document_handler as schemas
from gm_services.config import Settings

from uuid import UUID


class DocumentHandlerClient:
    def __init__(self) -> None:
        self.client = httpx.AsyncClient(
            base_url = Settings.services.document_handler.base_url
        )

    async def files_upload(
        self, user_id: str, file_data: bytes, content_type: str, filename: str
    ) -> schemas.UploadResponse:
        r = await self.client.post(
            "/files/upload/",
            params={"user_id": user_id},
            files={"file": (filename, file_data, content_type)},
        )
        r.raise_for_status()
        return schemas.UploadResponse.model_validate(r.json())

    async def get_data(
        self, user_id: str, id: UUID | None, md5sum: str | None
    ) -> bytes:
        if id is None and md5sum is None:
            raise ValueError("id or md5sum must be specified")

        params = {"id": str(id)} if id else {"md5sum": str(md5sum)}
        params["user_id"] = user_id
        r = await self.client.get("/files/data/", params=params)
        r.raise_for_status()
        return await r.aread()

    async def get_file(
        self, user_id: str, id: UUID, meta_fields: tuple[str] | None
    ) -> schemas.UploadResponse:
        params = {"user_id": user_id, "id": str(id)}
        body = schemas.FilterMetadataRequest(meta=meta_fields) if meta_fields else None
        if body:
            r = await self.client.post("/files/", params=params, json=body.model_dump())
        else:
            r = await self.client.post("/files/", params=params)
        r.raise_for_status()
        return schemas.UploadResponse.model_validate(r.json())

    async def delete_file(self, user_id: str, id: UUID):
        params = {"user_id": user_id, "id": str(id)}
        r = await self.client.delete("/", params=params)
        r.raise_for_status()

    async def create_transcribe_task(
        self, user_id: str, file_id: UUID
    ) -> schemas.TransriptionStatusResponse:
        params = {"user_id": user_id, "file_id": str(file_id)}
        r = await self.client.post("/transcribe/", params=params)
        r.raise_for_status()
        return schemas.TransriptionStatusResponse.model_validate(r.json())

    async def get_status(self, id: UUID) -> schemas.TransriptionStatusResponse:
        params = {"id": str(id)}
        r = await self.client.get("/transcribe/status/", params=params)
        r.raise_for_status()
        return schemas.TransriptionStatusResponse.model_validate(r.json())

    async def get_meta(
        self, id: UUID, meta_fields: tuple[str] | None
    ) -> schemas.TranscriptionResponse:
        params = {"id": str(id)}
        body = schemas.FilterMetadataRequest(meta=meta_fields) if meta_fields else None
        if body:
            r = await self.client.post(
                "/transcribe/meta/", params=params, json=body.model_dump()
            )
        else:
            r = await self.client.post("/transcribe/meta/", params=params)
        r.raise_for_status()
        return schemas.TranscriptionResponse.model_validate(r.json())
