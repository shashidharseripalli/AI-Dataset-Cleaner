from sqlalchemy.orm import Session

from . import models, schemas


# User CRUD

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(username=user.username)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    if user_update.username is not None:
        db_user.username = user_update.username
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    db.delete(db_user)
    db.commit()
    return db_user


# Dataset CRUD

def get_dataset(db: Session, dataset_id: int):
    return db.query(models.Dataset).filter(models.Dataset.id == dataset_id).first()


def get_datasets(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Dataset).offset(skip).limit(limit).all()


def create_dataset(db: Session, dataset: schemas.DatasetCreate):
    db_user = get_user(db, dataset.owner_id)
    if not db_user:
        return None
    db_dataset = models.Dataset(
        name=dataset.name,
        description=dataset.description,
        owner_id=dataset.owner_id,
    )
    db.add(db_dataset)
    db.commit()
    db.refresh(db_dataset)
    return db_dataset


def update_dataset(db: Session, dataset_id: int, dataset_update: schemas.DatasetUpdate):
    db_dataset = get_dataset(db, dataset_id)
    if not db_dataset:
        return None
    if dataset_update.name is not None:
        db_dataset.name = dataset_update.name
    if dataset_update.description is not None:
        db_dataset.description = dataset_update.description
    if dataset_update.owner_id is not None:
        db_dataset.owner_id = dataset_update.owner_id
    db.commit()
    db.refresh(db_dataset)
    return db_dataset


def delete_dataset(db: Session, dataset_id: int):
    db_dataset = get_dataset(db, dataset_id)
    if not db_dataset:
        return None
    db.delete(db_dataset)
    db.commit()
    return db_dataset
