# jewel_db/schemas/jewelry_tag.py
from sqlmodel import Field, SQLModel


class JewelryTagBase(SQLModel):
    name: str = Field(description="lower-case tag")


class JewelryTagCreate(JewelryTagBase):
    pass


class JewelryTagUpdate(SQLModel):
    name: str | None = None


class JewelryTagRead(JewelryTagBase):
    id: int
