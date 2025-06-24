

from urllib.parse import unquote
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse

from helpers.auth_helpers import is_beta_tester
from models.exceptions import NotFound
from models.resolute import *
from models.templates import ResoluteJinja, build_select_option


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
        species = request.app.cache.fetch(Species, value=unquote(species_name))

        if not Species:
            raise NotFound("Species not found")
        return await templates.TemplateResponse("/species/species.html", 
                                                {
                                                    "request": request,
                                                    "species": species,
                                                 })    
    
    # species_list = request.app.cache.get_model(Species, SpeciesSchema)
    species_list = request.app.cache.fetch(SpeciesSchema)
    return await templates.TemplateResponse("/species/species_list.html", 
                                            {"request": request, 
                                             "table": species_list})

@frontend_router.get('/classes')
@frontend_router.get('/classes/{class_name}')
async def classes(request: Request, class_name: str = None):
    if class_name:
        prim_class = request.app.cache.fetch(PrimaryClass, value=unquote(class_name))

        if not prim_class:
            raise NotFound("Class not found")
        return await templates.TemplateResponse("/classes/class.html",
                                                {
                                                    "request": request,
                                                    "primary_class": prim_class,
                                                })
    
    class_list = request.app.cache.fetch(PrimaryClassSchema)
    return await templates.TemplateResponse("/classes/classes_list.html", 
                                            {
                                                "request": request,
                                                "table": class_list
                                                })

@frontend_router.get('/archetypes')
@frontend_router.get('/archetypes/{arch_name}')
async def archetypes(request: Request, arch_name: str = None):
    options = {}
    class_options = build_select_option(request.app.cache.fetch(PrimaryClass))
    options["classes"] = class_options
    

    if arch_name:
        archetype = request.app.cache.fetch(Archetype, value=arch_name)

        if not archetype:
            raise NotFound("Archetype not found")
        
        return await templates.TemplateResponse("/archetypes/archetype.html",
                                                {
                                                    "request": request,
                                                    "archetype": archetype,

                                                }, options=options)
    
    archetype_list = request.app.cache.fetch(ArchetypeSchema)
    return await templates.TemplateResponse("/archetypes/archetype_list.html",
                                            {
                                                "request": request,
                                                "table": archetype_list
                                            }, options=options)

@frontend_router.get('/backgrounds')
@frontend_router.get('/backgrounds/{back_name}')
async def backgrounds(request: Request, back_name: str = None):
    if back_name:
        background = request.app.cache.fetch(Background, name=back_name)

        if not background:
            raise NotFound("Background not found")
        
        return await templates.TemplateResponse("/backgrounds/background.html",
                                                {
                                                    "request": request,
                                                    "background": background
                                                })
    
    background_list = request.app.cache.fetch(BackgroundSchema)
    if not background_list:
        # This will happen the first time, but not too often
        request.app.cache.update(request.app.db, Background)
        background_list = request.app.cache.fetch(BackgroundSchema)
    return await templates.TemplateResponse("/backgrounds/background_list.html",
                                            {
                                                "request": request,
                                                "table": background_list
                                            })

@frontend_router.get('/features')
async def features(request: Request):
    feature_list = request.app.cache.fetch(FeatureSchema)

    return await templates.TemplateResponse("/feats.html",
                                            {
                                                "request": request,
                                                "table": feature_list
                                            })
