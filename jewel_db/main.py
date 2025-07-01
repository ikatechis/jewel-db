# jewel_db/main.py

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from .api.items import router as items_router
from .config import DEBUG
from .db import get_session, init_db
from .models.jewelry_image import JewelryImage
from .models.jewelry_item import JewelryItem

app = FastAPI(title="Jewelry Inventory System", debug=DEBUG)


# Initialize the database (create tables) on startup
@app.on_event("startup")
def on_startup():
    init_db()


# Mount static assets (CSS/JS) and uploaded media
app.mount("/static", StaticFiles(directory="jewel_db/static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")

# Include API routes under /api
app.include_router(items_router, prefix="/api")

# Configure Jinja2 templates directory
templates = Jinja2Templates(directory="jewel_db/templates")

# ---------------------------------------------------------
# Frontend Routes
# ---------------------------------------------------------


@app.get("/")
def home(request: Request):
    """
    Render the home page (templates/index.html).
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/items")
def items_list(request: Request, session: Session = Depends(get_session)):
    """
    Render the list of all items, with thumbnails.
    """
    items = session.exec(select(JewelryItem)).all()

    # For each item, fetch its first image URL (or None)
    thumbs = {}
    for item in items:
        first_url = session.exec(
            select(JewelryImage.url)
            .where(JewelryImage.item_id == item.id)
            .order_by(JewelryImage.sort_order)
        ).first()
        thumbs[item.id] = first_url

    return templates.TemplateResponse(
        "items_list.html", {"request": request, "items": items, "thumbs": thumbs}
    )


@app.get("/items/create")
def items_create(request: Request):
    """
    Render the 'create new item' form.
    """
    return templates.TemplateResponse(
        "item_form.html", {"request": request, "item": None}
    )


@app.get("/items/{item_id}")
def item_detail(
    request: Request, item_id: int, session: Session = Depends(get_session)
):
    """
    Render the detail page for a single item, including all its images.
    """
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


@app.get("/items/{item_id}/edit")
def item_edit(request: Request, item_id: int, session: Session = Depends(get_session)):
    """
    Render the 'edit item' form.
    """
    item = session.get(JewelryItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return templates.TemplateResponse(
        "item_form.html", {"request": request, "item": item}
    )


# ---------------------------------------------------------
# Health Check
# ---------------------------------------------------------


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
