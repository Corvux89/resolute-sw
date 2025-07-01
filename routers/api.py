from typing import List, Literal, Type, Union
import uuid
import logging
from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2AuthorizationCodeBearer
from sqlalchemy import and_
from sqlalchemy.orm import Session

from constants import AUTH_URL
from helpers.auth_helpers import is_admin
from models.cache import ResoluteCache
from models.exceptions import BadRequest, NotFound
from models.general import HTTPError
from models.resolute import *

logger = logging.getLogger(__name__)

# Doing this mostly for Swagger
oauth = OAuth2AuthorizationCodeBearer(
    AUTH_URL,
    "https://discord.com/api/oauth2/token",
    scopes={
        "identify": "Access to basic user information (username, discriminator, avatar)",
        "guilds": "Access to the list of guilds the user is a member of",
        "email": "Access to the user's email address",
    },
)


api_router = APIRouter(
    tags=["API"],
    default_response_class=JSONResponse,
    responses={
        400: {
            "model": HTTPError,
            "description": "Malformed or bad request from the client",
        },
        401: {"description": "Authentication required"},
    },
)

# Admin API routes - requires admin privileges
admin_api_router = APIRouter(
    tags=["Admin API"],
    default_response_class=JSONResponse,
    responses={
        400: {
            "model": HTTPError,
            "description": "Malformed or bad request from the client",
        },
        401: {"description": "Authentication required"},
        403: {"description": "Admin privileges required"},
    },
    dependencies=[Depends(is_admin)],
)


# Administrative
@admin_api_router.post("/refresh_cache")
async def refresh_cache(request: Request):
    request.app.cache.initialize(request.app, True)
    logger.info("Cache reloaded via API")
    return "Complete!"


# Server Content
@api_router.get("/content", response_model=WebContentFullSchema)
async def get_web_content(key: str):
    content = ResoluteCache.global_fetch(WebContent, key)

    if not content:
        raise BadRequest("Content not found")

    return content


@admin_api_router.patch("/content", response_model=WebContentSchema)
async def update_web_content(request: Request, content: WebContentSchema):
    content = await update_object(request.app, content, WebContent)

    return content


@api_router.get("/species", response_model=List[SpeciesSchema])
async def get_species(name: str = None, size: str = None):
    try:
        if name:
            s = ResoluteCache.global_fetch(Species, value=name)
            species = [s] if s else []
        elif size:
            species = list(
                filter(lambda s: s.size and size.lower() in s.size.lower(), species)
            )
        else:
            species = ResoluteCache.global_fetch(Species)
    except Exception as e:
        raise BadRequest(str(e))

    if not species:
        raise NotFound("Species not found")

    return species


@admin_api_router.post("/species", response_model=SpeciesSchema)
async def new_species(request: Request, species: SpeciesSchema):
    species = await create_object(request.app, species, Species)

    return species


@admin_api_router.patch("/species", response_model=SpeciesSchema)
async def update_species(request: Request, species: SpeciesSchema):
    species = await update_object(request.app, species, Species)

    return species


@admin_api_router.delete("/species/{obj_id}")
async def delete_species(request: Request, obj_id: int):
    db: Session = request.db

    if (
        db.query(Character)
        .filter(
            and_(
                Character.species == obj_id,
                Character.active == True
            )
        )
        .count()
        >0
        ):
        raise BadRequest("Current active characters have this species set")

    return await delete_object(request.app, Species, obj_id)


@api_router.get("/classes", response_model=List[PrimaryClassSchema])
async def get_classes(name: str = None):
    try:
        if name:
            c = ResoluteCache.global_fetch(PrimaryClass, value=name)
            classes = [c] if c else []
        else:
            classes = ResoluteCache.global_fetch(PrimaryClass)
    except Exception as e:
        raise BadRequest(str(e))

    if not classes:
        raise NotFound("Classes not found")

    return classes


