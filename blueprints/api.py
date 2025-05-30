from typing import Optional, Union
from flask import Blueprint, current_app, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, asc, func, or_

from constants import DISCORD_GUILD_ID
from helpers.G0T0 import trigger_compendium_reload, trigger_guild_reload
from helpers.auth_helper import is_admin
from models.G0T0 import (
    Activity,
    ActivityPoints,
    BotMessage,
    Character,
    CodeConversion,
    G0T0Guild,
    LevelCost,
    Player,
    RefMessage,
)
from models.discord import DiscordChannel
from models.exceptions import BadRequest, NotFound
from sqlalchemy.orm import joinedload

from models.general import Content, ContentSource, Power, PowerType


api_blueprint = Blueprint("api", __name__)


@api_blueprint.route("/guild", methods=["GET"])
def get_guild():
    guild = _get_guild()
    return jsonify(guild)


@api_blueprint.route("/guild", methods=["PATCH"])
@is_admin
def update_guild():
    db: SQLAlchemy = current_app.config.get("DB")
    guild = _get_guild()
    update_data = request.get_json()

    # Max Level Validation
    if (
        db.session.query(Character)
        .filter(
            and_(
                Character.guild_id == guild.id,
                Character.active == True,
                Character.level > update_data.get("max_level", guild.max_level),
            )
        )
        .count()
        > 0
    ):
        raise BadRequest(
            f"There are currently active characters with a level exceeding {update_data.get('max_level', guild.max_level)}"
        )

    # Max Character Validation
    elif (
        db.session.query(
            Character._player_id, func.count(Character._player_id).label("count")
        )
        .filter(and_(Character.guild_id == guild.id, Character.active == True))
        .group_by(Character._player_id)
        .having(
            func.count(Character._player_id)
            > update_data.get("max_character", guild.max_characters)
        )
        .count()
        > 0
    ):
        raise BadRequest(
            f"there are currently players with more than {update_data.get('max_characters', guild.max_characters)} character(s)"
        )

    for k, v in update_data.items():
        if hasattr(guild, k) and k not in ["id", "last_reset"]:
            current_value = getattr(guild, k)
            expected_type = type(current_value)

            try:
                if current_value is not None:
                    value = expected_type(v)

                if current_value is None or current_value == "None" and value == "":
                    continue

                setattr(guild, k, v)

            except (ValueError, TypeError):
                raise BadRequest(
                    f"Type mismatch for '{k}': Expected {expected_type.__name__}, and got {type(value).__name__}"
                )

    db.session.commit()
    trigger_guild_reload()
    return jsonify(200)


@api_blueprint.route("/message", methods=["GET"])
@api_blueprint.route("/message/<int:message_id>", methods=["GET"])
@is_admin
def get_messages(message_id: int = None):
    message = _get_message(message_id, True)
    return jsonify(message)


@api_blueprint.route("/message", methods=["POST"])
@is_admin
def create_message():
    db: SQLAlchemy = current_app.config.get("DB")
    payload = request.get_json()

    discord_message = current_app.discord.request(
        f"/channels/{payload.get('channel_id')}/messages",
        "POST",
        json={"content": payload["message"]},
    )

    if "pin" in payload and payload.get("pin"):
        current_app.discord.request(
            f"/channels/{payload.get('channel_id')}/pins/{discord_message.get('id')}",
            "PUT",
        )

    message: RefMessage = RefMessage(
        guild_id=DISCORD_GUILD_ID,
        message_id=discord_message.get("id"),
        channel_id=payload.get("channel_id"),
        title=payload.get("title"),
    )

    db.session.add(message)
    db.session.commit()

    message = _get_message(message.message_id, True)

    return jsonify(message)


@api_blueprint.route("/message/<int:message_id>", methods=["PATCH"])
@is_admin
def update_message(message_id: int):
    message: RefMessage = _get_message(message_id)
    payload = request.get_json()
    db: SQLAlchemy = current_app.config.get("DB")

    try:
        discord_message = current_app.discord.request(
            f"/channels/{message.channel_id}/messages/{message.message_id}",
            "PATCH",
            json={"content": payload.get("content")},
        )

        message.title = payload.get("title")

        if "pin" in payload and payload.get("pin") != bool(
            discord_message.get("pinned", False)
        ):
            action = "PUT" if payload.get("pin") else "DELETE"

            current_app.discord.request(
                f"/channels/{message.channel_id}/pins/{message.message_id}", action
            )

        db.session.commit()

    except AttributeError:
        raise BadRequest()

    return jsonify(200)


