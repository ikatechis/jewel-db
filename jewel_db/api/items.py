# jewel_db/api/items.py
from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, Body, Depends, File, HTTPException, UploadFile
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from jewel_db.db import get_session
from jewel_db.models.jewelry_image import JewelryImage
from jewel_db.models.jewelry_item import (
    JewelryItem,
    JewelryItemCreate,
    JewelryItemUpdate,
)
from jewel_db.models.jewelry_tag import JewelryTag
from jewel_db.services.image_utils import normalise_image

# ──────────────────────────────────────────────────────────────────────────────
router = APIRouter(prefix="/items", tags=["items"])

MEDIA_DIR = Path("media")
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}  # gif kept as-is
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
    session: Session = Depends(get_session),
):
    """Attach one or more images to an item.

    • Empty file list → no-op
    • Images of any size are down-scaled to ≤1600 px on the longest side
      (see `services/image_utils.py`) and saved as high-quality JPEG/PNG.
    """
    # Strip out phantom parts browsers send when no file is chosen
    files = [
        f for f in files if f.filename and f.content_type != "application/octet-stream"
    ]
    if not files:
        return []

    item = session.get(JewelryItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Determine starting sort order
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

        # GIFs are left untouched (no resize); others go through the helper
        if upload.content_type == "image/gif":
            data = raw
            ext = ".gif"
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


@router.get("/{item_id}/images", response_model=list[JewelryImage])
def list_item_images(
    item_id: int,
    session: Session = Depends(get_session),
):
    """Return all images for an item, ordered by sort_order."""
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
    session: Session = Depends(get_session),
):
    """Re-assign sort_order based on *new_order* list of image IDs."""
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
    session: Session = Depends(get_session),
):
    """Remove a single image file + DB row, then compact sort_order."""
    img = session.get(JewelryImage, image_id)
    if not img or img.item_id != item_id:
        raise HTTPException(status_code=404, detail="Image not found")

    # Delete file on disk (best-effort)
    file_path = MEDIA_DIR / Path(img.url).name
    try:
        if file_path.exists():
            file_path.unlink()
    except Exception:
        pass

    session.delete(img)
    session.commit()

    # Re-normalize remaining images
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
    response_model=JewelryItem,
    status_code=201,
)
def create_item(
    *,
    session: Session = Depends(get_session),
    item_in: JewelryItemCreate,
):
    # ensure lowercase tags
    tag_objs = []
    for name in item_in.tags or []:
        tag = session.exec(
            select(JewelryTag).where(JewelryTag.name == name.lower())
        ).first()
        if not tag:
            tag = JewelryTag(name=name.lower())
            session.add(tag)
        tag_objs.append(tag)
    item = JewelryItem.model_validate(item_in, update={"tags": tag_objs})
    session.add(item)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="Name must be unique")
    session.refresh(item)
    return item


@router.get(
    "/",
    response_model=list[JewelryItem],
)
def list_items(*, session: Session = Depends(get_session)):
    return session.exec(select(JewelryItem)).all()


@router.get(
    "/{item_id}",
    response_model=JewelryItem,
)
def get_item(
    *,
    session: Session = Depends(get_session),
    item_id: int,
):
    item = session.get(JewelryItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.patch(
    "/{item_id}",
    response_model=JewelryItem,
)
def update_item(
    *,
    session: Session = Depends(get_session),
    item_id: int,
    item_in: JewelryItemUpdate,
):
    item = session.get(JewelryItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # ── 1. scalar fields (everything except tags) ───────────────
    data = item_in.model_dump(exclude_unset=True, exclude={"tags"})
    for k, v in data.items():
        setattr(item, k, v)

    # ── 2. tags (replace whole set if provided) ────────────────
    if item_in.tags is not None:
        tag_objs = []
        for name in item_in.tags:
            name = name.lower()
            tag = session.exec(
                select(JewelryTag).where(JewelryTag.name == name)
            ).first()
            if not tag:
                tag = JewelryTag(name=name)
                session.add(tag)
            tag_objs.append(tag)
        item.tags = tag_objs  # replace M2M collection

    # ── 3. commit once ─────────────────────────────────────────
    session.add(item)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="Name must be unique")

    session.refresh(item)
    return item


@router.delete("/batch", response_model=list[int], status_code=200)
async def batch_delete_items(
    ids: list[int] = Body(..., embed=True),
    session: Session = Depends(get_session),
):
    if not ids:
        raise HTTPException(status_code=400, detail="`ids` list is empty")
    deleted: list[int] = []
    for item_id in ids:
        item = session.get(JewelryItem, item_id)
        if item:
            session.delete(item)
            deleted.append(item_id)
    session.commit()
    return deleted


@router.delete(
    "/{item_id}",
    status_code=204,
)
def delete_item(
    *,
    session: Session = Depends(get_session),
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
    session: Session = Depends(get_session),
):
    """
    Reorder JewelryItem.sort_order based on the list of IDs.
    """
    for idx, item_id in enumerate(new_order):
        item = session.get(JewelryItem, item_id)
        if item:
            item.sort_order = idx + 1
            session.add(item)
    session.commit()
    return