@admin_api_router.post("/classes", response_model=PrimaryClassSchema)
async def new_class(request: Request, primary_class: PrimaryClassSchema):
    primary_class = await create_object(request.app, primary_class, PrimaryClass)

    return primary_class


@admin_api_router.patch("/classes", response_model=PrimaryClassSchema)
async def update_class(request: Request, primary_class: PrimaryClassSchema):
    primary_class = await update_object(request.app, primary_class, PrimaryClass)

    return primary_class


@admin_api_router.delete("/classes/{obj_id}")
async def delete_class(request: Request, obj_id: int):
    db: Session = request.db
    if (
        db.query(CharacterClass)
        .join(Character, Character.id == CharacterClass._character_id)
        .filter(
            and_(
                CharacterClass.active == True,
                Character.active == True,
                CharacterClass._primary_class == obj_id
            )
        )
        .count()
        >0
    ):
        raise BadRequest("current active charcter(s) have this class.")

    return await delete_object(request.app, PrimaryClass, obj_id)


@api_router.get("/archetypes", response_model=List[ArchetypeSchema])
def get_archetypes(name: str = None, parent_class: str = None, caster_type: str = None):

    try:
        if name:
            a = ResoluteCache.global_fetch(Archetype, value=name)
            archetypes = [a] if a else []
        else:
            archetypes = ResoluteCache.global_fetch(Archetype)

        if parent_class:
            archetypes = list(
                filter(
                    lambda c: c.parent_name
                    and parent_class.lower() in c.parent_name.lower(),
                    archetypes,
                )
            )

        if caster_type:
            archetypes = list(
                filter(
                    lambda a: a.caster_type
                    and caster_type.lower() in a.caster_type.value.lower(),
                    archetypes,
                )
            )
    except Exception as e:
        raise BadRequest(str(e))

    if not archetypes:
        raise NotFound("Archetypes not found")

    return archetypes


@admin_api_router.post("/archetypes", response_model=ArchetypeSchema)
async def new_archetype(request: Request, arch: ArchetypeSchema):
    archtype = await create_object(request.app, arch, Archetype)

    return archtype


@admin_api_router.patch("/archetypes", response_model=ArchetypeSchema)
async def update_archetype(request: Request, arch: ArchetypeSchema):
    archetype = await update_object(request.app, arch, Archetype)

    return archetype


@admin_api_router.delete("/archetypes/{obj_id}")
async def delete_archetype(request: Request, obj_id: int):
    db: Session = request.db
    if (
        db.query(CharacterClass)
        .join(Character, Character.id == CharacterClass._character_id)
        .filter(
            and_(
                CharacterClass.active == True,
                Character.active == True,
                CharacterClass._archetype == obj_id
            )
        )
        .count()
        >0
    ):
        raise BadRequest("current active charcter(s) have this archetype.")
    return await delete_object(request.app, Archetype, obj_id)


@api_router.get("/backgrounds", response_model=List[BackgroundSchema])
async def get_backgrounds(name: str = None):
    try:
        if name:
            b = ResoluteCache.global_fetch(Background, name=name)
            backgrounds = [b] if b else []
        else:
            backgrounds = ResoluteCache.global_fetch(Background)
    except Exception as e:
        raise BadRequest(str(e))

    if not backgrounds:
        raise NotFound("Backgrounds not found")

    return backgrounds


@admin_api_router.post("/backgrounds", response_model=BackgroundSchema)
async def new_background(request: Request, back: BackgroundSchema):
    background = await create_object(request.app, back, Background)

    return background


@admin_api_router.patch("/backgrounds", response_model=BackgroundSchema)
async def update_background(request: Request, back: BackgroundSchema):
    background = await update_object(request.app, back, Background)

    return background


@admin_api_router.delete("/backgrounds/{obj_id}")
async def delete_background(request: Request, obj_id: str):
    return await delete_object(request.app, Background, obj_id)


