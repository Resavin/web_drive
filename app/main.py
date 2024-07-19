import os
import uuid

from app.config import settings
from app.db import engine
from fastapi import FastAPI, UploadFile, Response, HTTPException, Cookie
from fastapi.responses import FileResponse
from app.models import FileChanges, FilePublic, SessionData
from app.services import FileService
from sqlmodel import SQLModel, Session
from fastapi.middleware.cors import CORSMiddleware
from app.utils import auth_check

# SQLModel.metadata.drop_all(engine)
SQLModel.metadata.create_all(engine)
app = FastAPI(debug=settings.app_debug)


origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/create-session/", tags=["session"])
def create_session(response: Response):
    with Session(engine) as session:
        session_id = str(uuid.uuid4())
        session_data = SessionData(session_id=session_id)
        session_data = SessionData.model_validate(session_data)
        session.add(session_data)
        session.commit()
        session.refresh(session_data)
        response.set_cookie(key="session_id", value=session_data.session_id)
        return session_data


@app.delete("/delete-session/", tags=["session"])
def delete_session(session_id: str | None = Cookie(None)):
    with Session(engine) as session:
        session_data = session.get(SessionData, session_id)
        if not session_data:
            raise HTTPException(
                status_code=404, detail="No sessiondata with this session_id in db"
            )
        session.delete(session_data)
        session.commit()
        return {"message": "Sessiondata was successfully deleted."}


@app.get("/protected-route/", tags=["session"])
@auth_check
def protected_route():
    return "Session found"


# @app.post("/create-file/")
# def create_file(file: FileCreate):
#     """
#     Debug route for adding a record to db without uploading the file
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


@app.post("/rotate-image/{file_id}", tags=["rabbitmq"])
def rotate_image(file_id: int):
    return FileService.rotate_image(file_id)
