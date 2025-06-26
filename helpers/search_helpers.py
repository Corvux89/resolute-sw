from urllib.parse import urlencode
from fastapi import Request
from models.cache import ResoluteCache
from models.general import SearchResult
from models.resolute import *

async def perform_search(request: Request, query: str):
    results: List[SearchResult] = []

    if not query or query == "":
        return []

    cache: ResoluteCache = request.app.cache

    # Web Contents
    contents = cache.fetch(WebContent)

    contents = list(filter(
        lambda c: query.lower() in c.content.lower(),
        contents
    ))

    for c in contents:
        route = request.url_for(c.key)
        results.append(
            SearchResult(title=f"Server Content - {c.key}", url=str(route))
        )

    # Powers
    powers = cache.fetch(Power)

    powers = list(filter(
        lambda p: query.lower() in p.name.lower() or
        (p.prerequisite and query.lower() in p.prerequisite.lower()) or
        query.lower() in p.description.lower(),
        powers
        ))
    
    for p in powers:
        route = request.url_for(f"{p.type.value.lower()}_powers")
        query_params = urlencode({"name": p.name})
        results.append(
            SearchResult(title=f"{p.type.value} Power - {p.name}", url=f"{route}?{query_params}")
        )

    # Species
    species = cache.fetch(Species)

    species = list(filter(
        lambda s: query.lower() in s.value.lower(),
        species
    ))

    for s in species:
        route = request.url_for("species")
        query_params = urlencode({"name": s.value})
        results.append(
            SearchResult(title=f"Species - {s.value}", url=f"{route}?{query_params}")
        )

    # Classes
    prim_classes = cache.fetch(PrimaryClass)

    
    # Archetypes
    # Equipment
    # Enhanced Items
    # Features
    # Backgrounds
    # Maneuvers
    # Customizations
    # Improvements

    return results[:25]