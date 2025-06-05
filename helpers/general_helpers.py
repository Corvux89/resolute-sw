from flask import current_app, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from models.G0T0 import Power, Species
from models.general import Content, SearchResult

def perform_search(query: str):
    db: SQLAlchemy = current_app.config.get("DB")
    results: list[SearchResult] = []
    
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

    return results


