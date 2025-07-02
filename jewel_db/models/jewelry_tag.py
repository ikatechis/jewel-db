# jewel_db/models/jewelry_tag.py
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import relationship
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .jewelry_item import JewelryItem


class ItemTagLink(SQLModel, table=True):
    item_id: int | None = Field(
        default=None, foreign_key="jewelryitem.id", primary_key=True
    )
    tag_id: int | None = Field(
        default=None, foreign_key="jewelrytag.id", primary_key=True
    )


class JewelryTagBase(SQLModel):
    name: str = Field(unique=True, index=True, description="lower-case tag")


class JewelryTag(JewelryTagBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    items: list[JewelryItem] = Relationship(
        sa_relationship=relationship(
            "JewelryItem",
            secondary="itemtaglink",
            back_populates="tags",
        ),
        link_model=ItemTagLink,
    )


class JewelryTagCreate(JewelryTagBase):
    pass


class JewelryTagUpdate(SQLModel):
    name: str | None = None


class JewelryTagRead(SQLModel):
    id: int
    name: str
