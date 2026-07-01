from typing import TypeVar

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

ModelT = TypeVar("ModelT")


def list_items(db: Session, model: type[ModelT]) -> list[ModelT]:
    return list(db.scalars(select(model).order_by(model.id.desc())).all())


def get_item(db: Session, model: type[ModelT], item_id: int) -> ModelT:
    item = db.get(model, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Registro nao encontrado")
    return item


def create_item(db: Session, model: type[ModelT], payload) -> ModelT:
    item = model(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_item(db: Session, model: type[ModelT], item_id: int, payload) -> ModelT:
    item = get_item(db, model, item_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


def delete_item(db: Session, model: type[ModelT], item_id: int) -> dict[str, bool]:
    item = get_item(db, model, item_id)
    db.delete(item)
    db.commit()
    return {"ok": True}
