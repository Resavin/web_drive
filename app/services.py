# services.py

import os
import shutil
from datetime import datetime

from config import settings
from db import engine
from fastapi import HTTPException, UploadFile
from models import File, FileChanges, FileCreate
from sqlmodel import Session, select
from utils import (check_duplicate_path, get_full_path, normalize_path,
                   scan_directory)


class FileService:
    @staticmethod
    def create_file(file_data: FileCreate):
        file = File.model_validate(file_data)
        normalize_path(file)
        with Session(engine) as session:
            check_duplicate_path(session, file)
            session.add(file)
            session.commit()
            session.refresh(file)
            return file

    @staticmethod
    def read_files():
        with Session(engine) as session:
            files = session.exec(select(File)).all()
            return files

    @staticmethod
    def read_file(file_id: int):
        with Session(engine) as session:
            file = session.get(File, file_id)
            if not file:
                raise HTTPException(status_code=404, detail="file not found")
            return file

    @staticmethod
    async def upload_file(
        upload_file: UploadFile,
        name: str | None = None,
        path: str | None = None,
        comment: str | None = None,
    ):
        file_changes = FileChanges(name=name, path=path, comment=comment)
        # if file_changes:
        # file_changes = FileChanges.model_validate_json(file_changes)

        name, ext = os.path.splitext(upload_file.filename)

        file_data = {
            "id": None,
            "name": name,
            "extension": ext,
            "size": 0,
            "path": "/",
            "creation_date": datetime.utcnow().isoformat(),
            "modification_date": None,
            "comment": None,
        }

        if file_changes:
            update_data = {
                key: value
                for key, value in file_changes.model_dump().items()
                if value is not None
            }
            file_data.update(update_data)

        file = File(**file_data)
        normalize_path(file)
        with open(get_full_path(file), "wb") as f:
            contents = await upload_file.read()
            f.write(contents)

        file.size = len(contents)

        with Session(engine) as session:
            check_duplicate_path(session, file)
            session.add(file)
            session.commit()
            session.refresh(file)
            return file

    @staticmethod
    def delete_file(file_id: int):
        with Session(engine) as session:
            file = session.get(File, file_id)
            if not file:
                raise HTTPException(
                    status_code=404, detail="File record not found")
            session.delete(file)
            session.commit()

        try:
            os.remove(get_full_path(file))
            return {"message": "File was successfully deleted."}
        except FileNotFoundError:
            return {
                "message": "The record was deleted, but there was no such file in storage."
            }
        except Exception:
            return {
                "message": "The record was deleted, but something unexpected happened during file deletion in storage."
            }

    @staticmethod
    def search_files(subpath: str):
        with Session(engine) as session:
            statement = select(File).where(File.path.contains(subpath))
            results = session.exec(statement).all()
            return results

    @staticmethod
    def download_file(file_id: int):
        with Session(engine) as session:
            file = session.get(File, file_id)
            if not file:
                raise HTTPException(
                    status_code=404, detail="File record not found")

            full_path = get_full_path(file)
            if not os.path.exists(full_path):
                raise HTTPException(
                    status_code=404, detail="File not found on disk")

        return full_path

    @staticmethod
    def change_file(file_id: int, file_changes: FileChanges):
        if any([file_changes.name, file_changes.path, file_changes.comment]):
            with Session(engine) as session:
                file = session.get(File, file_id)
                if not file:
                    raise HTTPException(
                        status_code=404, detail="File record not found")

                old_full_path = get_full_path(file)
                if file_changes.name:
                    file.name = file_changes.name
                if file_changes.path:
                    file.path = file_changes.path
                    normalize_path(file_changes)
                    check_duplicate_path(session, file)

                shutil.move(old_full_path, get_full_path(file))

                if file_changes.comment:
                    file.comment = file_changes.comment

                file.modification_date = datetime.utcnow().isoformat()
                session.commit()
                session.refresh(file)

                return file

    @staticmethod
    def sync():
        scanned_files = scan_directory(settings.root_directory)
        print(scanned_files)
        with Session(engine) as session:
            db_files = session.exec(select(File)).all()
            db_files_dict = {get_full_path(file): file.id for file in db_files}

            file_paths_to_add = set()
            ids_to_delete = set(db_files_dict.values())

            for file_path in scanned_files:
                if file_path in db_files_dict.keys():
                    ids_to_delete.remove(db_files_dict[file_path])
                else:
                    file_paths_to_add.add(file_path)

            for path_with_name in file_paths_to_add:
                os.chdir(settings.root_directory)
                new_file_stat = os.stat(path_with_name.lstrip("/"))
                name, ext = os.path.splitext(os.path.basename(path_with_name))

                new_file = File(
                    # maybe it should be FileCreate, but cool that it works.
                    id=None,
                    name=name,
                    extension=ext,
                    size=new_file_stat.st_size,
                    path=os.path.dirname(path_with_name),
                    creation_date=datetime.fromtimestamp(
                        new_file_stat.st_ctime
                    ).isoformat(),
                    modification_date=datetime.fromtimestamp(
                        new_file_stat.st_mtime
                    ).isoformat(),
                    comment=None,
                )
                session.add(new_file)
                session.commit()
                session.refresh(new_file)

            for id in ids_to_delete:
                FileService.delete_file(id)

            return {"added_files": file_paths_to_add, "deleted_files": ids_to_delete}
