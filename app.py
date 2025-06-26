import uuid

from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import sessionmaker
from constants import (
    DB_URI,
    DISCORD_CLIENT_ID,
    DISCORD_REDIRECT_URI,
    DISCORD_SECRET_KEY,
    SECRET_KEY,
)

from helpers.exceptions import setup_exception_handlers
from models.auth import DiscordBot
from models.cache import ResoluteCache
from models.templates import ResoluteJinja
from routers import api_router, admin_api_router, auth_router, frontend_router

tags_metadata = [
    {"name": "API", "description": "Backend routes that serve up data."},
    {
        "name": "Admin API",
        "description": "Administrative backend routes for modifying data",
    },
    {"name": "Frontend", "description": "These operations server a view"},
    {"name": "Authorization", "description": "Manages app security"},
]

json_encoder = {datetime: lambda v: v.isoformat(), uuid.UUID: lambda v: v.hex}


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = create_engine(DB_URI)
    app.db_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    app.db = app.db_session()

    app.cache = ResoluteCache(app)

    app.discord.initialize()
    yield


def csp_nonce(request: Request):
    return request.state.csp_nonce


app = FastAPI(
    lifespan=lifespan,
    redoc_url=None,
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/swagger",
    title="Resolute Website",
    description="Website for the Resolute SW5E Discord Server",
    version="0.0.1",
    openapi_tags=tags_metadata,
    json_encoder=json_encoder,
)

app.discord: DiscordBot = DiscordBot(
    DISCORD_CLIENT_ID, DISCORD_SECRET_KEY, DISCORD_REDIRECT_URI
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(frontend_router, prefix="")
app.include_router(api_router, prefix="/api")
app.include_router(admin_api_router, prefix="/api")
app.include_router(auth_router, prefix="/auth")
setup_exception_handlers(app)


templates = ResoluteJinja(directory="templates")


# Public routes (no authentication required)
@app.get("/", tags=["Frontend"])
async def homepage(request: Request):
    return await templates.TemplateResponse(
        "home.html",
        {
            "request": request,
        },
    )