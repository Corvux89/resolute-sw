from fastapi.responses import RedirectResponse
from fastapi import HTTPException
from constants import DISCORD_ADMINS
from models.auth import DiscordBot, User


from fastapi import Request

from models.exceptions import Forbidden, Unauthorized
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
        or guild.admin_role
        and guild.admin_role in member.roles
    ):
        return
    raise Forbidden()


async def is_beta_tester(request: Request) -> None:
    discord: DiscordBot = request.app.discord
    try:
        if user := await discord.user(request):
            member = await discord.fetch_members(user.id)
            try:
                await is_admin(request)
                return
            except Forbidden:
                pass

            # Check if user has beta testing role
            if (
                beta_role := await discord.fetch_roles(name="Beta Testing")
            ) and beta_role.id in member.roles:
                return

            raise Forbidden()
    except Unauthorized:
        # Pass the current URL as state parameter for redirect after login
        current_url = str(request.url)
        login_url = discord.get_oauth_login_url(state=current_url)
        # Use HTTPException with redirect status code for dependencies
        raise HTTPException(status_code=302, headers={"Location": login_url})
    except Exception as e:
        raise Forbidden(str(e))
