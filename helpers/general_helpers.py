from flask import current_app, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from models.G0T0 import Archetype, EnhancedItem, Equipment, Feat, Power, PrimaryClass, Species
from models.general import Content, SearchResult

def perform_search(query: str):
    db: SQLAlchemy = current_app.config.get("DB")
    results: list[SearchResult] = []

    if query == "":
        return []

    for rule in current_app.url_map.iter_rules():
        if query.lower() in rule.rule.lower() or query.lower() in rule.endpoint.lower():
            results.append(SearchResult(f"Page - {rule.rule.replace('/','')}", f"{rule.rule}"))
    
    # Web Content
    contents = db.session.query(Content).filter(Content.content.ilike(f"%{query.lower()}%")).all()

    for c in contents:
        results.append(SearchResult(f"Server Content - {c.title}", f"{url_for(f'resolute.{c.key}')}"))
    
    # Powers
    powers = db.session.query(Power).filter(or_(
        Power.name.ilike(f"%{query.lower()}%"),
        Power.pre_requisite.ilike(f"{query.lower()}")
    )).all()

    for p in powers:
        results.append(SearchResult(f"{p.type.value} Power - {p.name}", f"{url_for(f'resolute.{p.type.value.lower()}_powers', name=p.name)}"))

    # Species
    species = db.session.query(Species).filter(or_(
        Species.value.ilike(f"%{query.lower()}%")
    )).all()

    for s in species:
        results.append(SearchResult(f"Species - {s.value}", f"{url_for('resolute.species_details', species=s.value.lower())}"))

    # Classes
    classes = db.session.query(PrimaryClass).filter(or_(
        PrimaryClass.value.ilike(f"%{query.lower()}%"),
        PrimaryClass.features.ilike(f"%{query.lower()}%"),
        PrimaryClass.summary.ilike(f"%{query.lower()}%")
    )).all()

    for c in classes:
        results.append(SearchResult(f"Class - {c.value}", f"{url_for('resolute.class_details', p_class=c.value.lower())}"))

    # Archetypes
    arch = db.session.query(Archetype).filter(or_(
        Archetype.value.ilike(f"%{query.lower()}%"),
    ))

    for a in arch:
        results.append(SearchResult(f"Archetype - {a.value}", f"{url_for('resolute.archetype_details', arch=a.value.lower())}"))

    # Equipment
    equip = db.session.query(Equipment).filter(or_(
        Equipment.name.ilike(f"%{query.lower()}%")
    ))

    for e in equip:
        url = "adventuring"
        if e.category.value == "Weapon":
            url="weapons"
        elif e.category == "Armor":
            url="armor"
            

        results.append(SearchResult(f"Mundane Item: {e.category.value} - {e.name}", f"{url_for(f'resolute.{url}', name=e.name)}"))
    
    # Enhanced Item
    items = db.session.query(EnhancedItem).filter(or_(
        EnhancedItem.name.ilike(f"%{query.lower()}%")
    ))

    for i in items:
        results.append(SearchResult(f"Enhanced Item - {i.name}"), f"{url_for('resolute.enhanced_items', name=i.name)}")

    # Features
    feats = db.session.query(Feat).filter(or_(
        Feat.name.ilike(f"%{query.lower()}%"),
        Feat.text.ilike(f"%{query.lower()}%")
    ))

    for f in feats:
        results.append(SearchResult(f"Feature - {f.name}", f"{url_for('resolute.feats', name=f.name)}"))

    return results


