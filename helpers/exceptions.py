from fastapi import FastAPI, Request
from starlette.exceptions import HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from models.exceptions import RateLimited
from models.templates import ResoluteJinja

templates = ResoluteJinja(directory="templates")

async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail}
        )
    
    elif exc.status_code == 302 and (url := exc.headers.get("Location")):
        return RedirectResponse(url=url, status_code=exc.status_code)
    
    return await templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "error": exc.detail,
            "status_code": exc.status_code
        },
        status_code=exc.status_code
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=500,
            content={"error": "Internal Server Error", "detail": str(exc)}
        )
    
    return await templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "error": str(exc),
            "status_code": 500
        },
        status_code=500
    )

async def rate_limit_error_handler(_, e: RateLimited):
    return JSONResponse(
        {"error": "RateLimited", "retry": e.retry_after, "message": e.message},
        status_code=429,
    )    


def setup_exception_handlers(app: FastAPI):
    """Setup custom exception handlers for the app"""
    app.add_exception_handler(Exception, general_exception_handler)
    app.add_exception_handler(RateLimited, rate_limit_error_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)