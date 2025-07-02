# jewel_db/main.py

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
    page: int = 1,
    search: str | None = None,
    material: str | None = None,
    gemstone: str | None = None,
    session=Depends(get_session),
):
    # 1. Query & filter
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

    all_items = session.exec(stmt).all()

    # 2. Pagination
    per_page = 9
    total_count = len(all_items)
    total_pages = (total_count - 1) // per_page + 1
    start = (page - 1) * per_page
    end = start + per_page
    items = all_items[start:end]

    # 3. Thumbnails lookup (whatever your code does)
    thumbs = {item.id: item.images[0].url if item.images else None for item in items}

    # 4. Stats
    avg_price = (
        (sum(i.price or 0 for i in all_items) / total_count) if total_count else 0
    )
    total_weight = sum(i.weight or 0 for i in all_items)
    total_price = sum(i.price or 0 for i in all_items)  # ← new line

    # 5. Distinct filters
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
            "total_price": total_price,  # ← make sure this is here
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
