from typing import List, Type, Union
import uuid
from urllib.parse import unquote
from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2AuthorizationCodeBearer
from sqlalchemy.orm import Session

from constants import AUTH_URL
from helpers.auth_helpers import is_admin
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
async def get_web_content(request: Request, key: str):
    
    content = next((c for c in request.app.cache.fetch(WebContent) if c.key == key), None)

    if not content:
        raise BadRequest("Content not found")
    
    return content

@admin_api_router.patch('/content', response_model=WebContentSchema)
async def update_web_content(request: Request, content: WebContentSchema):
    content = await update_object(request.app, content, WebContent)
    
    return content

@api_router.get('/species', response_model=List[SpeciesSchema])
async def get_species(request: Request,
                      name: str = None,
                      size: str = None):
    species = request.app.cache.fetch(Species)

    try:
      if name:
        species = [next((s for s in species if name.lower() in s.value.lower()), None)]
      elif size:
          species = [next((s for s in species if s.size and size.lower() in s.size.lower()), None)]
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
async def get_classes(request: Request, name: str = None):
    classes = request.app.cache.fetch(PrimaryClass)

    try:
        if name:
            classes = [next((c for c in classes if name.lower() in c.value.lower()), None)]
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

async def update_object(app: FastAPI, update_model: BaseModel, model_class: Type) -> Type:

    if not update_model:
        raise BadRequest("No object found")
    
    db: Session = app.db    
    
    try:
        object_id = getattr(update_model, "id")

        if not object_id:
            raise BadRequest("Missing object identifier")

        object = app.cache.fetch(model_class, object_id, db=db)

        if not object:
            raise NotFound()
        
        object = db.merge(object)

        model_columns = {column.name for column in model_class.__table__.columns}
        raw_data = update_model.model_dump()

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


