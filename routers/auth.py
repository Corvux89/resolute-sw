from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from helpers.auth_helpers import get_discord
from models.auth import User


oauth2_scheme = HTTPBearer()

def get_token(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)) -> str:
    return credentials.credentials

# Router definition
auth_router = APIRouter(
    tags=["Authorization"],
    dependencies=[Depends(get_discord)],
    responses={429: {"description": "Rate limited from discord"}}
)

@auth_router.get('/login')
async def login(request: Request):
    return {"url": request.app.discord.oauth_login_url}

@auth_router.get('/callback')
async def callback(request: Request, code: str):
    token, refresh_token = await request.app.discord.get_access_token(code)
    return {"access_token": token, "refresh_token": refresh_token}

@auth_router.get("/user", response_model=User)
async def get_user(request: Request):
    return await request.app.discord.user(request)