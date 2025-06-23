

from typing import List
from urllib.parse import unquote
from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2AuthorizationCodeBearer
from sqlalchemy.orm import Session

from constants import AUTH_URL
from helpers.auth_helpers import is_admin
from models.exceptions import BadRequest, NotFound
from models.general import HTTPError, custom_encoder
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
                                 "description": "Malformed or bad request from the client"}
                           }
                        )

admin_api_router = APIRouter(tags=["API"],
                             default_response_class=JSONResponse,
                             responses={                           
                                400: {"model": HTTPError,
                                        "description": "Malformed or bad request from the client"}
                                },
                            dependencies=[Depends(oauth), Depends(is_admin)]
                            )



@api_router.get('/content', response_model=WebContentFullSchema)
async def get_web_content(request: Request, key: str):
    
    content = next((c for c in request.app.cache.fetch(WebContent) if c.key == key), None)

    if not content:
        raise BadRequest("Content not found")
    
    return custom_encoder(content)

@admin_api_router.patch('/content', response_model=WebContentSchema)
async def update_web_content(request: Request, content: WebContentSchema):
    content = await update_object(request.app, content, WebContent,
                            ["content", "title"])
    
    return custom_encoder(content)

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
    
    return custom_encoder(species)

# --------------------------- #
# Private Methods
# --------------------------- #
def filter_objects(request: Request, objects: [], filter_map: {}) -> []:
    for arg, filter_func in filter_map.items():
        if raw_value := request.query_params.get(arg):
            value = unquote(raw_value)
            objects = [p for p in objects if filter_func(p, value)]

    return objects

async def update_object(app: FastAPI, update_model: BaseModel, model_class: Type, fields: [] = [], fk_fields: [] = []) -> Type:
    all_fields = fields + fk_fields

    if not update_model:
        raise BadRequest("No request found")
    
    db: Session = app.db    
    
    try:
        object_id = getattr(update_model, "id")

        if not object_id:
            raise BadRequest("Missing object identifier")

        object = app.cache.fetch(model_class, object_id, db=db)

        if not object:
            raise NotFound()
        
        object = db.merge(object)

        for field in all_fields:
            if hasattr(update_model, field):
                if field in fields:
                    setattr(object, field, getattr(update_model, field))
                elif field in fk_fields:
                    setattr(object, f"_{field}", getattr(update_model, field))
        
        db.commit()

        if app.cache.contains(model_class):
            app.cache.update(db, model_class)
                    
        return object
    except Exception as e:
        db.rollback()
        raise BadRequest(str(e))