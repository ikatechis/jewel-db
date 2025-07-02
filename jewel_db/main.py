# jewel_db/main.py
from math import ceil

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from .api.items import router as items_router
from .config import DEBUG
from .db import get_session, init_db
from .models.jewelry_image import JewelryImage
from .models.jewelry_item import JewelryItem  # ← top‐level import

app = FastAPI(title="Jewelry Inventory System", debug=DEBUG)


@app.on_event("startup")
def on_startup():
    init_db()


app.mount("/static", StaticFiles(directory="jewel_db/static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")
app.include_router(items_router, prefix="/api")

templates = Jinja2Templates(directory="jewel_db/templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/items", response_class=HTMLResponse)
def list_items_page(
    request: Request,
    search: str | None = None,
    material: str | None = None,
    gemstone: str | None = None,
    sort_by: str | None = None,
    sort_dir: str = "asc",
    page: int = 1,
    page_size: int = 12,
    session: Session = Depends(get_session),
):
    # Trim leading/trailing whitespace on all text inputs
    search = search.strip() if search and search.strip() else None
    material = material.strip() if material and material.strip() else None
    gemstone = gemstone.strip() if gemstone and gemstone.strip() else None
    sort_by = sort_by.strip() if sort_by and sort_by.strip() else None
    sort_dir = sort_dir.strip() if sort_dir and sort_dir.strip() else "asc"

    # 1) Base filter
    stmt = select(JewelryItem)
    if search:
        stmt = stmt.where(JewelryItem.name.ilike(f"%{search}%"))
    if material:
        stmt = stmt.where(JewelryItem.material == material)
    if gemstone:
        if gemstone == "None":
            stmt = stmt.where(JewelryItem.gemstone.is_(None))
        else:
            stmt = stmt.where(JewelryItem.gemstone == gemstone)

    # 2) Compute full‐set stats
    all_items = session.exec(stmt).all()
    total_count = len(all_items)
    total_weight = sum(i.weight or 0 for i in all_items)
    total_price = sum(i.price or 0 for i in all_items)
    avg_price = round(total_price / total_count, 2) if total_count else 0

    # 3) Count items with an image
    ids = [i.id for i in all_items]
    with_ids = (
        session.exec(
            select(JewelryImage.item_id).where(JewelryImage.item_id.in_(ids)).distinct()
        ).all()
        if ids
        else []
    )
    no_count = total_count - len(with_ids)

    # 4) Ordering: default by sort_order, or by chosen column
    if sort_by in {"name", "price", "weight", "created_at"}:
        field = getattr(JewelryItem, sort_by)
        stmt = stmt.order_by(field.asc() if sort_dir == "asc" else field.desc())
    else:
        stmt = stmt.order_by(JewelryItem.sort_order.asc())

    # 5) Pagination
    total_pages = ceil(total_count / page_size) if total_count else 1
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    items = session.exec(stmt).all()

    # 6) Thumbnails for this page
    thumbs: dict[int, str | None] = {}
    for it in items:
        url = (
            session.exec(
                select(JewelryImage.url)
                .where(JewelryImage.item_id == it.id)
                .order_by(JewelryImage.sort_order)
            ).first()
            or None
        )
        thumbs[it.id] = url

    # 7) Facets
    materials = session.exec(
        select(JewelryItem.material).distinct().order_by(JewelryItem.material)
    ).all()
    gemstones = session.exec(
        select(JewelryItem.gemstone).distinct().order_by(JewelryItem.gemstone)
    ).all()

    return templates.TemplateResponse(
        "items_list.html",
        {
            "request": request,
            "items": items,
            "thumbs": thumbs,
            "search": search,
            "material": material,
            "gemstone": gemstone,
            "materials": materials,
            "gemstones": gemstones,
            "sort_by": sort_by,
            "sort_dir": sort_dir,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "total_count": total_count,
            "avg_price": avg_price,
            "total_weight": total_weight,
            "no_count": no_count,
        },
    )


@app.get("/items/create", response_class=HTMLResponse)
def items_create(request: Request):
    return templates.TemplateResponse(
        "item_form.html", {"request": request, "item": None}
    )


@app.get("/items/{item_id}", response_class=HTMLResponse)
def item_detail(
    request: Request, item_id: int, session: Session = Depends(get_session)
):
    item = session.get(JewelryItem, item_id)
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


@app.get("/items/{item_id}/edit", response_class=HTMLResponse)
def item_edit(request: Request, item_id: int, session: Session = Depends(get_session)):
    item = session.get(JewelryItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return templates.TemplateResponse(
        "item_form.html", {"request": request, "item": item}
    )


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
