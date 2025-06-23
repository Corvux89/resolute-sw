import time
import aiohttp

from aiocache import cached
from abc import ABC
from typing import Any, Dict, List, Literal, Optional, Tuple, TypedDict, Union

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from constants import CACHE_TIMEOUT, DISCORD_BOT_TOKEN, DISCORD_GUILD_ID, LIMIT
from models.exceptions import RateLimited

class RefreshTokenPayload(TypedDict):
    client_id: str
    client_secret: str
    grant_type: Literal["refresh_token"]
    refresh_token: str

class TokenGrantPayload(TypedDict):
    client_id: str
    client_secret: str
    grant_type: Literal["authorization_code"]
    code: str
    redirect_uri: str

class TokenResponse(TypedDict):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    scope: str

class ObjectCache(TypedDict):
    objects: Optional[list] = None
    timestamp: Optional[float] = 0



PAYLOAD = Union[TokenGrantPayload, RefreshTokenPayload]

def _tokens(resp: TokenResponse) -> Tuple[str, str]:
    access_token, refresh_token = resp.get("access_token"), resp.get("refresh_token")
    if access_token is None or refresh_token is None:
        raise Exception("Tokens can't be None")
    return access_token, refresh_token

class User(BaseModel):
    id: str
    username: str
    global_name: Optional[str] = None
    avatar: Optional[str]
    avatar_url: Optional[str] = None

    def __init__(self, **data: Any):
        super().__init__(**data)
        
        if self.avatar:
            self.avatar_url = f"https://cdn.discordapp.com/avatars/{self.id}/{self.avatar}.png"
        else:
            self.avatar_url = "https://cdn.discordapp.com/embed/avatars/1.png"

class Guild(BaseModel):
    id: str
    name: str
    icon: Optional[str] = None

class Role(BaseModel):
    id: str
    name: str

class Member(BaseModel):
    user: Optional[User] = None
    nick: Optional[str] = None
    roles: List[str]

