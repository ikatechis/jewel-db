# jewel_db/models/jewelry_item.py
from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import relationship
from sqlmodel import Field, Relationship, SQLModel

from .jewelry_image import JewelryImage


class JewelryItemBase(SQLModel):
    name: str = Field(index=True, unique=True, description="Item name/title")
    material: str | None = Field(default=None, description="Primary material")
    gemstone: str | None = Field(default=None, description="Gemstone type")
    weight: float | None = Field(default=None, description="Weight in grams")
    price: float | None = Field(default=None, description="Price in your currency")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )
    description: str | None = Field(default=None, description="Detailed description")


class JewelryItem(JewelryItemBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    sort_order: int = Field(default=0, index=True, description="UI sort order")

    images: list[JewelryImage] = Relationship(
        sa_relationship=relationship(
            "JewelryImage",
            back_populates="item",
            order_by="JewelryImage.sort_order",
            cascade="all, delete-orphan",
        )
    )


class JewelryItemCreate(JewelryItemBase):
    pass


class JewelryItemUpdate(SQLModel):
    name: str | None = None
    material: str | None = None
    gemstone: str | None = None
    weight: float | None = None
    price: float | None = None
    description: str | None = None
