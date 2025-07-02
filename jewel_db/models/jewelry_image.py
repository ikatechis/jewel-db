# jewel_db/models/jewelry_image.py
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import relationship
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .jewelry_item import JewelryItem


class JewelryImageBase(SQLModel):
    url: str
    sort_order: int = 0
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)


class JewelryImage(JewelryImageBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    item_id: int = Field(foreign_key="jewelryitem.id")

    item: JewelryItem = Relationship(
        sa_relationship=relationship(
            "JewelryItem",
            back_populates="images",
        )
    )
