import os
import shutil

import pytest
from config import settings
from db import engine
from fastapi.testclient import TestClient
from httpx import AsyncClient
from main import app
from models import File, FileCreate
from services import FileService
from sqlmodel import Session, SQLModel
from utils import get_full_path

client = TestClient(app)


# Set up the database for testing
@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)
    # clear storage
    shutil.rmtree(settings.root_directory)
    os.makedirs(settings.root_directory)


@pytest.fixture(name="client")
def client_fixture():
    return TestClient(app)


@pytest.fixture(name="async_client")
async def async_client_fixture():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


def create_and_write_file(file_data: FileCreate) -> File:
    new_file = FileService.create_file(file_data)
    with open(get_full_path(new_file), "w") as f:
        f.write("This is a test file content.")
    return new_file


def test_create_file(client: TestClient, session: Session):
    file_data = {
        "name": "testfile",
        "extension": ".txt",
        "size": 123,
        "path": "/",
        "creation_date": "2023-07-01T00:00:00",
        "modification_date": None,
        "comment": "A test file",
    }
    response = client.post("/create-file/", json=file_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "testfile"
    assert data["extension"] == ".txt"


def test_read_files(client: TestClient, session: Session):
    response = client.get("/files/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_read_file(client: TestClient, session: Session):
    file_data = FileCreate(
        name="testfile2",
        extension=".log",
        size=123,
        path="/",
        creation_date="2023-07-01T00:00:00",
        modification_date=None,
        comment="Another test file",
    )
    new_file = FileService.create_file(file_data)
    response = client.get(f"/files/{new_file.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "testfile2"


def test_upload_file(client: TestClient, session: Session):
    file_path = "test_upload.txt"
    with open(file_path, "w") as f:
        pass
    with open(file_path, "rb") as f:
        response = client.post(
            "/upload-file/?file_changes=%7B%22comment%22%3A%20%22uploaded%20file%22%2C%20%22name%22%3A%20%22tested%22%2C%20%22path%22%3A%20%22super%2Fpath%22%7D",
            files={"upload_file": (file_path, f, "text/plain")},
        )
    os.remove(file_path)

    assert response.status_code == 200
    data = response.json()
    file = File.model_validate(data)
    assert data["comment"] == "uploaded file"
    assert data["name"] == "tested"
    assert data["path"] == "/super/path"
    assert os.path.exists(get_full_path(file))


def test_delete_file(client: TestClient, session: Session):
    file_data = FileCreate(
        name="todelete",
        extension=".tmp",
        size=123,
        path="/",
        creation_date="2023-07-01T00:00:00",
        modification_date=None,
        comment="File to delete",
    )
    new_file = create_and_write_file(file_data)
    response = client.delete(f"/delete-file/{new_file.id}")
    assert response.status_code == 200
    assert response.json()["message"] == "File was successfully deleted."


def test_search_files(client: TestClient, session: Session):
    file_data = FileCreate(
        name="searchfile",
        extension=".log",
        size=123,
        path="/search/path",
        creation_date="2023-07-01T00:00:00",
        modification_date=None,
        comment="File to search",
    )
    FileService.create_file(file_data)
    response = client.get("/search-in-path/search")
    assert response.status_code == 200
    data = response.json()
    file = data[0]
    assert file["name"] == "searchfile"


def test_download_file(client: TestClient, session: Session):
    file_data = FileCreate(
        name="downloadme",
        extension=".log",
        size=123,
        path="/strangefolder",
        creation_date="2023-07-01T00:00:00",
        modification_date=None,
        comment="File to download",
    )
    new_file = create_and_write_file(file_data)
    response = client.get(f"/download-file/{new_file.id}")
    assert response.status_code == 200
    content_disposition = response.headers.get("content-disposition")
    assert content_disposition is not None
    assert (
        f'attachment; filename="{new_file.name + new_file.extension}"'
        in content_disposition
    )
    downloaded_file_content = response.content.decode("utf-8")
    assert downloaded_file_content == "This is a test file content."


def test_change_file(client: TestClient, session: Session):
    file_data = FileCreate(
        name="tochange",
        extension=".log",
        size=123,
        path="/new/path",
        creation_date="2023-07-01T00:00:00",
        modification_date=None,
        comment="File to change",
    )
    new_file = create_and_write_file(file_data)
    file_changes = {"name": "changedname", "comment": "Updated comment"}
    response = client.post(f"/change-file/{new_file.id}", json=file_changes)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "changedname"
    assert data["comment"] == "Updated comment"
    new_file = File.model_validate(data)
    assert os.path.exists(get_full_path(new_file))


def test_empty_sync(client: TestClient, session: Session):
    response = client.post("/sync")
    assert response.status_code == 200
    data = response.json()
    assert "added_files" in data
    assert "deleted_files" in data


def test_sync(client: TestClient, session: Session):
    file_data = FileCreate(
        name="to_delete_by_sync",
        extension=".log",
        size=123,
        path="/new/path",
        creation_date="2023-07-01T00:00:00",
        modification_date=None,
        comment="File to change",
    )
    file = FileService.create_file(file_data)
    filename = "to_add_by_sync.txt"
    with open(os.path.join(settings.root_directory, filename), "w") as f:
        f.write("TEEEEEEEEEEEEEEEEEEEEEEEEEee")
    if os.path.exists(os.path.join(settings.root_directory, "to_add_by_sync.txt")):
        response = client.post("/sync")
        assert response.status_code == 200
        data = response.json()
        assert filename in data["added_files"][0]
        assert file.id in data["deleted_files"]
