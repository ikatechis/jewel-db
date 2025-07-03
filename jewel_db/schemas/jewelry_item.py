# jewel_db/schemas/jewelry_item.py
from __future__ import annotations

from datetime import datetime

from pydantic import field_validator
from sqlmodel import Field, SQLModel

from .jewelry_tag import JewelryTagRead  # noqa: E402


class JewelryItemBase(SQLModel):
    name: str = Field(index=True)
    category: str | None = None
    material: str | None = None
    gemstone: str | None = None
    weight: float | None = 0.0
    price: float | None = 0.0
    description: str | None = None
    sort_order: int | None = 9999
    created_at: datetime = Field(default_factory=datetime.utcnow)


class JewelryItemCreate(JewelryItemBase):
    tags: list[str | None] = []

    # remove None or blank strings that a UI might send
    @field_validator("tags", mode="before")
    @classmethod
    def _strip_empty(cls, v):
        return [t for t in v if t]


class JewelryItemUpdate(SQLModel):
    name: str | None = None
    category: str | None = None
    material: str | None = None
    gemstone: str | None = None
    weight: float | None = None
    price: float | None = None
    description: str | None = None
    tags: list[str] | None = None

    @field_validator("tags", mode="before")
    @classmethod
    def _strip_empty(cls, v):
        if v is None:
            return v
        return [t for t in v if t]


class JewelryItemRead(SQLModel):
    id: int
    name: str
    category: str | None
    material: str | None
    gemstone: str | None
    weight: float | None
    price: float | None
    description: str | None
    sort_order: int | None
    created_at: datetime
    tags: list[JewelryTagRead] = []
