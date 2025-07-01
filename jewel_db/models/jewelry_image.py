# jewel_db/models/jewelry_image.py

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import relationship
from sqlmodel import Field, Relationship, SQLModel


class JewelryImageBase(SQLModel):
    url: str = Field(description="Image URL or /media path")
    sort_order: int = Field(default=0, description="Position in gallery")
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)


class JewelryImage(JewelryImageBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    item_id: int = Field(foreign_key="jewelryitem.id")

    item: JewelryItem | None = Relationship(  # noqa: F821
        sa_relationship=relationship("JewelryItem", back_populates="images")
    )


class JewelryImageCreate(JewelryImageBase):
    pass
