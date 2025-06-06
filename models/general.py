import datetime
import json
import uuid
import markdown
from flask import current_app, session
from flask.json.provider import JSONProvider
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
import requests
from sqlalchemy import inspect
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm.decl_api import registry
from constants import DISCORD_ADMINS, DISCORD_GUILD_ID
from models.exceptions import UnauthorizedAccessError

db = SQLAlchemy()

def render_markdown(text: str) -> str:
    if not text:
        return ""
    return markdown.markdown(text, extensions=["tables", "sane_lists", "toc"])

class User(UserMixin):
    id: str
    username: str
    global_name: str
    email: str
    avatar: str = None

    guilds = None

    def __init__(self, id, email, username, global_name, **kwargs):
        self.id = id
        self.email = email
        self.username = username
        self.global_name = global_name
        self.avatar = kwargs.get("avatar")

    @property
    def is_admin(self):
        from models.G0T0 import G0T0Guild
        from models.discord import DiscordMember
        db: SQLAlchemy = current_app.config.get("DB")
        guild = db.session.query(G0T0Guild).filter(G0T0Guild._id == DISCORD_GUILD_ID).first()
        member: DiscordMember = current_app.discord.fetch_members(self.id)
        admin_role = current_app.discord.fetch_roles(guild.admin_role)        

        return str(self.id) in set(str(admin) for admin in DISCORD_ADMINS) or admin_role.id in member.roles
    
    @property
    def is_beta_tester(self):
        from models.discord import DiscordMember
        member: DiscordMember = current_app.discord.fetch_members(self.id)
        
        if beta_role := current_app.discord.fetch_roles(name="Beta Testing"):   
            return beta_role.id in member.roles or self.is_admin
        return False
        

    @property
    def avatar_url(self):
        return (
            f"https://cdn.discordapp.com/avatars/{self.id}/{self.avatar}.png"
            if self.avatar
            else None
        )

    @classmethod
    def fetch_user(cls, provider: str):
        provider_data = current_app.config["OAUTH2_PROVIDERS"].get(provider)

        response = requests.get(
            provider_data["userinfo"]["url"],
            headers={
                "Authorization": f"Bearer {session['OAUTH2_TOKEN']}",
                "Accept": "application/json",
            },
        )

        if response.status_code != 200:
            raise UnauthorizedAccessError()

        user_data = response.json()
        session["USER_ID"] = provider_data["userinfo"]["id"](user_data)

        user = cls(
            id=session["USER_ID"],
            email=provider_data["userinfo"]["email"](user_data),
            username=provider_data["userinfo"]["username"](user_data),
            global_name=provider_data["userinfo"]["global_name"](user_data),
            avatar=provider_data["userinfo"]["avatar"](user_data),
        )

        return user


class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, uuid.UUID):
            return obj.hex
        elif hasattr(obj, "to_dict"):
            return obj.to_dict()
        elif hasattr(obj, "to_json"):
            return obj.to_json()
        return json.JSONEncoder.default(self, obj)


class CustomJSONProvider(JSONProvider):
    def dumps(self, obj, **kwargs):
        return json.dumps(obj, **kwargs, cls=AlchemyEncoder)

    def loads(self, s: str | bytes, **kwargs):
        return json.loads(s, **kwargs)


class BaseModel:
    def __init__(self, **kwargs):
        for key in kwargs:
            if hasattr(self, key):
                setattr(self, key, kwargs[key])

    def to_dict(self):
        result = {}
        for attr in dir(self):
            if attr.startswith("_") or callable(getattr(self, attr)):
                continue
            try:
                value = getattr(self, attr)

                if hasattr(value, "to_dict"):
                    result[attr] = value.to_dict()

                elif inspect(value, raiseerr=False) is not None or isinstance(
                    value, registry
                ):
                    continue

                elif isinstance(value, datetime.datetime):
                    result[attr] = value.isoformat()

                elif value == "None":
                    result[attr] = ""
                else:
                    result[attr] = value
            except AttributeError:
                continue
        return result


class IntAttributeMixin:
    def set_int_attribute(self, attr_name, value):
        try:
            setattr(self, attr_name, value)
        except (ValueError, TypeError):
            setattr(self, attr_name, None)

class Content(db.Model):
    __tablename__ = "web_content"
    key: Mapped[str] = mapped_column(primary_key=True)
    content: Mapped[str]
    title: Mapped[str]

    @property
    def html_content(self):
        return render_markdown(self.content)

class SearchResult(BaseModel):
    url: str
    title: str

    def __init__(self, title, url):
        self.title = title
        self.url = url