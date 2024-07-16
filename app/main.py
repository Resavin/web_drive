import os

from config import settings
from db import engine
from fastapi import FastAPI, UploadFile
from fastapi.responses import FileResponse
from models import FileChanges, FilePublic
from services import FileService
from sqlmodel import SQLModel

SQLModel.metadata.create_all(engine)
app = FastAPI(debug=settings.app_debug)


# @app.post("/create-file/")
# def create_file(file: FileCreate):
#     """
#     DEBUG ROUTE FOR ADDING A RECORD TO DB WITHOUT UPLOADING THE FILE
#     """
#     return FileService.create_file(file)


@app.get("/files/")
def read_files():
    return FileService.read_files()


@app.get("/files/{file_id}", response_model=FilePublic)
def read_file(file_id: int):
    return FileService.read_file(file_id)


@app.post("/upload-file/")
async def upload_file(
    upload_file: UploadFile,
    name: str | None = None,
    path: str | None = None,
    comment: str | None = None,
):
    return await FileService.upload_file(upload_file, name, path, comment)


@app.delete("/delete-file/{file_id}")
def delete_file(file_id: int):
    return FileService.delete_file(file_id)


@app.get("/search-in-path/{subpath}")
def search_files(subpath: str):
    return FileService.search_files(subpath)


@app.get("/download-file/{file_id}", response_class=FileResponse)
def download_file(file_id: int):
    full_path = FileService.download_file(file_id)
    return FileResponse(
        path=full_path,
        filename=os.path.basename(full_path),
        media_type="application/octet-stream",
    )


@app.post("/change-file/{file_id}")
def change_file(file_id: int, file_changes: FileChanges):
    return FileService.change_file(file_id, file_changes)


@app.post("/sync")
def sync():
    return FileService.sync()
