from urllib.parse import unquote
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from starlette.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from helpers.general_helpers import perform_search
from models.G0T0 import (
    Archetype,
    Background,
    ContentSource,
    CustomizationType,
    EnhancedItemSubtype,
    EnhancedItemType,
    EquipmentCategory,
    EquipmentSubCategory,
    ImprovementType,
    ManeuverType,
    PowerAlignment,
    PowerType,
    PrimaryClass,
    Property,
    Rarity,
    Species,
)
from models.general import Content
from models.db import get_db  # Dependency for database session

resolute = APIRouter()
templates = Jinja2Templates(directory="templates")


# --------------------------- #
# Routes
# --------------------------- #

@resolute.get("/house_rules", response_class=HTMLResponse)
async def house_rules(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("shell.html", 
                                      {"request": request, 
                                       "content": _get_content(request, db),
                                       "csp_nonce": request.state.csp_nonce})


@resolute.get("/content_rulings", response_class=HTMLResponse)
async def content_rulings(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("shell.html", {"request": request, "content": _get_content(request, db)})


@resolute.get("/errata", response_class=HTMLResponse)
async def errata(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("shell.html", {"request": request, "content": _get_content(request, db)})


@resolute.get("/tech_powers", response_class=HTMLResponse)
async def tech_powers(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("powers.html", {"request": request, "title": "Tech Powers", "options": _get_options(db)})


@resolute.get("/force_powers", response_class=HTMLResponse)
async def force_powers(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("powers.html", {"request": request, "title": "Force Powers", "options": _get_options(db)})





# --------------------------- #
# Private Methods
# --------------------------- #

def _get_content(request: Request, db: Session) -> Content:
    content = (
        db.query(Content)
        .filter(Content.key == request.url.path.replace("/", ""))
        .first()
    )
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return content


def _get_options(db: Session):
    options = {}

    def build_select_option(value_attr: str, label_attr: str, obj: []):
        return [
            {"value": getattr(o, value_attr), "label": getattr(o, label_attr)}
            for o in obj
        ]

    alignments = db.query(PowerAlignment).all()
    equipment_category = db.query(EquipmentCategory).all()
    rarity = db.query(Rarity).all()
    e_type = db.query(EnhancedItemType).all()
    sizes = [
        {"value": v, "label": v}
        for v in ["Tiny", "Small", "Medium", "Large", "Huge", "Gargantuan"]
    ]
    stats = [
        {"value": v, "label": v}
        for v in [
            "Strength",
            "Dexterity",
            "Constitution",
            "Intelligence",
            "Wisdom",
            "Charisma",
            "Any",
        ]
    ]

    options["power-type"] = build_select_option("id", "value", db.query(PowerType).all())
    options["content-source"] = build_select_option("id", "name", db.query(ContentSource).all())
    options["alignment"] = build_select_option("id", "value", alignments)
    options["sizes"] = sizes
    options["stats"] = stats
    options["equipment-category"] = build_select_option("id", "value", equipment_category)
    options["equipment-subcategory"] = [
        j.to_dict() for j in db.query(EquipmentSubCategory).all()
    ]
    options["rarity"] = build_select_option("id", "value", rarity)
    options["enhanced-item-type"] = build_select_option("id", "value", e_type)
    options["enhanced-item-subtype"] = [
        j.to_dict() for j in db.query(EnhancedItemSubtype).all()
    ]
    options["maneuver-type"] = build_select_option("id", "value", db.query(ManeuverType).all())
    options["customization-type"] = build_select_option("id", "value", db.query(CustomizationType).all())
    options["class-improvement-type"] = build_select_option("id", "value", db.query(ImprovementType).all())

    return options