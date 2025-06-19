from datetime import datetime
import uuid
import secrets
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.templating import Jinja2Templates
from helpers import get_csp
from routers.api import api
from routers.resolute import resolute


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(SessionMiddleware, secret_key="your-secret-key")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.json_encoders = {
    datetime: lambda v: v.isoformat(),
    uuid.UUID: lambda v: v.hex
}

@app.middleware("http")
async def add_csp(request: Request, call_next):
    csp_nonce = secrets.token_urlsafe(16)
    request.state.csp_nonce = csp_nonce  

    response = await call_next(request)

    csp = get_csp(csp_nonce) 
    # response.headers["Content-Security-Policy"] = csp

    return response

templates = Jinja2Templates(directory="templates")

def csp_nonce(request: Request):
    return request.state.csp_nonce

templates.env.globals["csp_nonce"] = csp_nonce
templates.env.globals["current_user"] = {"is_admin": True}

# app.state.db = ResoluteCache()
# app.state.discord = DiscordBot(app)

@app.get("/debug-static")
async def debug_static():
    return {"static_url": app.url_path_for("static", path="style.css")}

@app.get("/debug-routes")
async def debug_routes():
    return [{"path": route.path, "name": route.name} for route in app.router.routes]

@app.get("/")
async def homepage(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


# app.include_router(auth_router, prefix="/auth")
app.include_router(api, prefix="/api")
app.include_router(resolute, prefix="")

# register_handlers(app)
