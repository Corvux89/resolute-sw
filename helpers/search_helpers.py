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
    # Species
    # Classes
    # Archetypes
    # Equipment
    # Enhanced Items
    # Features
    # Backgrounds
    # Maneuvers
    # Customizations
    # Improvements

    return results[:25]