from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from models.exceptions import (
    BadRequest,
    NotFound,
    AdminAccessError,
    UnauthorizedAccessError,
    UnderConstruction,
)

templates = Jinja2Templates(directory="templates")


async def not_found_handler(request: Request, exc: NotFound):
    if "/api/" in str(request.url.path):
        return JSONResponse(status_code=404, content={"error": exc.message or "URL not found"})
    return templates.TemplateResponse("/exceptions/404.html", {"request": request})


async def unauthorized_error_handler(request: Request, exc: UnauthorizedAccessError):
    return JSONResponse(status_code=401, content={"error": exc.message})


async def exception_error_handler(request: Request, exc: AdminAccessError):
    return JSONResponse(status_code=403, content={"error": exc.message})


async def bad_request_handler(request: Request, exc: BadRequest):
    return JSONResponse(status_code=400, content={"error": exc.message})


async def general_error_handler(request: Request, exc: Exception):
    if "/api/" in str(request.url.path):
        return JSONResponse(status_code=500, content={"error": str(exc)})
    return templates.TemplateResponse("home.html", {"request": request, "error": str(exc)})


async def under_construction_handler(request: Request, exc: UnderConstruction):
    return templates.TemplateResponse("/exceptions/temp.html", {"request": request})


def register_handlers(app):
    app.add_exception_handler(NotFound, not_found_handler)
    app.add_exception_handler(UnauthorizedAccessError, unauthorized_error_handler)
    app.add_exception_handler(AdminAccessError, exception_error_handler)
    app.add_exception_handler(BadRequest, bad_request_handler)
    app.add_exception_handler(Exception, general_error_handler)
    app.add_exception_handler(UnderConstruction, under_construction_handler)
