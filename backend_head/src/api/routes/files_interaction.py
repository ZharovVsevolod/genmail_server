import os

from fastapi.responses import FileResponse
from fastapi import APIRouter, UploadFile, File
from fastapi import APIRouter

from gm_services.gm_services.config import Settings


file_router = APIRouter()


@file_router.get("/download")
async def download_file(filename: str) -> FileResponse:
    path = Settings.docs.full_mail_path + filename
    assert os.path.exists(path), "File not found!"

    return FileResponse(
        path = path, 
        filename = filename
    )


@file_router.post("/upload")
async def upload_files(files: list[UploadFile] = File(...)):
    saved_files = []
    for file in files:
        file_location = Settings.docs.full_mail_path + file.filename
        with open(file_location, "wb") as f:
            f.write(await file.read())
        saved_files.append(file.filename)

    return {"uploaded": saved_files}