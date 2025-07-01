# jewel_db/api/items.py

import uuid
from io import BytesIO
from pathlib import Path

from fastapi import APIRouter, Body, Depends, File, HTTPException, UploadFile
from PIL import Image
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from jewel_db.db import get_session
from jewel_db.models.jewelry_image import JewelryImage
from jewel_db.models.jewelry_item import (
    JewelryItem,
    JewelryItemCreate,
    JewelryItemUpdate,
)

router = APIRouter(prefix="/items", tags=["items"])

# Media and validation constants
MEDIA_DIR = Path("media")
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/gif"}
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB
MAX_DIMENSION = 2000  # pixels

# ─── Image endpoints ─────────────────────────────────────────────────────────


@router.post(
    "/{item_id}/images",
    response_model=list[JewelryImage],
    status_code=201,
)
async def upload_item_images(
    item_id: int,
    files: list[UploadFile] = File(...),
    session: Session = Depends(get_session),
):
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

    MEDIA_DIR.mkdir(exist_ok=True)
    saved: list[JewelryImage] = []
    for idx, file in enumerate(files):
        contents = await file.read()

        # Validate type & size
        if file.content_type not in ALLOWED_TYPES:
            raise HTTPException(status_code=400, detail="Invalid image type")
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="Image too large")

        # Validate dimensions
        try:
            img = Image.open(BytesIO(contents))
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid image file")
        if img.width > MAX_DIMENSION or img.height > MAX_DIMENSION:
            raise HTTPException(status_code=400, detail="Image dimensions too large")

        # Save to disk
        ext = file.filename.rsplit(".", 1)[-1].lower()
        fname = f"{uuid.uuid4().hex}.{ext}"
        path = MEDIA_DIR / fname
        path.write_bytes(contents)

        # Persist ORM object
        dbi = JewelryImage(
            url=f"/media/{fname}",
            sort_order=max_order + idx + 1,
            item_id=item_id,
        )
        session.add(dbi)
        saved.append(dbi)

    session.commit()
    return saved


@router.get(
    "/{item_id}/images",
    response_model=list[JewelryImage],
)
def list_item_images(
    item_id: int,
    session: Session = Depends(get_session),
):
    """
    Return all images for an item, ordered by sort_order.
    This lets your front-end do a GET /api/items/{item_id}/images
    instead of 405'ing.
    """
    item = session.get(JewelryItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    images = session.exec(
        select(JewelryImage)
        .where(JewelryImage.item_id == item_id)
        .order_by(JewelryImage.sort_order)
    ).all()
    return images


@router.patch(
    "/{item_id}/images/reorder",
    status_code=204,
)
def reorder_images(
    item_id: int,
    new_order: list[int] = Body(..., embed=True),
    session: Session = Depends(get_session),
):
    for idx, img_id in enumerate(new_order):
        img = session.get(JewelryImage, img_id)
        if img and img.item_id == item_id:
            img.sort_order = idx + 1
            session.add(img)
    session.commit()


@router.delete(
    "/{item_id}/images/{image_id}",
    status_code=204,
)
def delete_item_image(
    *,
    item_id: int,
    image_id: int,
    session: Session = Depends(get_session),
):
    """
    Delete a single JewelryImage (and its file) if it belongs to the given item,
    then re‐assign sort_order so the next image becomes the new thumbnail.
    """
    img = session.get(JewelryImage, image_id)
    if not img or img.item_id != item_id:
        raise HTTPException(status_code=404, detail="Image not found")

    # 1) delete file on disk
    file_path = MEDIA_DIR / Path(img.url).name
    if file_path.exists():
        try:
            file_path.unlink()
        except Exception:
            pass

    # 2) delete the record
    session.delete(img)
    session.commit()

    # 3) re‐normalize remaining images' sort_order
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
    item = JewelryItem.model_validate(item_in)
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
    for k, v in item_in.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    session.add(item)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="Name must be unique")
    session.refresh(item)
    return item


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