@api_router.get("/features", response_model=List[FeatSchema])
async def get_features(name: str = None):
    try:
        if name:
            f = ResoluteCache.global_fetch(Feat, name=name)
            features = [f] if f else []
        else:
            features = ResoluteCache.global_fetch(Feat)
    except Exception as e:
        raise BadRequest(str(e))

    if not features:
        raise NotFound("Features not found")

    return features


@admin_api_router.post("/features", response_model=FeatSchema)
async def new_feature(request: Request, feat: FeatSchema):
    feature = await create_object(request.app, feat, Feat)

    return feature


@admin_api_router.patch("/features", response_model=FeatSchema)
async def update_feature(request: Request, feat: FeatSchema):
    feature = await update_object(request.app, feat, Feat)

    return feature


@admin_api_router.delete("/features/{obj_id}")
async def delete_feature(request: Request, obj_id: str):
    return await delete_object(request.app, Feat, obj_id)


@api_router.get("/maneuvers", response_model=List[ManeuverSchema])
async def get_maneuvers(name: str = None, type: str = None):
    try:
        if name:
            m = ResoluteCache.global_fetch(Maneuver, name=name)
            maneuvers = [m] if m else []
        else:
            maneuvers = ResoluteCache.global_fetch(Maneuver)

        if type:
            maneuvers = list(
                filter(lambda m: m.type and m.type.value.lower() == type.lower()),
                maneuvers,
            )
    except Exception as e:
        raise BadRequest(str(e))

    if not maneuvers:
        raise NotFound("Maneuvers not found")

    return maneuvers


@admin_api_router.post("/maneuvers", response_model=ManeuverSchema)
async def new_maneuver(request: Request, man: ManeuverSchema):
    maneuver = await create_object(request.app, man, Maneuver)

    return maneuver


@admin_api_router.patch("/maneuvers", response_model=ManeuverSchema)
async def udpate_maneuver(request: Request, man: ManeuverSchema):
    maneuver = await update_object(request.app, man, Maneuver)

    return maneuver


@admin_api_router.delete("/maneuvers/{obj_id}")
async def delete_maneuver(request: Request, obj_id: str):
    await delete_object(request.app, Maneuver, obj_id)


@api_router.get("/customizations", response_model=List[CustomizationSchema])
async def get_customizations(name: str = None, type: str = None):
    try:
        if name:
            c = ResoluteCache.global_fetch(Customization, name=name)
            customizations = [c] if c else []
        else:
            customizations = ResoluteCache.global_fetch(Customization)

        if type:
            customizations = list(
                filter(
                    lambda c: c.type and type.lower() == c.type.value.lower(),
                    customizations,
                )
            )
    except Exception as e:
        raise BadRequest(str(e))

    if not customizations:
        raise NotFound("Customizations not found")

    return customizations


@admin_api_router.post("/customizations", response_model=CustomizationSchema)
async def new_customization(request: Request, custom: CustomizationSchema):
    customization = await create_object(request.app, custom, Customization)

    return customization


@admin_api_router.patch("/customizations", response_model=CustomizationSchema)
async def update_customization(request: Request, custom: CustomizationSchema):
    customization = await update_object(request.app, custom, Customization)

    return customization


@admin_api_router.delete("/customizations/{obj_id}")
async def delete_customization(request: Request, obj_id: str):
    return await delete_object(request.app, Customization, obj_id)


@api_router.get("/improvements", response_model=List[ImprovementSchema])
async def get_improvements(name: str = None, type: str = None):
    try:
        if name:
            i = ResoluteCache.global_fetch(Improvement, name=name)
            improvements = [i] if i else []
        else:
            improvements = ResoluteCache.global_fetch(Improvement)

        if type:
            improvements = list(
                filter(
                    lambda i: i.type and type.lower() == i.type.value.lower(),
                    improvements,
                )
            )
    except Exception as e:
        raise BadRequest(str(e))

    if not improvements:
        raise NotFound("Improvements not found")

    return improvements


