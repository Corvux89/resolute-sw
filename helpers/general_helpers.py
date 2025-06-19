from flask import current_app, url_for
from models.G0T0 import *
from models.general import Content, SearchResult


def perform_search(query: str):
    results: list[SearchResult] = []

    if query == "":
        return []

    for rule in current_app.url_map.iter_rules():
        if query.lower() in rule.rule.lower() or query.lower() in rule.endpoint.lower():
            results.append(
                SearchResult(f"Page - {rule.rule.replace('/','')}", f"{rule.rule}")
            )

    # Web Content
    contents = [
        c
        for c in current_app.cache.fetch(Content)
        if query.lower() in c.content.lower()
    ]

    for c in contents:
        results.append(
            SearchResult(
                f"Server Content - {c.title}", f"{url_for(f'resolute.{c.key}')}"
            )
        )

    # Powers
    powers = [
        p
        for p in current_app.cache.fetch(Power)
        if query.lower() in p.name.lower() or query.lower() in p.pre_requisite.lower()
    ]

    for p in powers:
        results.append(
            SearchResult(
                f"{p.type.value} Power - {p.name}",
                f"{url_for(f'resolute.{p.type.value.lower()}_powers', name=p.name)}",
            )
        )

    # Species
    species = [
        s
        for s in current_app.cache.fetch(Species)
        if query.lower() in s.value.lower()
    ]

    for s in species:
        results.append(
            SearchResult(
                f"Species - {s.value}",
                f"{url_for('resolute.species_details', species=s.value.lower())}",
            )
        )

    # Classes
    classes = [
        c
        for c in current_app.cache.fetch(PrimaryClass)
        if query.lower() in c.value.lower() or query.lower() in c.features.lower() or query.lower() in c.summary.lower()
    ]

    for c in classes:
        results.append(
            SearchResult(
                f"Class - {c.value}",
                f"{url_for('resolute.class_details', p_class=c.value.lower())}",
            )
        )

    # Archetypes
    arch = [
        a
        for a in current_app.cache.fetch(Archetype)
        if query.lower() in a.value.lower()
    ]

    for a in arch:
        results.append(
            SearchResult(
                f"Archetype - {a.value}",
                f"{url_for('resolute.archetype_details', arch=a.value.lower())}",
            )
        )

    # Equipment
    equip = [
        e
        for e in current_app.cache.fetch(Equipment)
        if query.lower() in e.name.lower()
    ]

    for e in equip:
        url = "adventuring"
        if e.category.value == "Weapon":
            url = "weapons"
        elif e.category == "Armor":
            url = "armor"

        results.append(
            SearchResult(
                f"Mundane Item: {e.category.value} - {e.name}",
                f"{url_for(f'resolute.{url}', name=e.name)}",
            )
        )

    # Enhanced Items
    items = [
        i
        for i in current_app.cache.fetch(EnhancedItem)
        if query.lower() in i.name.lower() or (i.prerequisite and query.lower() in i.prerequisite.lower())
    ]

    for i in items:
        url = 'enhanced_other'
        if i.type.value == "Consumable":
            url = 'enhanced_consumable'
        elif i.type.value == "Item Modification":
            url = 'enhanced_mods'
        elif i.type.value == "Droid Customization":
            url = 'enhanced_mods'
        elif i.type.value == "Cybernetic Augmentation":
            url = 'enhanced_augmentation'

        results.append(
            SearchResult(
                f"Enhanced Item: {i.type.value} - {i.name}",
                f"{url_for(f'resolute.{url}', name=i.name)}"
            )
        )

    # Features
    feats = [
        f
        for f in current_app.cache.fetch(Feat)
        if query.lower() == f.name.lower()
    ]

    for f in feats:
        results.append(
            SearchResult(
                f"Feature - {f.name}", f"{url_for('resolute.feats', name=f.name)}"
            )
        )

    # Backgrounds
    backgrounds = [
        b
        for b in current_app.cache.fetch(Background)
        if query.lower() in b.name.lower()
    ]

    for b in backgrounds:
        results.append(
            SearchResult(
                f"Background - {b.name}",
                f"{url_for('resolute.background_details', back=b.name.lower())}"
            )
        )

    # Maneuvers
    maneuvers = [
        m
        for m in current_app.cache.fetch(Maneuver)
        if query.lower() in m.name.lower()
    ]

    for m in maneuvers:
        results.append(
            SearchResult(
                f"Maneuver - {m.name}",
                f"{url_for('resolute.maneuvers', name=m.name)}"
            )
        )

    # Customizations
    customizations = [
        c
        for c in current_app.cache.fetch(Customization)
        if query.lower() in c.name.lower()
    ]

    for c in customizations:
        url = None
        if c.type.value == 'Fighting Style':
            url='fighting_styles'
        elif c.type.value == 'Fighting Mastery':
            url='fighting_masteries'
        elif c.type.value == 'Lightsaber Form':
            url='lightsaber_forms'
        elif c.type.value == 'Weapon Focus':
            url='weapon_focuses'
        elif c.type.value == 'Weapon Supremacy':
            url='weapon_supremacies'

        if url:
            results.append(
                SearchResult(
                    f"{c.type.value} - {c.name}",
                    f"{url_for(f'resolute.{url}', name=c.name)}"
                )
            )

    # Improvements
    improvements = [
        i
        for i in current_app.cache.fetch(Improvement)
        if query.lower() in i.name.lower()
    ]

    for i in improvements:
        try:
            url = i.type.value.lower().replace(' ', "_")+"s"

            results.append(
                SearchResult(
                    f"{i.type.value} - {i.name}",
                    f"{url_for(f'resolute.{url}', name=i.name)}"
                )
            )
        except:
            pass


    return results[:25]
