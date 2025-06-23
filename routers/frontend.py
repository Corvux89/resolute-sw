

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from models.exceptions import NotFound
from models.resolute import WebContent


frontend_router = APIRouter(
    tags=["Frontend"],
    default_response_class=HTMLResponse
)

templates = Jinja2Templates(directory="templates")

@frontend_router.get('/house_rules')
async def house_rules(request: Request):
    content = request.app.cache.fetch(WebContent, "house_rules")

    if not content:
        raise NotFound("Content not found")
    
    return templates.TemplateResponse("shell.html", {
        "content": content,
        "current_user": 

    }