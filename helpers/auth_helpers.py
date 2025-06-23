from constants import DISCORD_ADMINS
from models.auth import DiscordBot, User


from fastapi import Request

from models.exceptions import Forbidden
from models.resolute import ResoluteGuild


def get_discord(request: Request) -> DiscordBot:
    return request.app.discord

async def is_admin(request: Request) -> None:
    discord: DiscordBot = request.app.discord
    user: User = await discord.user(request)
    guild: ResoluteGuild = request.app.cache.fetch(ResoluteGuild)
    member = await discord.fetch_members(user.id)

    if (
        user.id in set(str(admin) for admin in DISCORD_ADMINS)
        or guild.admin_role and guild.admin_role in member.roles
        ):
        return
    raise Forbidden()

async def is_beta_tester(request: Request) -> None:
    discord: DiscordBot = request.app.discord
    user: User = await discord.user(request)
    guild: ResoluteGuild = request.app.cache.fetch(ResoluteGuild)
    member = await discord.fetch_members(user.id)

    if await is_admin(request):
        return 
    elif (beta_role := discord.fetch_roles(name="Beta Testing")) and beta_role.id in member.roles:
        return 

    raise Forbidden()