@api_blueprint.route("/message/<int:message_id>", methods=["DELETE"])
@is_admin
def delete_message(message_id: int):
    message: RefMessage = _get_message(message_id)
    db: SQLAlchemy = current_app.config.get("DB")

    try:
        current_app.discord.request(
            f"/channels/{message.channel_id}/messages/{message.message_id}", "DELETE"
        )

        db.session.delete(message)
        db.session.commit()

    except:
        raise BadRequest("Something went wrong")

    return jsonify(200)


@api_blueprint.route("/channels", methods=["GET"])
@is_admin
def get_channels():
    return jsonify(current_app.discord.fetch_channels())


@api_blueprint.route("/roles", methods=["GET"])
@is_admin
def get_roles():
    return jsonify(current_app.discord.fetch_roles())


@api_blueprint.route("/players", methods=["GET"])
@api_blueprint.route("/players/<int:player_id>", methods=["GET"])
@is_admin
def get_players(player_id: int = None):
    db: SQLAlchemy = current_app.config.get("DB")
    query = (
        db.session.query(Player)
        .filter(Player._guild_id == DISCORD_GUILD_ID)
        .options(joinedload(Player.characters))
    )

    if player_id:
        query = query.filter(Player._id == player_id)

    players = query.all()

    if not players:
        raise NotFound("Players not found")

    return jsonify(players[0] if player_id else players)


@api_blueprint.route("/activities", methods=["GET"])
@is_admin
def get_activities():
    return jsonify(_get_activities())


@api_blueprint.route("/activities", methods=["PATCH"])
@is_admin
def update_activities():
    activities = _get_activities()
    act_dict = {a.id: a for a in activities}
    payload = request.get_json()
    db: SQLAlchemy = current_app.config.get("DB")

    try:
        update_data = [Activity(**a) for a in payload]

        for act in update_data:
            activity = act_dict.get(act.id)

            if not activity:
                db.session.rollback()
                raise NotFound(f"Activity {act.id} not found.")

            activity.cc = act.cc
            activity.diversion = act.diversion
            activity.points = act.points
            activity.credit_ratio = act.credit_ratio

        db.session.commit()
        trigger_compendium_reload()
    except:
        db.session.rollback()
        raise BadRequest()

    return jsonify(200)


@api_blueprint.route("/activity_points", methods=["GET"])
@is_admin
def get_activity_points():
    return jsonify(_get_activity_points())


@api_blueprint.route("/activity_points", methods=["PATCH"])
@is_admin
def update_activity_points():
    points = _get_activity_points()
    point_dict = {p.id: p for p in points}
    db: SQLAlchemy = current_app.config.get("DB")
    payload = request.get_json()

    try:
        update_data = [ActivityPoints(**a) for a in payload]

        for p in update_data:
            point = point_dict.get(p.id)

            if not point:
                db.session.rollback()
                raise NotFound(f"Activity Point {p.id} not found")

            point.points = p.points

        db.session.commit()
        trigger_compendium_reload()
    except:
        db.session.rollback()
        raise BadRequest()

    return jsonify(200)


@api_blueprint.route("/code_conversion", methods=["GET"])
@is_admin
def get_code_conversion():
    return jsonify(_get_code_conversion())


@api_blueprint.route("/code_conversion", methods=["PATCH"])
@is_admin
def update_code_conversion():
    db: SQLAlchemy = current_app.config.get("DB")
    codes = _get_code_conversion()
    code_dict = {c.id: c for c in codes}
    payload = request.get_json()

    try:
        update_data = [CodeConversion(**c) for c in payload]

        for cc in update_data:
            conversion = code_dict.get(cc.id)

            if not conversion:
                db.session.rollback()
                raise NotFound(f"Code Conversion {cc.id} not found")

            conversion.value = cc.value

        db.session.commit()
        trigger_compendium_reload()
    except:
        db.session.rollback()
        raise BadRequest()

    return jsonify(200)


@api_blueprint.route("/level_costs", methods=["GET"])
@is_admin
def get_level_costs():
    return jsonify(_get_level_costs())


@api_blueprint.route("/level_costs", methods=["PATCH"])
@is_admin
def update_level_costs():
    db: SQLAlchemy = current_app.config.get("DB")
    costs = _get_level_costs()
    cost_dict = {c.id: c for c in costs}
    payload = request.get_json()

    try:
        update_data = [LevelCost(**c) for c in payload]

        for c in update_data:
            cost = cost_dict.get(c.id)

            if not cost:
                db.session.rollback()
                raise NotFound(f"Level for {c.id} not found")

            cost.cc = c.cc

        db.session.commit()
        trigger_compendium_reload()

    except:
        db.session.rollback()
        raise BadRequest()

    return jsonify(200)