@admin_api_router.post("/improvements", response_model=ImprovementSchema)
async def new_improvement(request: Request, imp: ImprovementSchema):
    improvement = await create_object(request.app, imp, Improvement)

    return improvement


@admin_api_router.patch("/improvements", response_model=ImprovementSchema)
async def update_improvement(request: Request, imp: ImprovementSchema):
    improvement = await update_object(request.app, imp, Improvement)

    return improvement


@admin_api_router.delete("/improvements/{obj_id}")
async def delete_improvement(request: Request, obj_id: str):
    return await delete_object(request.app, Improvement, obj_id)


@api_router.get("/equipment", response_model=List[EquipmentSchema])
async def get_equipment(
    name: str = None,
    category: str = None,
    sub_category: str = None,
):
    try:
        if name:
            e = ResoluteCache.global_fetch(Equipment, name=name)
            equipment = [e] if e else []
        else:
            equipment = ResoluteCache.global_fetch(Equipment)

        if category:
            if category.lower() == "adventuring":
                equipment = list(
                    filter(
                        lambda e: e.category and e.category.id not in [3, 4], equipment
                    )
                )
            else:
                equipment = list(
                    filter(
                        lambda e: e.category
                        and category.lower() == e.category.value.lower(),
                        equipment,
                    )
                )

        if sub_category:
            equipment = list(
                filter(
                    lambda e: e.sub_category
                    and sub_category.lower() == e.sub_category.value.lower(),
                    equipment,
                )
            )

    except Exception as e:
        raise BadRequest(str(e))

    if not equipment:
        raise NotFound("Equipment not found")

    return equipment


@admin_api_router.post("/equipment", response_model=EquipmentSchema)
async def new_equipment(request: Request, equip: EquipmentSchema):
    equipment: Equipment = await create_object(request.app, equip, Equipment)

    if (
        equipment.category
        and equipment.sub_category
        and equipment.sub_category.parent != equipment.category.id
    ):
        await delete_object(request.app, Equipment, equipment.id)
        raise BadRequest("Not a valid subcategory choice for this equipment category")

    return equipment


@admin_api_router.patch("/equipment", response_model=EquipmentSchema)
async def update_equipment(request: Request, equip: EquipmentSchema):
    equipment = await update_object(request.app, equip, Equipment)
    return equipment


@admin_api_router.delete("/equipment/{obj_id}")
async def delete_equipment(request: Request, obj_id: str):
    return await delete_object(request.app, Equipment, obj_id)


@api_router.get("/enhanced_items", response_model=List[EnhancedItemSchema])
async def get_enhanced_items(name: str = None, type: str = None, subtype: str = None):
    try:
        if name:
            i = ResoluteCache.global_fetch(EnhancedItem, name=name)
            items = [i] if i else []
        else:
            items = ResoluteCache.global_fetch(EnhancedItem)

        if type:
            if type.lower() == "other":
                items = list(
                    filter(lambda i: i.type and i.type.id not in [3, 7, 5, 4], items)
                )
            else:
                items = list(
                    filter(
                        lambda i: i.type and i.type.value.lower() == type.lower(), items
                    )
                )

        if subtype:
            items = list(
                filter(
                    lambda i: (i.subtype and i.subtype.value.lower() == subtype.lower())
                    or (i.subtype_ft and subtype.lower() in i.subtype_ft.lower()),
                    items,
                )
            )
    except Exception as e:
        raise BadRequest(str(e))

    if not items:
        raise NotFound("Enhanced Items not found")

    return items


@admin_api_router.post("/enhanced_items", response_model=EnhancedItemSchema)
async def new_enhanced_item(request: Request, item: EnhancedItemSchema):
    i: EnhancedItem = await create_object(request.app, item, EnhancedItem)

    if i.subtype and i.subtype.parent != i.type.id:
        await delete_object(request.app, EnhancedItem, i.id)
        raise BadRequest("Not a valid subcategory choice for this enhanced item type")

    return i


