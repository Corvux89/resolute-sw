from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from urllib.parse import unquote

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


@auth_router.get('/callback')
async def callback(request: Request, code: str, state: str = None):
    token, refresh_token = await request.app.discord.get_access_token(code)
    
    redirect_url = "/"  
    if state:
        try:
            redirect_url = unquote(state)
        except:
            redirect_url = "/"
    
    response = RedirectResponse(url=redirect_url, status_code=302)
    

    jwt_token = request.app.discord.encode_tokens_to_jwt(token, refresh_token)
    

    response.set_cookie(
        key="auth_token",
        value=jwt_token,
        max_age=3600 * 24 * 7,  # 7 days 
        httponly=True,  
        secure=True,    
        samesite="lax"  
    )
    
    return response

@auth_router.get("/user", response_model=User)
async def get_user(request: Request):
    return await request.app.discord.user(request)

@auth_router.get('/login')
async def login(request: Request, return_to: str = None):
    """
    Initiate Discord OAuth login with optional return URL
    """
    state = return_to if return_to else str(request.headers.get("referer", "/"))
    login_url = request.app.discord.get_oauth_login_url(state=state)
    return RedirectResponse(url=login_url, status_code=302)

@auth_router.get('/logout')
async def logout(request: Request, return_to: str = "/"):
    """
    Logout user by clearing cookies and redirecting
    """
    response = RedirectResponse(url=return_to, status_code=302)
    
    # Clear JWT authentication cookie
    response.delete_cookie("auth_token")
    
    return response