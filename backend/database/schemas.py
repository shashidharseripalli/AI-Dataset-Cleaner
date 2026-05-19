from typing import List, Optional

import pydantic
from pydantic import BaseModel


def _orm_config():
    try:
        pv = tuple(int(x) for x in pydantic.__version__.split(".")[:2])
    except Exception:
        return None
    if pv[0] >= 2:
        return {"from_attributes": True}
    return None


ORM_CONFIG = _orm_config()


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    username: Optional[str] = None


class DatasetBase(BaseModel):
    name: str
    description: Optional[str] = None
    owner_id: int


class DatasetCreate(DatasetBase):
    pass


class DatasetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    owner_id: Optional[int] = None


class Dataset(BaseModel):
    id: int
    name: str
    description: Optional[str]
    owner_id: int

    if ORM_CONFIG:
        model_config = ORM_CONFIG
    else:
        class Config:
            orm_mode = True


class FileUploadResponse(BaseModel):
    dataset_id: int
    filename: str
    content_type: Optional[str] = None
    size_bytes: int
    saved_path: str
    owner_id: int


class User(UserBase):
    id: int
    datasets: List[Dataset] = []

    if ORM_CONFIG:
        model_config = ORM_CONFIG
    else:
        class Config:
            orm_mode = True


if ORM_CONFIG:
    class UserList(pydantic.RootModel[List[User]]):
        root: List[User]
else:
    class UserList(BaseModel):
        __root__: List[User]
