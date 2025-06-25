from typing import List, Type, Union
import uuid
from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2AuthorizationCodeBearer
from sqlalchemy.orm import Session

from constants import AUTH_URL
from helpers.auth_helpers import is_admin
from models.cache import ResoluteCache
from models.exceptions import BadRequest, NotFound
from models.general import HTTPError
from models.resolute import *

# Doing this mostly for Swagger
oauth = OAuth2AuthorizationCodeBearer(AUTH_URL,
                                      "https://discord.com/api/oauth2/token",
                                      scopes={
                                            "identify": "Access to basic user information (username, discriminator, avatar)",
                                            "guilds": "Access to the list of guilds the user is a member of",
                                            "email": "Access to the user's email address"
                                        })



api_router = APIRouter(tags=["API"], 
                       default_response_class=JSONResponse,
                       responses={                           
                           400: {"model": HTTPError,
                                 "description": "Malformed or bad request from the client"},
                           401: {"description": "Authentication required"}
                           }
                        )

# Admin API routes - requires admin privileges
admin_api_router = APIRouter(tags=["Admin API"],
                             default_response_class=JSONResponse,
                             responses={                           
                                400: {"model": HTTPError,
                                        "description": "Malformed or bad request from the client"},
                                401: {"description": "Authentication required"},
                                403: {"description": "Admin privileges required"}
                                },
                            dependencies=[Depends(is_admin)]
                            )



@api_router.get('/content', response_model=WebContentFullSchema)
async def get_web_content(key: str):
    content = ResoluteCache.global_fetch(WebContent, key)

    if not content:
        raise BadRequest("Content not found")
    
    return content

@admin_api_router.patch('/content', response_model=WebContentSchema)
async def update_web_content(request: Request, content: WebContentSchema):
    content = await update_object(request.app, content, WebContent)
    
    return content

@api_router.get('/species', response_model=List[SpeciesSchema])
async def get_species(name: str = None,
                      size: str = None):
    try:
      if name:
        s = ResoluteCache.global_fetch(Species, value=name)
        species = [s] if s else []
      elif size:
          species = list(filter(lambda s: s.size and size.lower() in s.size.lower(), species))
      else:
          species = ResoluteCache.global_fetch(Species)
    except Exception as e:
        raise BadRequest(str(e))
    
    if not species:
        raise NotFound("Species not found")
    
    return species

@admin_api_router.post('/species', response_model=SpeciesSchema)
async def new_species(request: Request, species: SpeciesSchema):
    species = await create_object(request.app, species, Species)

    return species

@admin_api_router.patch('/species', response_model=SpeciesSchema)
async def update_species(request: Request, species: SpeciesSchema):
    species = await update_object(request.app, species, Species)
    
    return species

@admin_api_router.delete('/species/{obj_id}')
async def delete_species(request: Request, obj_id: int):
    return await delete_object(request.app, Species, obj_id)

@api_router.get('/classes', response_model=List[PrimaryClassSchema])
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

@admin_api_router.post('/classes', response_model=PrimaryClassSchema)
async def new_class(request: Request, primary_class: PrimaryClassSchema):
    primary_class = await create_object(request.app, primary_class, PrimaryClass)
    
    return primary_class

@admin_api_router.patch('/classes', response_model=PrimaryClassSchema)
async def update_class(request: Request, primary_class: PrimaryClassSchema):
    primary_class = await update_object(request.app, primary_class, PrimaryClass)
    
    return primary_class

@admin_api_router.delete('/classes/{obj_id}')
async def delete_class(request: Request, obj_id: int):
    return await delete_object(request.app, PrimaryClass, obj_id)

@api_router.get('/archetypes', response_model=List[ArchetypeSchema])
def get_archetypes(name: str = None, parent_class: str = None, caster_type: str = None):

    try:
        if name:
            a = ResoluteCache.global_fetch(Archetype, value=name)
            archetypes = [a] if a else []
        else:
            archetypes = ResoluteCache.global_fetch(Archetype)
        
        if parent_class:
            archetypes = list(filter(lambda c: c.parent_name and parent_class.lower() in c.parent_name.lower(), archetypes))

        if caster_type:
            archetypes = list(filter(lambda a: a.caster_type and caster_type.lower() in a.caster_type.value.lower(), archetypes))
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
    return await delete_object(request.app, Archetype, obj_id)

@api_router.get('/backgrounds', response_model=List[BackgroundSchema])
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

@admin_api_router.post('/backgrounds', response_model=BackgroundSchema)
async def new_background(request: Request, back: BackgroundSchema):
    background = await create_object(request.app, back, Background)

    return background

@admin_api_router.patch('/backgrounds', response_model=BackgroundSchema)
async def update_background(request: Request, back: BackgroundSchema):
    background = await update_object(request.app, back, Background)

    return background

@admin_api_router.delete('/backgrounds/{obj_id}')
async def delete_background(request: Request, obj_id: str):
    return await delete_object(request.app, Background, obj_id)

@api_router.get('/features', response_model=List[FeatureSchema])
async def get_features(name: str = None):
    try:
        if name:
            f = ResoluteCache.global_fetch(Feature, name=name)
            features = [f] if f else []
        else:
            features = ResoluteCache.global_fetch(Feature)
    except Exception as e:
        raise BadRequest(str(e))
    
    if not features:
        raise NotFound("Features not found")
    
    return features