@admin_api_router.patch("/enhanced_items", response_model=EnhancedItemSchema)
async def update_enhanced_item(request: Request, item: EnhancedItemSchema):
    i = await update_object(request.app, item, EnhancedItem)

    return i


@admin_api_router.delete("/enhanced_items/{obj_id}")
async def delete_enhanced_item(request: Request, obj_id: str):
    return await delete_object(request.app, EnhancedItem, obj_id)


@api_router.get("/powers", response_model=List[PowerSchema])
async def get_powers(
    name: str = None,
    prereq: str = None,
    casttime: str = None,
    range: str = None,
    level: int = None,
):
    try:
        if name:
            p = ResoluteCache.global_fetch(Power, name=name)
            powers = [p] if p else []
        else:
            powers = ResoluteCache.global_fetch(Power)
    except Exception as e:
        raise BadRequest(str(e))

    if not powers:
        raise NotFound("Powers not found")

    return powers


@admin_api_router.post("/powers", response_model=PowerSchema)
async def new_power(request: Request, power: PowerSchema):
    p = await create_object(request.app, power, Power)

    return p


@admin_api_router.patch("/powers", response_model=PowerSchema)
async def update_power(request: Request, power: PowerSchema):
    p = await update_object(request.app, power, Power)

    return p


@admin_api_router.delete("/powers/{obj_id}")
async def delete_power(request: Request, obj_id: str = None):
    return await delete_object(request.app, Power, obj_id)


# --------------------------- #
# Private Methods
# --------------------------- #
async def create_object(app: FastAPI, new_object: BaseModel, model_class: Type) -> Type:
    if not new_object:
        raise BadRequest("No object found")

    db: Session = app.db

    try:
        model_columns = {column.name for column in model_class.__table__.columns}
        raw_data = new_object.model_dump()

        filtered_data = {}
        for k, v in raw_data.items():
            if v is None or v == "":
                continue

            if k in model_columns:
                if isinstance(v, dict) and "id" in v:
                    filtered_data[f"_{k}"] = v["id"]
                else:
                    filtered_data[k] = v

        object = model_class(**filtered_data)
        db.add(object)
        db.flush()
        db.commit()
        app.cache.add_record(model_class, object)
        return object
    except Exception as e:
        db.rollback()
        raise BadRequest(str(e))


async def update_object(
    app: FastAPI, update_object: BaseModel, model_class: Type
) -> Type:

    if not update_object:
        raise BadRequest("No object found")

    db: Session = app.db

    try:
        object_id = getattr(update_object, "id")

        if not object_id:
            raise BadRequest("Missing object identifier")

        object = app.cache.fetch(model_class, object_id, db=db)

        if not object:
            raise NotFound()

        object = db.merge(object)

        model_columns = {column.name for column in model_class.__table__.columns}
        raw_data = update_object.model_dump()
        
        for k, v in raw_data.items():
            if k in model_columns and k not in model_class.__exceptions__:
                if isinstance(v, dict) and "id" in v:
                    setattr(object, f"_{k}", v["id"])
                else:
                    setattr(object, k, v)
        db.commit()
        app.cache.update_record(model_class, object)

        return object
    except Exception as e:
        db.rollback()
        raise BadRequest(str(e))


async def delete_object(
    app: FastAPI, model_class: Type, object_id: Union[int, uuid.UUID, str]
):
    if not object_id:
        raise BadRequest("No object found")

    db: Session = app.db

    try:
        object = app.cache.fetch(model_class, object_id)

        if not object:
            raise NotFound()

        object = db.merge(object)

        db.delete(object)
        db.commit()
        app.cache.remove_record(model_class, object_id)

        return {"message": f"{model_class.__name__} deleted successfully"}
    except Exception as e:
        db.rollback()
        raise BadRequest(str(e))