class DiscordBot(ABC):
    _base_url = "https://discordapp.com/api"
    _auth_url = "https://discord.com/api/oauth2"

    client_id: str
    client_secret: str
    redirect_uri: str
    scopes: [str] = ["identify", "guilds", "email"]
    proxy: Optional[str]
    proxy_auth: Optional[str]
    client_session: Optional[aiohttp.ClientSession] = None

    _channels: ObjectCache = {}
    _roles: ObjectCache = {}
    _members: ObjectCache = {}

    def __init__(self, client_id, client_secret, redirect_uri, **kwargs):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scopes = "%20".join(kwargs.get('scopes', ["identify", "guilds", "email"]))
        self.proxy = kwargs.get('proxy')
        self.proxy_auth = kwargs.get('proxy_auth')

    def initialize(self):
        if self.client_session:
            return
        self.client_session = aiohttp.ClientSession()

    def get_oauth_login_url(self, state: Optional[str] = None):
        client_id = f"client_id={self.client_id}"
        redirect_uri = f"redirect_uri={self.redirect_uri}"
        scopes = f"scope={self.scopes}"
        response_type = "response_type=code"
        state = f"&state={state}" if state else ''

        return f"{self._auth_url}/authorize?{client_id}&{redirect_uri}&{scopes}&{response_type}{state}"
    
    oauth_login_url = property(get_oauth_login_url)
    
    @property
    def token_url(self):
        return f"{self._auth_url}/token"

    async def get_token_response(self, payload: PAYLOAD) -> TokenResponse:
        if self.client_session is None:
            raise Exception("Client Session not initialized")
        
        async with self.client_session.post(
            f"{self.token_url}",
            data=payload,
            proxy=self.proxy,
            proxy_auth=self.proxy_auth
        ) as response:
            test = await response.text()
            return await response.json()

    async def get_access_token(self, code: str) -> Tuple[str, str]:
        payload: TokenGrantPayload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri
        }

        resp = await self.get_token_response(payload)
        return _tokens(resp)
    
    async def refresh_access_token(self, refresh_token: str) -> Tuple[str, str]:
        payload: RefreshTokenPayload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        resp = await self.get_token_response(payload)
        return _tokens(resp)
    
    @cached(ttl=550)
    async def request(self, route: str, token: Optional[str] = None, method: Literal["GET", "POST"] = "GET"):
        if self.client_session is None:
            raise Exception("Client Session not initialized")
        headers: Dict = {}
        if token:
            headers = {"Authorization": f"Bearer {token}"}
        if method == "GET":
            async with self.client_session.get(
                f"{self._base_url}{route}",
                headers=headers,
                proxy=self.proxy,
                proxy_auth=self.proxy_auth,
            ) as resp:
                data = await resp.json()
        elif method == "POST":
            async with self.client_session.post(
                f"{self._base_url}{route}",
                headers=headers,
                proxy=self.proxy,
                proxy_auth=self.proxy_auth,
            ) as resp:
                data = await resp.json()
        else:
            raise Exception("Other HTTP than GET and POST are currently not Supported")
        if resp.status == 401:
            raise Exception("Unauthorized")
        if resp.status == 429:
            raise RateLimited(data, resp.headers)
        return data
    
    @cached(ttl=550)
    async def bot_request(self, route: str, method: Literal["GET", "POST", "PATCH", "PUT"] = "GET", **kwargs):
        if self.client_session is None:
            raise Exception("Client Session not initialized")
        headers: Dict = {"Authorization": f"Bot {DISCORD_BOT_TOKEN}"}
        if method == "GET":
            async with self.client_session.get(
                f"{self._base_url}{route}",
                headers=headers,
                proxy=self.proxy,
                proxy_auth=self.proxy_auth,
            ) as resp:
                data = await resp.json()
        elif method == "POST":
            async with self.client_session.post(
                f"{self._base_url}{route}",
                headers=headers,
                proxy=self.proxy,
                proxy_auth=self.proxy_auth,
            ) as resp:
                data = await resp.json()
        else:
            raise Exception("Other HTTP than GET and POST are currently not Supported")
        if resp.status == 401:
            raise Exception("Unauthorized")
        if resp.status == 429:
            raise RateLimited(data, resp.headers)
        return data
    
    async def user(self, request: Request):
        if "identify" not in self.scopes:
            raise Exception("Missing identify scope")
        route = "/users/@me"
        token = self.get_token(request)
        return User(**(await self.request(route, token)))
    
    async def isAuthenticated(self, token: str):
        route = "/oauth2/@me"
        try:
            await self.request(route, token)
            return True
        except:
            return False

    async def requires_authorization(self, bearer: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer())):
        if bearer is None:
            raise Exception("Unauthorized")
        if not await self.isAuthenticated(bearer.credentials):
            raise Exception("Unathorized")
        
    def get_token(self, request: Request):
        authorization_header = request.headers.get("Authorization")
        if not authorization_header:
            raise Exception("Unathorized")
        authorization_header = authorization_header.split(" ")
        if not authorization_header[0] == "Bearer" or len(authorization_header) > 2:
            raise Exception("Unathorized")

        token = authorization_header[1]
        return token
    
    async def fetch_members(self, member_id: str = None) -> Union[Optional[Member], List[Member]]:
        current_time = time.time()

        if not self._members.get('objects') or (
            current_time - self._members.get('timestamp', 0) > CACHE_TIMEOUT
        ):
            members = [Member(**m) for m in await self.bot_request(f"/guilds/{DISCORD_GUILD_ID}/members?limit={LIMIT}")]

            self._members["objects"] = members
            self._members["timestamp"] = current_time

        
        if member_id:
            return next((m for m in self._members["objects"] if m.user and m.user.id == member_id), None)
        
        return self._members["objects"]
    
    async def fetch_roles(self, role_id: str = None, **kwargs) -> Union[Optional[Role], List[Role]]:
        current_time = time.time()

        if not self._roles["objects"] or (
            current_time - self._roles.get('timestamp', 0) > CACHE_TIMEOUT
        ):
            roles = [Role(*r) for r in await self.bot_request(f"/guilds/{DISCORD_GUILD_ID}/roles")]
            self._roles["objects"] = roles
            self._roles["timestamp"] = current_time

        if role_id:
            return next((r for r in self._roles["objects"] if r.id == role_id), None)
        
        elif kwargs.get('name'):
            return next((r for r in self._roles["objects"] if r.name == kwargs.get('name')), None)
        
        return self._roles["objects"]


    
 


        


