from __future__ import annotations

from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


@router.get("/echo")
def echo(message: str, times: int = 1) -> dict:
    times = max(1, min(times, 10))
    return {"message": message, "echo": [message] * times}


class ItemIn(BaseModel):
    name: str
    description: Optional[str] = None


@router.post("/items")
def create_item(item: ItemIn) -> dict:
    return {"created": True, "item": item.model_dump()}
