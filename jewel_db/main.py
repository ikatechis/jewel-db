# jewel_db/main.py
from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from .api.items import router as items_router
from .api.tags import router as tags_router
from .config import DEBUG
from .db import get_session, init_db
from .models.jewelry_image import JewelryImage
from .models.jewelry_item import JewelryItem
from .models.jewelry_tag import JewelryTag

app = FastAPI(title="Jewelry Inventory System", debug=DEBUG)


@app.on_event("startup")
def on_startup():
    init_db()


# Mount static directories
app.mount("/static", StaticFiles(directory="jewel_db/static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")

# Include API routers
app.include_router(items_router, prefix="/api")
app.include_router(tags_router, prefix="/api")

templates = Jinja2Templates(directory="jewel_db/templates")


# Home
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ─── Items List Page ──────────────────────────────────────────────────────────
@app.get("/items", response_class=HTMLResponse)
def list_items_page(
    request: Request,
    page: int = 1,
    search: str | None = None,
    material: str | None = None,
    gemstone: str | None = None,
    session: Session = Depends(get_session),
):
    # 1. Build base query (eager‐load tags)
    stmt = select(JewelryItem).options(selectinload(JewelryItem.tags))
    if search:
        stmt = stmt.where(JewelryItem.name.ilike(f"%{search}%"))
    if material:
        stmt = stmt.where(JewelryItem.material == material)
    if gemstone:
        stmt = stmt.where(
            JewelryItem.gemstone.is_(None)
            if gemstone == "None"
            else JewelryItem.gemstone == gemstone
        )

    all_items = session.exec(stmt).all()

    # 2. Paginate
    per_page = 9
    total_count = len(all_items)
    total_pages = (total_count - 1) // per_page + 1 if total_count else 1
    start = (page - 1) * per_page
    end = start + per_page
    items = all_items[start:end]

    # 3. Thumbnails
    thumbs = {i.id: (i.images[0].url if i.images else None) for i in items}

    # 4. Stats
    avg_price = (
        (sum(i.price or 0 for i in all_items) / total_count) if total_count else 0
    )
    total_price = sum(i.price or 0 for i in all_items)
    total_weight = sum(i.weight or 0 for i in all_items)
    no_image_count = sum(1 for i in all_items if not i.images)

    # 5. Distinct filter values
    materials = sorted({i.material for i in all_items if i.material})
    gemstones = sorted({i.gemstone for i in all_items if i.gemstone})

    return templates.TemplateResponse(
        "items_list.html",
        {
            "request": request,
            "items": items,
            "materials": materials,
            "gemstones": gemstones,
            "thumbs": thumbs,
            "page": page,
            "total_pages": total_pages,
            "search": search,
            "material": material,
            "gemstone": gemstone,
            "total_count": total_count,
            "avg_price": avg_price,
            "total_weight": total_weight,
            "total_price": total_price,
            "no_image_count": no_image_count,
        },
    )


# ─── Add Item Page ────────────────────────────────────────────────────────────
@app.get("/items/create", response_class=HTMLResponse)
def items_create(request: Request):
    return templates.TemplateResponse(
        "item_form.html", {"request": request, "item": None}
    )


# ─── Item Detail Page ─────────────────────────────────────────────────────────
@app.get("/items/{item_id}", response_class=HTMLResponse)
def item_detail(
    request: Request,
    item_id: int,
    session: Session = Depends(get_session),
):
    # Eager‐load tags
    stmt = (
        select(JewelryItem)
        .options(selectinload(JewelryItem.tags))
        .where(JewelryItem.id == item_id)
    )
    item = session.exec(stmt).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    images = session.exec(
        select(JewelryImage)
        .where(JewelryImage.item_id == item_id)
        .order_by(JewelryImage.sort_order)
    ).all()

    return templates.TemplateResponse(
        "item_detail.html", {"request": request, "item": item, "images": images}
    )


# ─── Edit Item Page ───────────────────────────────────────────────────────────
@app.get("/items/{item_id}/edit", response_class=HTMLResponse)
def item_edit(
    request: Request,
    item_id: int,
    session: Session = Depends(get_session),
):
    # Eager‐load tags for the edit form
    stmt = (
        select(JewelryItem)
        .options(selectinload(JewelryItem.tags))
        .where(JewelryItem.id == item_id)
    )
    item = session.exec(stmt).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return templates.TemplateResponse(
        "item_form.html", {"request": request, "item": item}
    )


# ─── Tags Admin Page ─────────────────────────────────────────────────────────
@app.get("/tags", response_class=HTMLResponse)
def tags_list_page(request: Request, session: Session = Depends(get_session)):
    tags = session.exec(select(JewelryTag).order_by(JewelryTag.name)).all()
    return templates.TemplateResponse(
        "tags_list.html", {"request": request, "tags": tags}
    )


# ─── Health Check ─────────────────────────────────────────────────────────────
@app.get("/api/health")
def health_check():
    return {"status": "ok"}
