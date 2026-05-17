from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.database import crud, db, models, schemas

app = FastAPI()


@app.on_event("startup")
def on_startup():
    try:
        models.Base.metadata.create_all(bind=db.engine)
    except Exception as e:
        import logging

        logging.warning(f"Could not create tables on startup: {e}")


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(db.get_db)):
    existing = crud.get_user_by_username(db, username=user.username)
    if existing:
        raise HTTPException(status_code=400, detail="username already exists")
    return crud.create_user(db, user)


@app.get("/users/", response_model=List[schemas.User])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(db.get_db)):
    return crud.get_users(db, skip=skip, limit=limit)


@app.get("/users/{user_id}", response_model=schemas.User)
def get_user(user_id: int, db: Session = Depends(db.get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(db.get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if user_update.username:
        existing = crud.get_user_by_username(db, username=user_update.username)
        if existing and existing.id != user_id:
            raise HTTPException(status_code=400, detail="username already exists")
    updated = crud.update_user(db, user_id=user_id, user_update=user_update)
    return updated


@app.delete("/users/{user_id}", response_model=schemas.User)
def delete_user(user_id: int, db: Session = Depends(db.get_db)):
    db_user = crud.delete_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/datasets/", response_model=schemas.Dataset)
def create_dataset(dataset: schemas.DatasetCreate, db: Session = Depends(db.get_db)):
    owner = crud.get_user(db, user_id=dataset.owner_id)
    if not owner:
        raise HTTPException(status_code=404, detail="Owner user not found")
    return crud.create_dataset(db, dataset=dataset)


@app.get("/datasets/", response_model=List[schemas.Dataset])
def list_datasets(skip: int = 0, limit: int = 100, db: Session = Depends(db.get_db)):
    return crud.get_datasets(db, skip=skip, limit=limit)


@app.get("/datasets/{dataset_id}", response_model=schemas.Dataset)
def get_dataset(dataset_id: int, db: Session = Depends(db.get_db)):
    db_dataset = crud.get_dataset(db, dataset_id=dataset_id)
    if not db_dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return db_dataset


@app.put("/datasets/{dataset_id}", response_model=schemas.Dataset)
def update_dataset(dataset_id: int, dataset_update: schemas.DatasetUpdate, db: Session = Depends(db.get_db)):
    db_dataset = crud.update_dataset(db, dataset_id=dataset_id, dataset_update=dataset_update)
    if not db_dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return db_dataset


@app.delete("/datasets/{dataset_id}", response_model=schemas.Dataset)
def delete_dataset(dataset_id: int, db: Session = Depends(db.get_db)):
    db_dataset = crud.delete_dataset(db, dataset_id=dataset_id)
    if not db_dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return db_dataset
