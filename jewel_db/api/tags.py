from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from jewel_db.db import get_session
from jewel_db.models.jewelry_tag import JewelryTag, JewelryTagCreate, JewelryTagUpdate

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/", response_model=list[JewelryTag])
def list_tags(session: Session = Depends(get_session)):
    return session.exec(select(JewelryTag).order_by(JewelryTag.name)).all()


@router.post("/", response_model=JewelryTag, status_code=201)
def create_tag(tag_in: JewelryTagCreate, session: Session = Depends(get_session)):
    tag = JewelryTag(name=tag_in.name.lower())
    session.add(tag)
    session.commit()
    session.refresh(tag)
    return tag


@router.patch("/{tag_id}", response_model=JewelryTag)
def update_tag(
    tag_id: int, tag_in: JewelryTagUpdate, session: Session = Depends(get_session)
):
    tag = session.get(JewelryTag, tag_id)
    if not tag:
        raise HTTPException(404)
    if tag_in.name:
        tag.name = tag_in.name.lower()
    session.add(tag)
    session.commit()
    session.refresh(tag)
    return tag


@router.delete("/{tag_id}", status_code=204)
def delete_tag(tag_id: int, session: Session = Depends(get_session)):
    tag = session.get(JewelryTag, tag_id)
    if not tag:
        raise HTTPException(404)
    session.delete(tag)
    session.commit()
