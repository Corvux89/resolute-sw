import time
from flask import current_app
from constants import CACHE_TIMEOUT, DISCORD_CLIENT_ID, DISCORD_GUILD_ID, LIMIT

MEMBER_CACHE = {
    "members": None,
    "timestamp": 0
    }

CHANNEL_CACHE = {
    "channels": None,
    "timestamp": 0
    }

ROLE_CACHE = {
    "roles": None,
    "timestamp": 0
    }

ENTITLEMENT_CACHE = {
    "entitlements": None, 
    "timestamp": 0
    }

BOT_CACHE = {
    "guilds": None, 
    "timestamp": 0
    }


def get_members_from_cache(guild_id: int = DISCORD_GUILD_ID):
    current_time = time.time()

    if guild_id not in MEMBER_CACHE:
        MEMBER_CACHE[guild_id] = {"members": None, "timestamp": 0}

    cache = MEMBER_CACHE[guild_id]

    if cache["members"] is None or (current_time - cache["timestamp"] > CACHE_TIMEOUT):
        members = current_app.discord.request(
            f"/guilds/{guild_id}/members?limit={LIMIT}"
        )
        cache["members"] = members
        cache["timestamp"] = current_time
    return cache["members"]


def get_channels_from_cache():
    current_time = time.time()

    if CHANNEL_CACHE["channels"] is None or (current_time - CHANNEL_CACHE["timestamp"] > CACHE_TIMEOUT):
        channels = current_app.discord.request(f"/guilds/{DISCORD_GUILD_ID}/channels")
        CHANNEL_CACHE["channels"] = channels
        CHANNEL_CACHE["timestamp"] = current_time
    return CHANNEL_CACHE["channels"]


def get_roles_from_cache(guild_id: int = DISCORD_GUILD_ID):
    current_time = time.time()

    if ROLE_CACHE["roles"] is None or (current_time - ROLE_CACHE["timestamp"] > CACHE_TIMEOUT):
        roles = current_app.discord.request(f"/guilds/{guild_id}/roles")
        ROLE_CACHE["roles"] = roles
        ROLE_CACHE["timestamp"] = current_time
    return ROLE_CACHE["roles"]


def get_bot_guilds_from_cache():
    current_time = time.time()

    if BOT_CACHE["guilds"] is None or (
        current_time - BOT_CACHE["timestamp"] > CACHE_TIMEOUT
    ):
        guilds = current_app.discord.request(f"/users/@me/guilds")
        BOT_CACHE["guilds"] = guilds
        BOT_CACHE["timestamp"] = current_time

    return BOT_CACHE["guilds"]


def get_entitlements_from_cache():
    current_time = time.time()

    if ENTITLEMENT_CACHE["entitlements"] is None or (
        current_time - ENTITLEMENT_CACHE["timestamp"] > CACHE_TIMEOUT
    ):
        entitlements = current_app.discord.request(
            f"/applications/{DISCORD_CLIENT_ID}/entitlements"
        )
        ENTITLEMENT_CACHE["entitlements"] = entitlements
        ENTITLEMENT_CACHE["timestamp"] = current_time

    return ENTITLEMENT_CACHE["entitlements"]
