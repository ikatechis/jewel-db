# jewel_db/api/items.py
from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, Body, Depends, File, HTTPException, UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from jewel_db.core.dependencies import get_db
from jewel_db.models.jewelry_image import JewelryImage
from jewel_db.models.jewelry_item import JewelryItem
from jewel_db.models.jewelry_tag import JewelryTag
from jewel_db.schemas.jewelry_item import (
    JewelryItemCreate,
    JewelryItemRead,
    JewelryItemUpdate,
)
from jewel_db.services.image_utils import normalise_image

router = APIRouter(prefix="/items", tags=["items"])

MEDIA_DIR = Path("media")
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MEDIA_DIR.mkdir(exist_ok=True)

# ─── Image endpoints ─────────────────────────────────────────────────────────


@router.post(
    "/{item_id}/images",
    response_model=list[JewelryImage],
    status_code=201,
)
async def upload_item_images(
    item_id: int,
    files: list[UploadFile] = File([]),
    session: Session = Depends(get_db),
):
    # ... your existing image logic untouched ...
    files = [
        f for f in files if f.filename and f.content_type != "application/octet-stream"
    ]
    if not files:
        return []
    item = session.get(JewelryItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    max_order = (
        session.exec(
            select(JewelryImage.sort_order)
            .where(JewelryImage.item_id == item_id)
            .order_by(JewelryImage.sort_order.desc())
        ).first()
        or 0
    )
    saved: list[JewelryImage] = []
    for idx, upload in enumerate(files):
        if upload.content_type not in ALLOWED_TYPES:
            raise HTTPException(status_code=400, detail="Invalid image type")
        raw = await upload.read()
        if upload.content_type == "image/gif":
            data, ext = raw, ".gif"
        else:
            data, ext = normalise_image(raw, upload.content_type)
        fname = f"{uuid.uuid4().hex}{ext}"
        (MEDIA_DIR / fname).write_bytes(data)
        img = JewelryImage(
            url=f"/media/{fname}",
            sort_order=max_order + idx + 1,
            item_id=item_id,
        )
        session.add(img)
        saved.append(img)
    session.commit()
    return saved


@router.get(
    "/{item_id}/images",
    response_model=list[JewelryImage],
)
def list_item_images(
    item_id: int,
    session: Session = Depends(get_db),
):
    # ... unchanged ...
    item = session.get(JewelryItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return session.exec(
        select(JewelryImage)
        .where(JewelryImage.item_id == item_id)
        .order_by(JewelryImage.sort_order)
    ).all()


@router.patch("/{item_id}/images/reorder", status_code=204)
def reorder_images(
    item_id: int,
    new_order: list[int] = Body(..., embed=True),
    session: Session = Depends(get_db),
):
    # ... unchanged ...
    for idx, img_id in enumerate(new_order):
        img = session.get(JewelryImage, img_id)
        if img and img.item_id == item_id:
            img.sort_order = idx + 1
            session.add(img)
    session.commit()


@router.delete("/{item_id}/images/{image_id}", status_code=204)
def delete_item_image(
    *,
    item_id: int,
    image_id: int,
    session: Session = Depends(get_db),
):
    # ... unchanged ...
    img = session.get(JewelryImage, image_id)
    if not img or img.item_id != item_id:
        raise HTTPException(status_code=404, detail="Image not found")
    file_path = MEDIA_DIR / Path(img.url).name
    try:
        if file_path.exists():
            file_path.unlink()
    except Exception:
        pass
    session.delete(img)
    session.commit()
    remaining = session.exec(
        select(JewelryImage)
        .where(JewelryImage.item_id == item_id)
        .order_by(JewelryImage.sort_order)
    ).all()
    for idx, image in enumerate(remaining):
        image.sort_order = idx + 1
        session.add(image)
    session.commit()
    return


# ─── CRUD endpoints ───────────────────────────────────────────────────────────


@router.post(
    "/",
    response_model=JewelryItemRead,
    status_code=201,
)
def create_item(
    *,
    session: Session = Depends(get_db),
    item_in: JewelryItemCreate,
):
    # ── lowercase & link tags ────────────────────────────────────────────
    tag_objs: list[JewelryTag] = []
    for name in item_in.tags or []:
        nm = name.lower().strip()
        tag = session.exec(select(JewelryTag).where(JewelryTag.name == nm)).first()
        if not tag:
            tag = JewelryTag(name=nm)
            session.add(tag)
        tag_objs.append(tag)

    # ── create the item ─────────────────────────────────────────────────
    item = JewelryItem.model_validate(item_in, update={"tags": tag_objs})
    session.add(item)

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="Name must be unique")

    # ── refresh & ensure tags are loaded ──
    session.refresh(item)  # pulls DB-generated fields into the same instance
    _ = item.tags  # triggers lazy load so response includes tags

    return item


@router.get(
    "/",
    response_model=list[JewelryItemRead],
)
def list_items(*, session: Session = Depends(get_db)):
    items = session.exec(
        select(JewelryItem).options(selectinload(JewelryItem.tags))
    ).all()
    return items


@router.get(
    "/{item_id}",
    response_model=JewelryItemRead,
)
def get_item(
    *,
    session: Session = Depends(get_db),
    item_id: int,
):
    stmt = (
        select(JewelryItem)
        .options(selectinload(JewelryItem.tags))
        .where(JewelryItem.id == item_id)
    )
    item = session.exec(stmt).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.patch(
    "/{item_id}",
    response_model=JewelryItemRead,
)
def update_item(
    *,
    session: Session = Depends(get_db),
    item_id: int,
    item_in: JewelryItemUpdate,
):
    item = session.get(JewelryItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    data = item_in.model_dump(exclude_unset=True)
    tag_names = data.pop("tags", None)

    # apply scalar updates
    for key, val in data.items():
        setattr(item, key, val)

    # sync tags if provided
    if tag_names is not None:
        new_tags: list[JewelryTag] = []
        for name in tag_names:
            nm = name.lower().strip()
            if not nm:
                continue
            tag = session.exec(select(JewelryTag).where(JewelryTag.name == nm)).first()
            if not tag:
                tag = JewelryTag(name=nm)
                session.add(tag)
                session.commit()
                session.refresh(tag)
            new_tags.append(tag)
        item.tags = new_tags

    session.add(item)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="Name must be unique")

    # return with tags eagerly loaded
    result = session.exec(
        select(JewelryItem)
        .options(selectinload(JewelryItem.tags))
        .where(JewelryItem.id == item_id)
    ).one()
    return result


@router.delete("/batch", response_model=list[int], status_code=200)
async def batch_delete_items(
    ids: list[int] = Body(..., embed=True),
    session: Session = Depends(get_db),
):
    if not ids:
        raise HTTPException(status_code=400, detail="`ids` list is empty")
    deleted: list[int] = []
    for iid in ids:
        itm = session.get(JewelryItem, iid)
        if itm:
            session.delete(itm)
            deleted.append(iid)
    session.commit()
    return deleted


@router.delete(
    "/{item_id}",
    status_code=204,
)
def delete_item(
    *,
    session: Session = Depends(get_db),
    item_id: int,
):
    item = session.get(JewelryItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    session.delete(item)
    session.commit()


@router.patch(
    "/reorder",
    status_code=204,
)
def reorder_items(
    new_order: list[int] = Body(..., embed=True),
    session: Session = Depends(get_db),
):
    for idx, iid in enumerate(new_order):
        itm = session.get(JewelryItem, iid)
        if itm:
            itm.sort_order = idx + 1
            session.add(itm)
    session.commit()
    return
