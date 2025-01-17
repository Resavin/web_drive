import os

from app.config import settings
from fastapi import HTTPException, Cookie
from app.models import File, FileChanges, SessionData
from sqlmodel import Session, select
from app.logger import logger
from app.db import engine


def get_full_path(file: File):
    return os.path.join(
        settings.root_directory, file.path.lstrip("/"), file.name + file.extension
    )


def check_duplicate_path(
    session: Session, file: File, file_changes: FileChanges | None = None
):
    path = file.path
    name = file.name
    if file_changes:
        logger.debug("check dup " + file_changes.path)
        if file_changes.path:
            path = file_changes.path
        if file_changes.name:
            name = file_changes.name
    statement = select(File).where(
        File.path == path, File.name == name, File.extension == file.extension
    )
    existing_file = session.exec(statement).first()

    if existing_file or os.path.exists(
        os.path.join(settings.root_directory, path, name + file.extension)
    ):
        raise HTTPException(
            status_code=400,
            detail="File record in db with the same path, name, and extension already exists",
        )


def normalize_path(file: File | FileChanges):
    splits = file.path.split("/")
    if ".." in splits or "." in splits or "~" in splits:
        raise HTTPException(
            status_code=400, detail="Path shouldn't use '.', '..' or '~' "
        )

    if file.path != "/":
        try:
            os.makedirs(
                os.path.join(settings.root_directory, file.path.lstrip("/")),
                exist_ok=True,
            )
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid path")

    if file.path.endswith("/"):
        file.path = file.path.rstrip("/")
    if not file.path.startswith("/"):
        file.path = "/" + file.path


def scan_directory(directory):
    file_path_set = set()
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_path_set.add("/" + file_path.removeprefix(directory + "/"))
    return file_path_set


def auth_check(func):
    def wrapper(session_id: str | None = Cookie(default=None)):
        if not session_id:
            raise HTTPException(status_code=400, detail="No session_id in cookies")
        logger.debug("session_id: " + str(session_id))

        with Session(engine) as session:
            # statement = select(SessionData).where(SessionData.session_id == session_id)
            # session_data = session.exec(statement).first()
            session_data = session.get(SessionData, session_id)
            if not session_data:
                raise HTTPException(
                    status_code=400, detail="No sessiondata with this session_id in db"
                )
        return func()

    return wrapper
