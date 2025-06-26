from urllib.parse import unquote
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse

from helpers.auth_helpers import is_beta_tester
from helpers.search_helpers import perform_search
from models.exceptions import BadRequest, NotFound
from models.resolute import *
from models.templates import ResoluteJinja, build_select_option


frontend_router = APIRouter(
    tags=["Frontend"],
    default_response_class=HTMLResponse,
    dependencies=[Depends(is_beta_tester)],
)

templates = ResoluteJinja(directory="templates")

@frontend_router.get('/search')
async def search(request: Request, q: str):
    results = await perform_search(request, q)

    return await templates.TemplateResponse("search_results.html",
                                      {
                                          "request": request,
                                          "query": q,
                                          "results": results
                                      })



# Server Content
async def get_web_content(request: Request, key: str):
    content = request.app.cache.fetch(WebContent, key)

    if not content:
        raise NotFound("Content not found")

    return await templates.TemplateResponse(
        "/shell.html",
        {
            "request": request,
            "content": content,
        },
    )


@frontend_router.get("/house_rules")
async def house_rules(request: Request):
    return await get_web_content(request, "house_rules")


@frontend_router.get("/content_rulings")
async def content_rulings(request: Request):
    return await get_web_content(request, "content_rulings")


@frontend_router.get("/errata")
async def errata(request: Request):
    return await get_web_content(request, "errata")


# Characters
@frontend_router.get("/species/")
@frontend_router.get("/species/{species_name:path}")
async def species(request: Request, species_name: str = None):
    if species_name:
        species = request.app.cache.fetch(Species, value=unquote(species_name))

        if not Species:
            raise NotFound("Species not found")
        return await templates.TemplateResponse(
            "/species/species.html",
            {
                "request": request,
                "species": species,
            },
        )

    # species_list = request.app.cache.get_model(Species, SpeciesSchema)
    species_list = request.app.cache.fetch(SpeciesSchema)
    return await templates.TemplateResponse(
        "/species/species_list.html", {"request": request, "table": species_list}
    )


@frontend_router.get("/classes")
@frontend_router.get("/classes/{class_name:path}")
async def classes(request: Request, class_name: str = None):
    if class_name:
        prim_class = request.app.cache.fetch(PrimaryClass, value=unquote(class_name))

        if not prim_class:
            raise NotFound("Class not found")
        return await templates.TemplateResponse(
            "/classes/class.html",
            {
                "request": request,
                "primary_class": prim_class,
            },
        )

    class_list = request.app.cache.fetch(PrimaryClassSchema)
    return await templates.TemplateResponse(
        "/classes/classes_list.html", {"request": request, "table": class_list}
    )


@frontend_router.get("/archetypes")
@frontend_router.get("/archetypes/{arch_name:path}")
async def archetypes(request: Request, arch_name: str = None):
    options = {}
    class_options = build_select_option(request.app.cache.fetch(PrimaryClass))
    options["classes"] = class_options

    if arch_name:
        archetype = request.app.cache.fetch(Archetype, value=arch_name)

        if not archetype:
            raise NotFound("Archetype not found")

        return await templates.TemplateResponse(
            "/archetypes/archetype.html",
            {
                "request": request,
                "archetype": archetype,
            },
            options=options,
        )

    archetype_list = request.app.cache.fetch(ArchetypeSchema)
    return await templates.TemplateResponse(
        "/archetypes/archetype_list.html",
        {"request": request, "table": archetype_list},
        options=options,
    )


@frontend_router.get("/backgrounds")
@frontend_router.get("/backgrounds/{back_name:path}")
async def backgrounds(request: Request, back_name: str = None):
    if back_name:
        background = request.app.cache.fetch(Background, name=back_name)

        if not background:
            raise NotFound("Background not found")

        return await templates.TemplateResponse(
            "/backgrounds/background.html",
            {"request": request, "background": background},
        )

    background_list = request.app.cache.fetch(BackgroundSchema)
    if not background_list:
        # This will happen the first time, but not too often
        request.app.cache.update(request.app.db, Background)
        background_list = request.app.cache.fetch(BackgroundSchema)
    return await templates.TemplateResponse(
        "/backgrounds/background_list.html",
        {"request": request, "table": background_list},
    )


@frontend_router.get("/features")
async def features(request: Request):
    feature_list = request.app.cache.fetch(FeatureSchema)

    return await templates.TemplateResponse(
        "/feats.html", {"request": request, "table": feature_list}
    )


@frontend_router.get("/maneuvers")
async def maneuvers(request: Request):
    options = {}
    types = build_select_option(request.app.cache.fetch(ManeuverType))
    options["maneuver-type"] = types
    maneuver_list = request.app.cache.fetch(ManeuverSchema)

    return await templates.TemplateResponse(
        "/maneuvers.html", {"request": request, "table": maneuver_list}, options=options
    )


async def get_customizations_by_type(
    request: Request, customization_type: str, title: str
):
    options = {}
    types = build_select_option(request.app.cache.fetch(CustomizationType))
    options["customization-type"] = types

    customizations = request.app.cache.fetch(CustomizationSchema)
    customization_list = list(
        filter(
            lambda c: c["type"] and c["type"]["value"] == customization_type,
            customizations,
        )
    )

    return await templates.TemplateResponse(
        "/customizations.html",
        {"request": request, "table": customization_list, "title": title},
        options=options,
    )


@frontend_router.get("/fighting_styles")
async def fighting_styles(request: Request):
    return await get_customizations_by_type(
        request, "Fighting Style", "Fighting Styles"
    )


