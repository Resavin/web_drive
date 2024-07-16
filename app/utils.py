import os

from config import settings
from fastapi import HTTPException
from models import File
from sqlmodel import Session, select


def get_full_path(file: File):
    return os.path.join(
        settings.root_directory, file.path.lstrip("/"), file.name + file.extension
    )


def check_duplicate_path(session: Session, file: File):
    statement = select(File).where(
        File.path == file.path, File.name == file.name, File.extension == file.extension
    )
    existing_file = session.exec(statement).first()
    if existing_file:
        raise HTTPException(
            status_code=400,
            detail="File record in db with the same path, name, and extension already exists",
        )


def normalize_path(file: File):
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
