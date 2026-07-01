from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models import Task
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.services.crud import create_item, delete_item, get_item, update_item

router = APIRouter(prefix="/tarefas", tags=["tarefas"])


@router.get("", response_model=list[TaskRead])
def list_tasks(status: str | None = None, prioridade: str | None = None, db: Session = Depends(get_db)):
    stmt = select(Task).order_by(Task.id.desc())
    if status:
        stmt = stmt.where(Task.status == status)
    if prioridade:
        stmt = stmt.where(Task.prioridade == prioridade)
    return db.scalars(stmt).all()


@router.post("", response_model=TaskRead, status_code=201)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    return create_item(db, Task, payload)


@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: int, db: Session = Depends(get_db)):
    return get_item(db, Task, task_id)


@router.put("/{task_id}", response_model=TaskRead)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)):
    return update_item(db, Task, task_id, payload)


@router.patch("/{task_id}/concluir", response_model=TaskRead)
def complete_task(task_id: int, db: Session = Depends(get_db)):
    return update_item(db, Task, task_id, TaskUpdate(status="Concluida"))


@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    return delete_item(db, Task, task_id)
