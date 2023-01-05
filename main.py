from typing import Optional
from fastapi import FastAPI, Depends, HTTPException
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


class Task(BaseModel):
    title: str
    description: Optional[str]
    status: int = Field(
        gt=-1, lt=4, description="O status deve estar entre 1 e 3")


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
    task_model.status = task.status

    db.add(task_model)
    db.commit()
    return {"message": "Task Criada com sucesso"}


@app.delete('/{id}')
async def delete_task(id: int, db: Session = Depends(get_db)):
    finded_task = db.query(models.Tasks).filter(models.Tasks.id == id).first()

    if finded_task is None:
        raise HTTPException(status_code=404, detail="Task não encontrada")

    db.query(models.Tasks).filter(models.Tasks.id == id).delete()
    db.commit()
    return {"message": "Tarefa deletada com sucesso!"}


@app.get('/{id}')
async def get_task_by_id(id: int, db: Session = Depends(get_db)):
    task_finded = db.query(models.Tasks).filter(models.Tasks.id == id).first()
    print(task_finded)
    if task_finded is not None:
        return task_finded
    raise HTTPException(status_code=404, detail="Task não encontrada")


@app.put('/{id}')
async def update_task(id: int, task: Task, db: Session = Depends(get_db)):
    finded_task = db.query(models.Tasks).filter(models.Tasks.id == id).first()

    if finded_task is None:
        raise HTTPException(status_code=404, detail="Task não encontrada")

    finded_task.title = task.title
    finded_task.description = task.description
    finded_task.status = task.status

    db.add(finded_task)
    db.commit()

    return {"message": "Tarefa atualizada com sucessso!"}


@app.get('/tasks/{status}')
async def get_tasks_by_status(status: int, db: Session = Depends(get_db)):
    return db.query(models.Tasks).filter(models.Tasks.status == status).all()
