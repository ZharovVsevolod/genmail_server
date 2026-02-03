import os

from fastapi.responses import FileResponse
from fastapi import APIRouter, UploadFile, File
from fastapi import APIRouter

from ...head import HEAD
from gm_services.config import Settings, DOCUMENT_SESSION_ID_PLACEHOLDER

from typing import TypedDict


file_router = APIRouter()


@file_router.get("/download")
async def download_file(filename: str) -> FileResponse:
    path = Settings.docs.full_mail_path + filename
    assert os.path.exists(path), "File not found!"

    return FileResponse(
        path = path, 
        filename = filename
    )


class UPLOAD_FILES_RETURN(TypedDict):
    uploaded: list[str]

@file_router.post("/upload")
async def upload_files(
    user_id: str,
    files: list[UploadFile] = File(...)
) -> UPLOAD_FILES_RETURN:
    await HEAD.files_upload(
        files = files, 
        user_id = user_id, 
        session_id = DOCUMENT_SESSION_ID_PLACEHOLDER
    )

    saved_files = [file.filename for file in files]
    return {"uploaded": saved_files}