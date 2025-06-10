import json
from urllib.parse import unquote

from flask import Blueprint, current_app, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

from helpers.general_helpers import perform_search
from models.G0T0 import Archetype, ContentSource, PowerAlignment, PowerType, PrimaryClass, Species
from models.exceptions import NotFound
from models.general import Content

resolute_blueprint = Blueprint("resolute", __name__)


@resolute_blueprint.get("/house_rules")
def house_rules():
    return render_template("shell.html", content=_get_content())


@resolute_blueprint.get("/content_rulings")
def content_rulings():
    return render_template("shell.html", content=_get_content())


@resolute_blueprint.get("/errata")
def errata():
    return render_template("shell.html", content=_get_content())


@resolute_blueprint.get("/tech_powers")
def tech_powers():
    return render_template("powers.html", title="Tech Powers", options=_get_options())


@resolute_blueprint.get("/force_powers")
def force_powers():
    return render_template("powers.html", title="Force Powers", options=_get_options())

@resolute_blueprint.get('/weapons')
def weapons():
    return render_template("equipment.html", title="Weapons", options=_get_options())

@resolute_blueprint.get('/armor')
def armor():
    return render_template("equipment.html", title="Armor", options=_get_options())

@resolute_blueprint.get('/adventuring')
def adventuring():
    return render_template("equipment.html", title="Adventuring Gear", options=_get_options())

@resolute_blueprint.get("/search")
def search():
    query = request.args.get('q', '')

    results = perform_search(query)

    return render_template("search_results.html", query=query, results=results)

@resolute_blueprint.get("/species")
def species():
    return render_template("/species/species_list.html", options=_get_options())

@resolute_blueprint.get("/species/<species>")
def species_details(species):
    db: SQLAlchemy = current_app.config.get("DB")
    species: Species = db.session.query(Species).filter(func.lower(Species.value) == unquote(species).lower()).first()

    if not species:
        raise NotFound()

    return render_template("/species/species.html", species=species, options=_get_options())

@resolute_blueprint.get("/classes")
def classes():
    return render_template("/classes/classes_list.html", options=_get_options())

@resolute_blueprint.get("/classes/<p_class>")
def class_details(p_class):
    db: SQLAlchemy = current_app.config.get("DB")
    primary_class: PrimaryClass = db.session.query(PrimaryClass).filter(func.lower(PrimaryClass.value) == unquote(p_class).lower()).first()

    if not primary_class:
        raise NotFound()

    return render_template("/classes/class.html", primary_class=primary_class, options=_get_options())

@resolute_blueprint.get("/archetypes")
def archetypes():
    db: SQLAlchemy = current_app.config.get("DB")
    classes = db.session.query(PrimaryClass.id, PrimaryClass.value).all()

    prim_classes = [{"value": v.id, "label": v.value} for v in classes]
    
    return render_template("/archetypes/archetype_list.html", options=_get_options(), classes=prim_classes)

@resolute_blueprint.get("/archetypes/<arch>")
def archetype_details(arch):
    db: SQLAlchemy = current_app.config.get("DB")
    archetype: Archetype = db.session.query(Archetype).filter(func.lower(Archetype.value) == unquote(arch).lower()).first()

    if not archetype:
        raise NotFound()

    return render_template("/archetypes/archetype.html", archetype=archetype, options=_get_options())

# --------------------------- #
# Private Methods
# --------------------------- #

def _get_content() -> Content:
    db: SQLAlchemy = current_app.config.get("DB")
    content: Content = (
        db.session.query(Content).filter(Content.key == request.path.replace("/","")).first()
    )

    if not content:
        raise NotFound()
    
    return content

def _get_options():
    db: SQLAlchemy = current_app.config.get("DB")
    options = {}

    power_type = db.session.query(PowerType).all()
    sources = db.session.query(ContentSource).all()
    alignments = db.session.query(PowerAlignment).all()
    sizes = [{"value": v, "label": v} for v in ["Tiny", "Small", "Medium", "Large", "Huge", "Gargantuan"]]
    stats = [{"value": v, "label": v} for v in ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]]

    options["power-type"] = [{"value": p.id, "label": p.value} for p in power_type]
    options["content-source"] = [{"value": s.id, "label": s.name} for s in sources]
    options["alignment"] = [{"value": a.id, "label": a.value} for a in alignments]
    options["sizes"] = sizes
    options["stats"] = stats

    return options