@api_blueprint.route("/content/<key>", methods=["PATCH"])
@is_admin
def update_content(key):
    db: SQLAlchemy = current_app.config.get("DB")
    payload = request.get_json()

    content: Content = db.session.query(Content).filter(Content.key == key).first()

    content.content = payload.get("content")

    db.session.commit()

    return jsonify(200)


@api_blueprint.route("/powers", methods=["GET"])
def powers(type: str = None):
    db: SQLAlchemy = current_app.config.get("DB")

    query = db.session.query(Power)

    if request.args.get("type"):
        power_type: PowerType = (
            db.session.query(PowerType)
            .filter(func.lower(PowerType.value) == request.args.get("type").lower())
            .first()
        )
        if not power_type:
            raise NotFound("Power Type not found")
        query = query.filter(Power._type == power_type.id)

    if request.args.get("level"):
        query = query.filter(Power.level == request.args.get("level"))

    if request.args.get("source"):
        source: ContentSource = (
            db.session.query(ContentSource)
            .filter(
                or_(
                    func.lower(ContentSource.abbreviation)
                    == request.args.get("source").lower(),
                    ContentSource.name.ilike(f"%{request.args.get('source').lower()}%"),
                )
            )
            .first()
        )
        if not source:
            raise NotFound("Content source not found")

        query = query.filter(Power._source == source.id)

    filter_map = {
        "name": Power.name,
        "prereq": Power.pre_requisite,
        "casttime": Power.casttime,
        "range": Power.range,
        "description": Power.description,
    }

    for arg, column in filter_map.items():
        if value := request.args.get(arg):
            query = query.filter(column.ilike(f"%{value.lower()}%"))

    powers = query.all()

    if not powers:
        raise NotFound("No power found")

    return jsonify(powers)


# --------------------------- #
# Private Methods
# --------------------------- #
def _get_level_costs() -> list[LevelCost]:
    db: SQLAlchemy = current_app.config.get("DB")
    costs: list[LevelCost] = (
        db.session.query(LevelCost).order_by(asc(LevelCost.id)).all()
    )

    if not costs:
        raise NotFound("Level costs not found")

    return costs


def _get_code_conversion() -> list[CodeConversion]:
    db: SQLAlchemy = current_app.config.get("DB")
    points: list[CodeConversion] = (
        db.session.query(CodeConversion).order_by(asc(CodeConversion.id)).all()
    )

    if not points:
        raise NotFound("Code Conversions not found")

    return points


def _get_activity_points() -> list[ActivityPoints]:
    db: SQLAlchemy = current_app.config.get("DB")
    points: list[ActivityPoints] = (
        db.session.query(ActivityPoints).order_by(asc(ActivityPoints.id)).all()
    )

    if not points:
        raise NotFound("Activity Points not found")

    return points


def _get_activities() -> list[Activity]:
    db: SQLAlchemy = current_app.config.get("DB")

    activities: list[Activity] = (
        db.session.query(Activity).order_by(asc(Activity.id)).all()
    )

    if not activities:
        raise NotFound("No Activities found")

    return activities


def _get_message(
    message_id: int = None, full_load: bool = False
) -> Optional[Union[BotMessage, RefMessage, list[RefMessage]]]:
    db: SQLAlchemy = current_app.config.get("DB")

    query = db.session.query(RefMessage).filter(
        RefMessage._guild_id == DISCORD_GUILD_ID
    )

    if message_id:
        message = query.filter(RefMessage._message_id == message_id).first()

        if not message:
            raise NotFound("Message not found")

        if full_load:
            discord_message = current_app.discord.request(
                f"/channels/{message.channel_id}/messages/{message.message_id}"
            )

            if "id" not in discord_message:
                db.session.delete(message)
                db.session.commit()
                raise NotFound("Discord message not found")

            else:
                channel: DiscordChannel = current_app.discord.fetch_channels(
                    message.channel_id
                )
                m = BotMessage(
                    message.message_id,
                    message.channel_id,
                    channel.name,
                    message.title,
                    discord_message["content"],
                    pin=discord_message["pinned"],
                    error=(
                        f"{discord_message.get('message')} - Need to ensure the bot has 'Read Message History access to #{channel.name}"
                        if "message" in discord_message
                        else ""
                    ),
                )
        else:
            m = message
    else:
        m = query.all()

    return m


def _get_guild() -> G0T0Guild:
    db: SQLAlchemy = current_app.config.get("DB")
    try:
        guild: G0T0Guild = (
            db.session.query(G0T0Guild)
            .filter(G0T0Guild._id == int(DISCORD_GUILD_ID))
            .first()
        )

        if not guild:
            raise NotFound("Guild not found")

        return guild
    except:
        raise BadRequest()