@admin_api_router.post('/features', response_model=FeatureSchema)
async def new_feature(request: Request, feat: FeatureSchema):
    feature = await create_object(request.app, feat, Feature)

    return feature

@admin_api_router.patch('/features', response_model=FeatureSchema)
async def update_feature(request: Request, feat: FeatureSchema):
    feature = await update_object(request.app, feat, Feature)

    return feature

@admin_api_router.delete('/features/{obj_id}')
async def delete_feature(request: Request, obj_id: str):
    return await delete_object(request.app, Feature, obj_id)

@api_router.get('/maneuvers', response_model=List[ManeuverSchema])
async def get_maneuvers(name: str = None, type: str = None):
    try:
        if name:
            m = ResoluteCache.global_fetch(Maneuver, name=name)
            maneuvers = [m] if m else []
        else:
            maneuvers = ResoluteCache.global_fetch(Maneuver)

        if type:
            maneuvers = list(filter(lambda m: m.type and m.type.value.lower() == type.lower()), maneuvers)
    except Exception as e:
        raise BadRequest(str(e))
    
    if not maneuvers:
        raise NotFound("Maneuvers not found")
    
    return maneuvers

@admin_api_router.post('/maneuvers', response_model=ManeuverSchema)
async def new_maneuver(request: Request, man: ManeuverSchema):
    maneuver = await create_object(request.app, man, Maneuver)

    return maneuver

@admin_api_router.patch('/maneuvers', response_model=ManeuverSchema)
async def udpate_maneuver(request: Request, man: ManeuverSchema):
    maneuver = await update_object(request.app, man, Maneuver)

    return maneuver

@admin_api_router.delete('/maneuvers/{obj_id}')
async def delete_maneuver(request: Request, obj_id: str):
    await delete_object(request.app, Maneuver, obj_id)

@api_router.get('/customizations', response_model=List[CustomizationSchema])
async def get_customizations(name: str = None, type: str = None):
    try:
        if name:
            c = ResoluteCache.global_fetch(Customization, name=name)
            customizations = [c] if c else []
        else:
            customizations = ResoluteCache.global_fetch(Customization)

        if type:
            customizations = list(filter(lambda c: c.type and type.lower() == c.type.value.lower(), customizations))
    except Exception as e:
        raise BadRequest(str(e))
    
    if not customizations:
        raise NotFound("Customizations not found")
    
    return customizations

@admin_api_router.post('/customizations', response_model=CustomizationSchema)
async def new_customization(request: Request, custom: CustomizationSchema):
    customization = await create_object(request.app, custom, Customization)

    return customization

@admin_api_router.patch('/customizations', response_model=CustomizationSchema)
async def update_customization(request: Request, custom: CustomizationSchema):
    customization = await update_object(request.app, custom, Customization)

    return customization

@admin_api_router.delete('/customizations/{obj_id}')
async def delete_customization(request: Request, obj_id: str):
    return await delete_object(request.app, Customization, obj_id)

@api_router.get('/improvements', response_model=List[ImprovementSchema])
async def get_improvements(name: str = None, type: str = None):
    try:
        if name:
            i = ResoluteCache.global_fetch(Improvement, name=name)
            improvements = [i] if i else []
        else:
            improvements = ResoluteCache.global_fetch(Improvement)

        if type:
            improvements = list(filter(lambda i: i.type and type.lower() == i.type.value.lower(), improvements))
    except Exception as e:
        raise BadRequest(str(e))
    
    if not improvements:
        raise NotFound("Improvements not found")
    
    return improvements

@admin_api_router.post('/improvements', response_model=ImprovementSchema)
async def new_improvement(request: Request, imp: ImprovementSchema):
    improvement = await create_object(request.app, imp, Improvement)

    return improvement

@admin_api_router.patch('/improvements', response_model=ImprovementSchema)
async def update_improvement(request: Request, imp: ImprovementSchema):
    improvement = await update_object(request.app, imp, Improvement)

    return improvement

@admin_api_router.delete('/improvements/{obj_id}')
async def delete_improvement(request: Request, obj_id: str):
    return await delete_object(request.app, Improvement, obj_id)


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
            if v is None or v == '':
                continue
                  
            if k in model_columns:                
                if isinstance(v, dict) and 'id' in v:
                    filtered_data[f"_{k}"] = v['id']
                else:
                    filtered_data[k] = v
        
        object = model_class(**filtered_data)
        db.add(object)
        db.flush()  
        db.commit()
        app.cache.update(db, model_class)
        return object
    except Exception as e:
        db.rollback()
        raise BadRequest(str(e))

async def update_object(app: FastAPI, update_object: BaseModel, model_class: Type) -> Type:

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
                if isinstance(v, dict) and 'id' in v:
                    setattr(object, f"_{k}", v['id'])
                else:
                    setattr(object, k, v)
        db.commit()
        app.cache.update(db, model_class)
                    
        return object
    except Exception as e:
        db.rollback()
        raise BadRequest(str(e))
    
async def delete_object(app: FastAPI, model_class: Type, object_id: Union[int, uuid.UUID, str]):
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
        app.cache.update(db, model_class)

        return {"message": f"{model_class.__name__} deleted successfully"}
    except Exception as e:
        db.rollback()
        raise BadRequest(str(e))


