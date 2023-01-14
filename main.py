from typing import Optional
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


models.Base.metadata.create_all(bind=engine)


class Task(BaseModel):
    title: str
    description: Optional[str]
    state: int = Field(
        gt=-1, lt=3, description="O estado deve estar entre 1 e 3")


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.get('/')
async def get_all_tasks(db: Session = Depends(get_db)):
    return db.query(models.Tasks).all()


@app.post('/')
async def create_task(task: Task, db: Session = Depends(get_db)):
    task_model = models.Tasks()
    task_model.title = task.title
    task_model.description = task.description
    task_model.state = task.state

    db.add(task_model)
    db.commit()
    return success_response(201, task)


@app.delete('/{id}')
async def delete_task(id: int, db: Session = Depends(get_db)):
    finded_task = db.query(models.Tasks).filter(models.Tasks.id == id).first()

    if finded_task is None:
        raise http_exceptinon()

    db.query(models.Tasks).filter(models.Tasks.id == id).delete()
    db.commit()
    return success_response(200)


@app.get('/{id}')
async def get_task_by_id(id: int, db: Session = Depends(get_db)):
    task_finded = db.query(models.Tasks).filter(models.Tasks.id == id).first()

    if task_finded is not None:
        return success_response(200, task_finded)
    raise http_exceptinon()


@app.put('/{id}')
async def update_task(id: int, task: Task, db: Session = Depends(get_db)):
    finded_task = db.query(models.Tasks).filter(models.Tasks.id == id).first()

    if finded_task is None:
        raise http_exceptinon()

    finded_task.title = task.title
    finded_task.description = task.description
    finded_task.state = task.state

    db.add(finded_task)
    db.commit()

    return success_response(200, finded_task)


@app.get('/tasks/{state}')
async def get_tasks_by_status(state: int, db: Session = Depends(get_db)):
    return db.query(models.Tasks).filter(models.Tasks.state == state).all()


def http_exceptinon():
    return HTTPException(status_code=404, detail="Tarefa não encontrada")


def success_response(status_code: int, content: Optional[dict] = None):
    return {
        "status": status_code,
        "message": "Sucesso!",
        "content": content
    }
