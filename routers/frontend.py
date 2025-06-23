

from urllib.parse import unquote
from aiocache import cached
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse

from helpers.auth_helpers import is_beta_tester
from models.exceptions import NotFound
from models.resolute import PrimaryClass, Species, WebContent
from models.templates import ResoluteJinja


frontend_router = APIRouter(
    tags=["Frontend"],
    default_response_class=HTMLResponse,
    dependencies=[Depends(is_beta_tester)]
)

templates = ResoluteJinja(directory="templates")

# Server Content
async def get_web_content(request: Request, key: str):
    content = request.app.cache.fetch(WebContent, key)

    if not content:
        raise NotFound("Content not found")
    
    return await templates.TemplateResponse("/shell.html", {
        "request": request,
        "content": content,
    })

@frontend_router.get('/house_rules')
async def house_rules(request: Request):
    return await get_web_content(request, "house_rules")

@frontend_router.get('/content_rulings')
async def content_rulings(request: Request):
     return await get_web_content(request, "content_rulings")

@frontend_router.get('/errata')
async def errata(request: Request):
     return await get_web_content(request, "errata")

# Characters
@frontend_router.get('/species/')
@frontend_router.get('/species/{species_name}')
async def species(request: Request, species_name: str = None):
    if species_name:
        species = next((s for s in request.app.cache.fetch(Species) if unquote(species_name).lower() == s.value.lower()),None)

        if not Species:
            raise NotFound("Species not found")
        return await templates.TemplateResponse("/species/species.html", 
                                                {
                                                    "request": request,
                                                    "species": species,
                                                 })    
    return await templates.TemplateResponse("/species/species_list.html", {"request": request})

@frontend_router.get('/classes')
@frontend_router.get('/classes/{class_name}')
async def classes(request: Request, class_name: str = None):
    if class_name:
        prim_class = next((c for c in request.app.cache.fetch(PrimaryClass) if unquote(class_name).lower() == c.value.lower()), None)

        if not prim_class:
            raise NotFound("Class not found")
        return await templates.TemplateResponse("/classes/class.html",
                                                {
                                                    "request": request,
                                                    "primary_class": prim_class,
                                                })  
    return await templates.TemplateResponse("/classes/classes_list.html", {"request": request})