@frontend_router.get("/fighting_masteries")
async def fighting_masteries(request: Request):
    return await get_customizations_by_type(
        request, "Fighting Mastery", "Fighting Masteries"
    )


@frontend_router.get("/lightsaber_forms")
async def lightsaber_forms(request: Request):
    return await get_customizations_by_type(
        request, "Lightsaber Form", "Lightsaber Forms"
    )


@frontend_router.get("/weapon_focus")
async def weapon_focus(request: Request):
    return await get_customizations_by_type(request, "Weapon Focus", "Weapon Focuses")


@frontend_router.get("/weapon_supremacies")
async def weapon_supremacies(request: Request):
    return await get_customizations_by_type(
        request, "Weapon Supremacy", "Weapon Supremacies"
    )


async def get_improvement_by_type(request: Request, improvement_type: str, title: str):
    options = {}
    types = build_select_option(request.app.cache.fetch(ImprovementType))
    options["class-improvement-type"] = types

    improvements = request.app.cache.fetch(ImprovementSchema)
    improvement_list = list(
        filter(
            lambda c: c["type"] and c["type"]["value"] == improvement_type, improvements
        )
    )

    return await templates.TemplateResponse(
        "/class_improvements.html",
        {"request": request, "table": improvement_list, "title": title},
        options=options,
    )


@frontend_router.get("/class_improvements")
async def class_improvements(request: Request):
    return await get_improvement_by_type(
        request, "Class Improvement", "Class Improvements"
    )


@frontend_router.get("/multiclass_improvements")
async def multiclass_improvements(request: Request):
    return await get_improvement_by_type(
        request, "Multiclass Improvement", "Multiclass Improvements"
    )


@frontend_router.get("/splashclass_improvements")
async def splashclass_improvements(request: Request):
    return await get_improvement_by_type(
        request, "Splashclass Improvement", "Splashclass Improvements"
    )


# Items
async def get_equipment_type_category(request: Request, category: str, title: str):
    options = {}
    options["equipment-category"] = build_select_option(
        request.app.cache.fetch(EquipmentCategory)
    )
    options["equipment-subcategory"] = build_select_option(
        request.app.cache.fetch(EquipmentSubCategory)
    )

    equipment = request.app.cache.fetch(EquipmentSchema)

    if category.lower() == "adventuring":
        equipment = list(
            filter(
                lambda e: e["category"] and e["category"]["id"] not in [3, 4], equipment
            )
        )
    else:
        equipment = list(
            filter(
                lambda e: e["category"] and e["category"]["value"] == category,
                equipment,
            )
        )

    return await templates.TemplateResponse(
        "/equipment.html",
        {
            "request": request,
            "table": equipment,
            "properties": request.app.cache.fetch(PropertySchema),
            "title": title,
        },
        options=options,
    )


@frontend_router.get("/weapons")
async def weapons(request: Request):
    return await get_equipment_type_category(request, "Weapon", "Weapons")


@frontend_router.get("/armor")
async def armor(request: Request):
    return await get_equipment_type_category(request, "Armor", "Armor")


@frontend_router.get("/adventuring")
async def adventuring(request: Request):
    return await get_equipment_type_category(request, "Adventuring", "Adventuring Gear")


async def get_item_type(request: Request, category: str, title: str):
    options = {}
    options["enhanced-item-type"] = build_select_option(
        request.app.cache.fetch(EnhancedItemType)
    )
    options["enhanced-item-subtype"] = request.app.cache.fetch(
        EnhancedItemSubTypeSchema
    )
    options["rarity"] = build_select_option(request.app.cache.fetch(Rarity))

    items = request.app.cache.fetch(EnhancedItemSchema)

    if category.lower() == "other":
        items = list(
            filter(lambda i: i["type"] and i["type"]["id"] not in [3, 7, 5, 4], items)
        )
    else:
        items = list(
            filter(lambda e: e["type"] and e["type"]["value"] == category, items)
        )

    return await templates.TemplateResponse(
        "/enhanced_items.html",
        {"request": request, "table": items, "title": title},
        options=options,
    )


@frontend_router.get("/consumables")
async def consumables(request: Request):
    return await get_item_type(request, "Consumable", "Consumables")


@frontend_router.get("/item_modifications")
async def item_modifications(request: Request):
    return await get_item_type(request, "Item Modification", "Item Modifications")


@frontend_router.get("/droid_customizations")
async def droid_customizations(request: Request):
    return await get_item_type(request, "Droid Customization", "Droid Customizations")


@frontend_router.get("/cybernetic_augmentation")
async def cybernetic_augmentations(request: Request):
    return await get_item_type(
        request, "Cybernetic Augmentation", "Cybernetic Augmentations"
    )


@frontend_router.get("/enhanced_items")
async def enhanced_items(request: Request):
    return await get_item_type(request, "Other", "Enhanced Items")


@frontend_router.get("/tech_powers")
async def tech_powers(request: Request):
    powers = request.app.cache.fetch(PowerSchema)
    powers = list(filter(lambda p: p["type"] and p["type"]["id"] == 2, powers))
    return await templates.TemplateResponse(
        "/powers.html", {"request": request, "table": powers, "title": "Tech Powers"}
    )


@frontend_router.get("/force_powers")
async def force_powers(request: Request):
    powers = request.app.cache.fetch(PowerSchema)
    powers = list(filter(lambda p: p["type"] and p["type"]["id"] == 1, powers))
    return await templates.TemplateResponse(
        "/powers.html", {"request": request, "table": powers, "title": "Force Powers"}
    )