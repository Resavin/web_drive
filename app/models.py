from datetime import datetime
from sqlmodel import Field, SQLModel


class FileBase(SQLModel):
    name: str = Field(nullable=False)
    extension: str = Field(nullable=False)
    size: int = Field(nullable=False)
    path: str = Field(nullable=False)
    creation_date: datetime = Field(nullable=False)
    modification_date: datetime | None = Field(default=None)
    comment: str | None = Field(default=None)


class File(FileBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class FileCreate(FileBase):
    pass


class FilePublic(FileBase):
    id: int

class FileChanges(SQLModel):
    name: str | None = Field(default=None)
    path: str | None = Field(default=None)
    comment: str | None = Field(default=None)