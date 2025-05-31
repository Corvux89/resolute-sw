import typing
import time
import json

from abc import ABC

from flask import Flask, current_app, session
from requests import request

from constants import CACHE_TIMEOUT, DISCORD_GUILD_ID, LIMIT
from models.exceptions import UnauthorizedAccessError
from models.general import BaseModel, IntAttributeMixin, User


class MemberAttributeMixin:
    def get_member_attribute(self, member_id: str):
        member = current_app.discord.fetch_members(member_id)
        
        if member:
            return member.__dict__        
        return None


class DiscordGuild(BaseModel, IntAttributeMixin):
    _id: str = None
    name: str = None
    icon: str = None

    @property
    def id(self):
        return str(self._id)

    @id.setter
    def id(self, value):
        self.set_int_attribute("_id", value)


class DiscordUser(BaseModel, IntAttributeMixin):
    global_name: str = None
    _id: int = None
    username: str = None
    avatar: str = None

    guilds = None

    @property
    def id(self):
        return str(self._id)

    @id.setter
    def id(self, value):
        self.set_int_attribute("_id", value)


class DiscordChannel(BaseModel, IntAttributeMixin):
    _id: int = None
    name: str = None
    _parent_id: int = None
    type: int = None

    @property
    def id(self):
        return str(self._id)

    @id.setter
    def id(self, value):
        self.set_int_attribute("_id", value)

    @property
    def parent_id(self):
        return str(self._parent_id)

    @parent_id.setter
    def parent_id(self, value):
        self.set_int_attribute("_parent_id", value)


class DiscordRole(BaseModel, IntAttributeMixin):
    _id: int = None
    name: str = None

    @property
    def id(self):
        return str(self._id)

    @id.setter
    def id(self, value):
        self.set_int_attribute("_id", value)

class DiscordMember:
    nick: str = None
    roles: list[str] = None
    user: DiscordUser = None
    bot: bool = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.__annotations__:
                if key == "user" and isinstance(value, dict):
                    setattr(self, key, DiscordUser(**value))
                else:
                    setattr(self, key, value)

    def to_dict(self):
        result = {}
        for attr in dir(self):
            if attr.startswith("_") or callable(getattr(self, attr)):
                continue
            try:
                value = getattr(self, attr)
                if isinstance(value, DiscordUser):
                    result[attr] = value.to_dict()
                else:
                    result[attr] = value
            except AttributeError:
                continue
        return result

    @property
    def member_display_name(self):
        return (
            self.nick
            or self.user.global_name
            or self.user.username
            or "Player not found"
        )


class DiscordBot(ABC):
    base_url = "https://discordapp.com/api"

    _channels = {"channels": None, "timestamp": 0}

    _roles = {"roles": None, "timestamp": 0}

    _members = {"members": None, "timestamp": 0}

    def __init__(self, app: Flask):
        self.client_id = app.config["DISCORD_CLIENT_ID"]
        self.bot_token = app.config["DISCORD_BOT_TOKEN"]

        self.retries = app.config.get("DISCORD_RETRIES", 5)

        self.user_cache = {}

    def request(self, route: str, method="GET", **kwargs) -> typing.Union[dict, str]:
        headers = {"Authorization": f"Bot {self.bot_token}"}

        url = f"{self.base_url}{route}"

        for attempt in range(self.retries):
            response = request(method, url, headers=headers, **kwargs)

            if response.status_code == 401:
                raise UnauthorizedAccessError()
            elif response.status_code == 429:
                retry_after = response.headers.get("Retry-After", 2**attempt)
                time.sleep(float(retry_after))
            else:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    return response.text

        raise Exception("Max retries exceeded")

    def user_request(
        self, token, route, method="GET", **kwargs
    ) -> typing.Union[dict, str]:
        headers = {"Authorization": f"Bearer {token}"}

        url = f"{self.base_url}{route}"

        for attempt in range(self.retries):
            response = request(method, url, headers=headers, **kwargs)

            if response.status_code == 401:
                raise UnauthorizedAccessError()
            elif response.status_code == 429:
                retry_after = response.headers.get("Retry-After", 2**attempt)
                time.sleep(float(retry_after))
            else:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    return response.text()

        raise Exception("Max retries exceeded")

    @staticmethod
    def fetch_user() -> User:
        if not (user := current_app.discord.user_cache.get(session.get("USER_ID"))):
            user = User.fetch_user("discord")
            current_app.discord.user_cache.update({user.id: user})

        return user

    def fetch_channels(
        self, channel_id: str = None
    ) -> typing.Union[DiscordChannel, list[DiscordChannel]]:
        current_time = time.time()

        if not self._channels.get("channels") or (
            current_time - self._channels.get("timestamp", 0) > CACHE_TIMEOUT
        ):
            channels = self.request(f"/guilds/{DISCORD_GUILD_ID}/channels")
            self._channels["channels"] = [DiscordChannel(**c) for c in channels]
            self._channels["timestamp"] = current_time

        if channel_id:
            return next(
                (c for c in self._channels.get("channels") if c.id == channel_id), None
            )

        return self._channels.get("channels", [])

    def fetch_roles(
        self, role_id: str = None, **kwargs
    ) -> typing.Union[DiscordRole, list[DiscordRole]]:
        current_time = time.time()

        if not self._roles.get("roles") or (
            current_time - self._roles.get("timestamp", 0) > CACHE_TIMEOUT
        ):
            roles = self.request(f"/guilds/{DISCORD_GUILD_ID}/roles")
            self._roles["roles"] = [DiscordRole(**r) for r in roles]
            self._roles["timestamp"] = current_time

        if role_id:
            return next((r for r in self._roles.get("roles") if r.id == role_id), None)
        
        elif kwargs.get('name'):
            return next((r for r in self._roles.get("roles") if r.name == kwargs.get('name')), None)

        return self._roles.get("roles", [])
    
    def fetch_members(
            self, member_id: str = None
    ) -> typing.Union[typing.Optional[DiscordMember], list[DiscordMember]]:
        current_time = time.time()

        if not self._members.get('members') or (
            current_time - self._roles.get('timestamp',0) > CACHE_TIMEOUT
        ):
            members = self.request(
            f"/guilds/{DISCORD_GUILD_ID}/members?limit={LIMIT}"
        )
            
            self._members["members"] = [DiscordMember(**m) for m in members]
            self._members["timestamp"] = current_time

        if member_id:
            return next((m for m in self._members.get('members') if m.user and m.user.id == member_id), None)
        
        return self._members.get('members', [])

        
