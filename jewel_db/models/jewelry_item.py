# jewel_db/models/jewelry_item.py
from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import relationship
from sqlmodel import Field, Relationship, SQLModel

from .jewelry_image import JewelryImage  # noqa: F401
from .jewelry_tag import ItemTagLink, JewelryTag  # noqa: F401


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

    images: list[JewelryImage] = Relationship(
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
