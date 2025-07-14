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

    # Routes
    routes = []
    for route in request.app.routes:
        if hasattr(route, 'path') and hasattr(route, 'name') and not route.path.startswith('/api') and route.name and "{" not in route.path:
            if query.lower() in route.name.lower() or query.lower() in route.name.replace("_", " ").lower():
                routes.append(route)

    for route in routes:
        results.append(
            SearchResult(title=f"Page - {route.name.replace('_', ' ').title()}", url=f"{route.path}")
        )

    # Web Contents
    contents = cache.fetch(WebContent)

    contents = list(filter(
        lambda c: query.lower() in c.content.lower(),
        contents
    ))

    for c in contents:
        route = request.url_for(c.key)
        results.append(
            SearchResult(title=f"Server Content - {c.key}", url=f"{route}")
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
        route = request.url_for("species", name=s.value)
        results.append(
            SearchResult(title=f"Species - {s.value}", url=f"{route}")
        )

    # Classes
    prim_classes = cache.fetch(PrimaryClass)

    prim_classes = list(filter(
        lambda c: query.lower() in c.value.lower(),
        prim_classes
    ))

    for c in prim_classes:
        route = request.url_for("classes", name=c.value)
        results.append(
            SearchResult(title=f"Class - {c.value}", url=f"{route}")
        )

    # Archetypes
    arch = cache.fetch(Archetype)

    arch = list(filter(
        lambda a: query.lower() in a.value.lower(),
        arch
    ))

    for a in arch:
        route = request.url_for("archetypes", name=a.value)
        results.append(
            SearchResult(title=f"Archetype - {a.value}", url=f"{route}")
        )

    # Equipment
    equipment = cache.fetch(Equipment)

    equipment = list(filter(
        lambda e: query.lower() in e.name.lower(),
        equipment
    ))

    for e in equipment:
        if e.category and e.category.value == "Weapon":
            route = request.url_for("weapons")
        elif e.category and e.category.value == "Armor":
            route = request.url_for("armor")
        else:
            route = request.url_for("adventuring")
        query_params = urlencode({"name": e.name})
        results.append(
            SearchResult(title=f"Equipment - {e.name}", url=f"{route}?{query_params}")
        )

    # Enhanced Items      
    items = cache.fetch(EnhancedItem)

    items = list(filter(
        lambda i: query.lower() in i.name.lower(),
        items
    ))

    for i in items:
        if i.type and i.type.value == "Consumable":
            route = request.url_for("consumables")
        elif i.type and i.type.value == "Item Modification":
            route = request.url_for("item_modifications")
        elif i.type and i.type.value == "Droid Customization":
            route = request.url_for("droid_customizations")
        elif i.type and i.type.value == "Cybernetic Augmentation":
            route = request.url_for("cybernetic_augmentations")
        else:
            route = request.url_for("enhanced_items")

        query_params = urlencode({"name": i.name})

        results.append(
            SearchResult(title=f"{i.type.value if i.type else 'Enhanced Item'} - {i.name}", url=f"{route}?{query_params}")
        )

    # Feats
    feats = cache.fetch(Feat)

    feats = list(filter(
        lambda f: query.lower() in f.name.lower(),
        feats
    ))

    for f in feats:
        route = request.url_for("feats")
        query_params = urlencode({"name": f.name})
        results.append(
            SearchResult(title=f"Feature - {f.name}", url=f"{route}?{query_params}")
        )

    # Backgrounds
    backgrounds = cache.fetch(Background)

    backgrounds = list(filter(
        lambda b: query.lower() in b.name.lower(),
        backgrounds
    ))

    for b in backgrounds:
        route = request.url_for("backgrounds", name=b.name)
        results.append(
            SearchResult(title=f"Background - {b.name}", url=f"{route}")
        )

    # Maneuvers
    maneuvers = cache.fetch(Maneuver)

    maneuvers = list(filter(
        lambda m: query.lower() in m.name.lower(),
        maneuvers
    ))

    for m in maneuvers:
        route = request.url_for("maneuvers")
        query_params = urlencode({"name": m.name})
        results.append(
            SearchResult(title=f"Maneuvers - {m.name}", url=f"{route}?{query_params}")
        )

    # Customizations
    customizations = cache.fetch(Customization)

    customizations = list(filter(
        lambda c: query.lower() in c.name.lower(),
        customizations
    ))

    for c in customizations:
        route = None
        if c.type and c.type.value == "Fighting Style":
            route = request.url_for("fighting_styles")
        elif c.type and c.type.value == "Fighting Mastery":
            route = request.url_for("fighting_masteries")
        elif c.type and c.type.value == "Weapon Focus":
            route = request.url_for("weapon_focus")
        elif c.type and c.type.value == "Weapon Supremacy":
            route = request.url_for("weapon_supremacies")
        query_params = urlencode({"name": c.name})
        if route:
            results.append(
                SearchResult(title=f"{c.type.value} - {c.name}", url=f"{route}?{query_params}")
            )

    # Improvements
    improvements = cache.fetch(Improvement)

    improvements = list(filter(
        lambda i: query.lower() in i.name.lower(),
        improvements
    ))

    for i in improvements:
        route = request.url_for(f"{i.type.value.lower().replace(' ', '_')}s")
        query_params = urlencode({"name": i.name})

        results.append(
            SearchResult(title=f"{i.type.value} - {i.name}", url=f"{route}?{query_params}")
        )


    return results[:25]