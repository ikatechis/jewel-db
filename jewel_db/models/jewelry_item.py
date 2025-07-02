# jewel_db/models/jewelry_item.py
from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import relationship
from sqlmodel import Field, Relationship, SQLModel

from .jewelry_image import JewelryImage  # noqa: F401, F811
from .jewelry_tag import ItemTagLink, JewelryTag, JewelryTagRead


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


class JewelryItem(JewelryItemBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    images: list[JewelryImage] = Relationship(  # noqa: F821
        sa_relationship=relationship(
            "JewelryImage",
            back_populates="item",
            cascade="all, delete-orphan",
        )
    )

    tags: list[JewelryTag] = Relationship(
        sa_relationship=relationship(
            "JewelryTag",
            secondary="itemtaglink",
            back_populates="items",
        ),
        link_model=ItemTagLink,
    )


class JewelryItemCreate(JewelryItemBase):
    tags: list[str] = []


class JewelryItemUpdate(SQLModel):
    name: str | None = None
    category: str | None = None
    material: str | None = None
    gemstone: str | None = None
    weight: float | None = None
    price: float | None = None
    description: str | None = None
    tags: list[str] | None = None


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
    # include the related tags
    tags: list[JewelryTagRead] = []
