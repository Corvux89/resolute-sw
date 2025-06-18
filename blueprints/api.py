from typing import Optional, Union
from urllib.parse import unquote
from flask import Blueprint, current_app, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, func

from constants import DISCORD_GUILD_ID
from helpers.G0T0 import trigger_compendium_reload, trigger_guild_reload
from helpers.auth_helper import is_admin
from models.general import Content
from models.discord import DiscordChannel
from models.G0T0 import (
    Activity,
    ActivityPoints,
    Archetype,
    Background,
    BotMessage,
    Character,
    CharacterClass,
    CodeConversion,
    EnhancedItem,
    Equipment,
    Feat,
    G0T0Guild,
    LevelCost,
    Player,
    Power,
    PrimaryClass,
    RefMessage,
    Species,
)
from models.exceptions import BadRequest, NotFound
from sqlalchemy.orm import joinedload


api_blueprint = Blueprint("api", __name__)

@api_blueprint.post('/refresh_cache')
@is_admin
def refresh_cache():
    try:
        current_app.cache.initialize(True)
    except Exception as e:
        raise BadRequest(str(e))

    return jsonify("Done")


@api_blueprint.get("/guild")
def get_guild():
    guild = current_app.cache.fetch(G0T0Guild)
    return jsonify(guild)


@api_blueprint.patch("/guild")
@is_admin
def update_guild():
    db: SQLAlchemy = current_app.config.get("DB")
    guild = current_app.cache.fetch(G0T0Guild)
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
    current_app.cache.update(db.session, G0T0Guild)
    trigger_guild_reload()
    return jsonify(200)


@api_blueprint.get("/message")
@api_blueprint.get("/message/<int:message_id>")
@is_admin
def get_messages(message_id: int = None):
    message = _get_message(message_id, True)
    return jsonify(message)


@api_blueprint.post("/message")
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
    current_app.cache.update(db.session, RefMessage)

    message = _get_message(message.message_id, True)

    return jsonify(message)


@api_blueprint.patch("/message/<int:message_id>")
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
        current_app.cache.update(db.session, RefMessage)

    except AttributeError:
        raise BadRequest()

    return jsonify(200)


@api_blueprint.delete("/message/<int:message_id>")
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
        current_app.cache.update(db.session, RefMessage)

    except:
        raise BadRequest("Something went wrong")

    return jsonify(200)


@api_blueprint.get("/channels")
@is_admin
def get_channels():
    return jsonify(current_app.discord.fetch_channels())


@api_blueprint.get("/roles")
@is_admin
def get_roles():
    return jsonify(current_app.discord.fetch_roles())


@api_blueprint.get("/players")
@api_blueprint.get("/players/<int:player_id>")
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


@api_blueprint.get("/activities")
@is_admin
def get_activities():
    return jsonify(_get_activities())


@api_blueprint.patch("/activities")
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
        current_app.cache.update(db.session, Activity)
        trigger_compendium_reload()
    except:
        db.session.rollback()
        raise BadRequest()

    return jsonify(200)


@api_blueprint.get("/activity_points")
@is_admin
def get_activity_points():
    return jsonify(_get_activity_points())


@api_blueprint.patch("/activity_points")
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
        current_app.cache.update(db.session, ActivityPoints)
        trigger_compendium_reload()
    except:
        db.session.rollback()
        raise BadRequest()

    return jsonify(200)


@api_blueprint.get("/code_conversion")
@is_admin
def get_code_conversion():
    return jsonify(_get_code_conversion())


@api_blueprint.patch("/code_conversion")
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
        current_app.cache.update(db.session, CodeConversion)
        trigger_compendium_reload()
    except:
        db.session.rollback()
        raise BadRequest()

    return jsonify(200)


@api_blueprint.get("/level_costs")
@is_admin
def get_level_costs():
    return jsonify(_get_level_costs())


@api_blueprint.patch("/level_costs")
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
        current_app.cache.update(db.session, LevelCost)
        trigger_compendium_reload()

    except:
        db.session.rollback()
        raise BadRequest()

    return jsonify(200)


@api_blueprint.patch("/content/<key>")
@is_admin
def update_content(key):
    db: SQLAlchemy = current_app.config.get("DB")
    payload = request.get_json()
    content: Content = next(
        (c for c in current_app.cache.fetch(Content) if c.key == key), None
    )

    if not content:
        raise NotFound("Content not found")

    content.content = payload.get("content")

    db.session.commit()

    return jsonify(200)


@api_blueprint.get("/powers")
def powers():
    powers = current_app.cache.fetch(Power)
    try:
        filter_map = {
            "level": lambda p, value: p.level == int(value),
            "type": lambda p, value: (
                value.lower() == p.type.value.lower() if p.type else None
            ),
            "name": lambda p, value: value.lower() in p.name.lower(),
            "prereq": lambda p, value: value.lower() in p.pre_requisite.lower(),
            "casttime": lambda p, value: value.lower() in p.casttime.lower(),
            "range": lambda p, value: value.lower() in p.range.lower(),
            "description": lambda p, value: value.lower() in p.description.lower(),
        }

        powers = filter_objects(filter_map, powers)
    except Exception as e:
        raise BadRequest(str(e))

    if not powers:
        raise NotFound("Power(s) not found")
    return jsonify(powers)


@api_blueprint.post("/powers")
@is_admin
def new_power():
    power = create_object(Power)
    return jsonify(power)


@api_blueprint.patch("/powers")
@is_admin
def update_power():
    power = update_object(
        Power,
        [
            "name",
            "pre_requisite",
            "casttime",
            "range",
            "description",
            "concentration",
            "level",
            "duration",
        ],
        ["type", "source", "alignment"],
    )

    return jsonify(power), 200


@api_blueprint.delete("/powers/<power_id>")
@is_admin
def delete_power(power_id):
    return delete_object(Power, power_id)


@api_blueprint.get("/species")
def get_species():
    species = current_app.cache.fetch(Species)
    try:
        filter_map = {
            "name": lambda s, value: value.lower() in s.value.lower(),
            "size": lambda s, value: value.lower() in s.size.lower(),
        }

        species = filter_objects(filter_map, species)
    except Exception as e:
        raise BadRequest(str(e))

    if not species:
        raise NotFound("No species found")

    return jsonify(species)


@api_blueprint.post("/species")
@is_admin
def new_species():
    species = create_object(Species)
    return jsonify(species), 200


@api_blueprint.patch("/species")
@is_admin
def update_species():
    species = update_object(
        Species,
        [
            "value",
            "skin_options",
            "hair_options",
            "eye_options",
            "distinctions",
            "height_average",
            "height_mod",
            "weight_average",
            "weight_mod",
            "homeworld",
            "flavortext",
            "language",
            "image_url",
            "size",
            "traits",
        ],
        ["source"],
    )
    return jsonify(species), 200


@api_blueprint.delete("/species/<species_id>")
@is_admin
def delete_species(species_id):
    return delete_object(Species, species_id)


@api_blueprint.get("/classes")
def get_classes():
    classes = current_app.cache.fetch(PrimaryClass)

    try:
        filter_map = {
            "name": lambda c, value: value.lower() in c.value.lower(),
        }

        classes = filter_objects(filter_map)
    except Exception as e:
        raise BadRequest(str(e))

    if not classes:
        raise NotFound("No Classes found")
    return jsonify(classes)


@api_blueprint.post("/classes")
@is_admin
def new_class():
    prim_class = create_object(PrimaryClass)
    return jsonify(prim_class), 200


@api_blueprint.patch("/classes")
@is_admin
def update_class():
    prim_class = update_object(
        PrimaryClass,
        [
            "value",
            "summary",
            "primary_ability",
            "flavortext",
            "level_changes",
            "hit_die",
            "level_1_hp",
            "higher_hp",
            "armor_prof",
            "weapon_prof",
            "tool_prof",
            "saving_throws",
            "skill_choices",
            "starting_equipment",
            "features",
            "archetype_flavor",
            "image_url",
        ],
        ["source", "caster_type"],
    )
    return jsonify(prim_class), 200


@api_blueprint.delete("/classes/<class_id>")
@is_admin
def delete_class(class_id):
    db: SQLAlchemy = current_app.config.get("DB")
    prim_class = current_app.cache.fetch(PrimaryClass, class_id)

    if not prim_class:
        raise NotFound("Class not found")

    if (
        db.session.query(CharacterClass)
        .join(Character, CharacterClass.character_id == Character.id)
        .filter(
            and_(
                CharacterClass.active == True,
                Character.active == True,
                CharacterClass._primary_class == class_id,
            )
        )
        .count()
        > 0
    ):
        raise BadRequest("Current active character have that class set")

    return delete_object(PrimaryClass, class_id)


@api_blueprint.get("/archetypes")
def get_archetypes():
    archetypes = current_app.cache.fetch(Archetype)

    try:
        filter_map = {
            "name": lambda a, value: value.lower() in a.value.lower(),
            "class": lambda a, value: value.lower() in a.parent_name.lower(),
            "caster": lambda a, value: (
                value.lower() in a.caster_type.value.lower() if a.caster_type else False
            ),
        }

        archetypes = filter_objects(filter_map, archetypes)
    except Exception as e:
        raise BadRequest(str(e))
    if not archetypes:
        raise NotFound("Archetype not found")

    return jsonify(archetypes)


@api_blueprint.post("/archetypes")
@is_admin
def new_archetype():
    arch = create_object(Archetype)
    return jsonify(arch), 200


@api_blueprint.patch("/archetypes")
@is_admin
def update_archetypes():
    arch = update_object(
        Archetype,
        ["value", "level_table", "image_url", "flavortext"],
        ["caster_type", "source"],
    )
    return jsonify(arch), 200


@api_blueprint.delete("/archetypes/<arch_id>")
@is_admin
def delete_archetype(arch_id):
    db: SQLAlchemy = current_app.config.get("DB")
    arch = current_app.cache.fetch(Archetype, arch_id)

    if not arch:
        raise NotFound("Archetype not found")

    if (
        db.session.query(CharacterClass)
        .join(Character, CharacterClass.character_id == Character.id)
        .filter(
            and_(
                CharacterClass.active == True,
                Character.active == True,
                CharacterClass._archetype == arch_id,
            )
        )
        .count()
        > 0
    ):
        raise BadRequest("Current active character(s) have that archetype set")

    return delete_object(Archetype, arch_id)


@api_blueprint.get("/equipment")
def get_equipment():
    equipment = current_app.cache.fetch(Equipment)

    try:
        filter_map = {
            "type": lambda e, value: (
                value.lower() == e.category.value.lower()
                if e.category and value.lower() != "adventuring"
                else (
                    e.category.id not in [3, 4]
                    if e.category and value.lower() == "adventuring"
                    else False
                )
            )
        }

        equipment = filter_objects(filter_map, equipment)
    except Exception as e:
        raise BadRequest(str(e))

    if not equipment:
        raise NotFound("Equipment not found")

    return jsonify(equipment)


@api_blueprint.post("/equipment")
@is_admin
def new_equipment():
    equipment = create_object(Equipment)
    return jsonify(equipment), 200


@api_blueprint.patch("/equipment")
@is_admin
def update_equipment():
    equipment = update_object(
        Equipment,
        [
            "name",
            "description",
            "cost",
            "weight",
            "dmg_number_of_die",
            "dmg_die_type",
            "dmg_type",
            "properties",
            "ac",
            "stealth_dis",
        ],
        ["source", "sub_category"],
    )
    return jsonify(equipment), 200


@api_blueprint.delete("/equipment/<equip_id>")
@is_admin
def delete_equipment(equip_id):
    return delete_object(Equipment, equip_id)


@api_blueprint.get("/enhanced_items")
def get_enhanced_items():
    items = current_app.cache.fetch(EnhancedItem)

    try:
        filter_map = {
            "type": lambda i, value: (
                value.lower() == i.type.value.lower()
                if i.type and value.lower() != "other"
                else (
                    i.type.id not in [3, 7, 5, 4]
                    if i.type and value.lower() == "other"
                    else False
                )
            ),
            "name": lambda i, value: value.lower() in i.name.lower(),
            "prereq": lambda i, value: value.lower() in i.prerequisite.lower(),
        }

        items = filter_objects(filter_map, items)
    except Exception as e:
        raise BadRequest(e)

    if not items:
        raise NotFound("Enhanced Items not found")

    return jsonify(items), 200


@api_blueprint.post("/enhanced_items")
@is_admin
def new_enhanced_item():
    item = create_object(EnhancedItem)
    return jsonify(item), 200


@api_blueprint.patch("/enhanced_items")
@is_admin
def update_enhanced_item():
    item = update_object(
        EnhancedItem,
        ["name", "attunement", "text", "prerequisite", "subtype_ft", "cost"],
        ["source", "subtype", "rarity"],
    )
    return jsonify(item), 200


@api_blueprint.delete("/enhanced_items/<e_id>")
@is_admin
def delete_enhanced_item(e_id):
    return delete_object(EnhancedItem, e_id)


@api_blueprint.get("/feats")
def get_feats():
    feats = current_app.cache.fetch(Feat)

    try:
        filter_map = {
            "name": lambda f, value: value.lower() in f.name.lower(),
            "prereq": lambda f, value: value.lower() in f.prerequisite.lower(),
        }

        feats = filter_objects(filter_map, feats)
    except Exception as e:
        raise BadRequest(str(e))

    if not feats:
        raise NotFound("Feats not found")

    return jsonify(feats)


@api_blueprint.post("/feats")
@is_admin
def new_feat():
    feat = create_object(Feat)
    return jsonify(feat), 200


@api_blueprint.patch("/feats")
@is_admin
def update_feat():
    feat = update_object(
        Feat, ["name", "prerequisite", "text", "attributes"], ["source"]
    )
    return jsonify(feat), 200


@api_blueprint.delete("/feats/<f_id>")
@is_admin
def delete_feat(f_id):
    return delete_object(Feat, f_id)


@api_blueprint.get("/backgrounds")
def get_backgrounds():
    backgrounds = current_app.cache.fetch(Background)

    try:
        filter_map = {
            "name": lambda b, value: (
                value.lower() in b.name.lower() if b.name else False
            )
        }

        backgrounds = filter_objects(filter_map, backgrounds)
    except Exception as e:
        raise BadRequest(str(e))

    if not backgrounds:
        raise NotFound("Backgrounds not found")

    return jsonify(backgrounds)


@api_blueprint.post("/backgrounds")
@is_admin
def new_background():
    background = create_object(Background)
    return jsonify(background), 200


@api_blueprint.patch("/backgrounds")
@is_admin
def update_background():
    background = update_object(
        Background,
        [
            "name",
            "flavortext",
            "flavor_name",
            "flavor_description",
            "skills",
            "tools",
            "languages",
            "equipment",
            "suggested_characteristics",
            "feature_name",
            "feature_text",
            "feats",
            "personality",
            "ideal",
            "flaw",
            "bond",
        ],
        ["source"],
    )
    return jsonify(background), 200


@api_blueprint.delete("/backgrounds/<id>")
@is_admin
def delete_backgrounds(id):
    return delete_object(Background, id)


# --------------------------- #
# Private Methods
# --------------------------- #


def filter_objects(filter_map: {}, objects: []) -> []:
    for arg, filter_func in filter_map.items():
        if raw_value := request.args.get(arg):
            value = unquote(raw_value)
            objects = [p for p in objects if filter_func(p, value)]

    return objects


def create_object(model_class):
    db: SQLAlchemy = current_app.config.get("DB")
    if not request:
        raise BadRequest()

    data = request.get_json()
    try:
        obj = model_class.from_json(data)
        db.session.add(obj)
        db.session.commit()
        if current_app.cache.contains(model_class):
            current_app.cache.update(db.session, model_class)
        return obj
    except Exception as e:
        db.session.rollback()
        raise BadRequest(str(e))


def delete_object(model_class, id):
    db: SQLAlchemy = current_app.config.get("DB")
    try:
        if not id:
            raise BadRequest("Missing Object ID")

        obj = current_app.cache.fetch(model_class, id)

        if not obj:
            raise NotFound(f"{model_class.__name__} not found")

        db.session.delete(obj)
        db.session.commit()

        if current_app.cache.contains(model_class):
            current_app.cache.update(db.session, model_class)

        return jsonify(200)

    except Exception as e:
        raise BadRequest(str(e))


def update_object(model_class, update_fields: [] = [], fk_fields: [] = []):
    db: SQLAlchemy = current_app.config.get("DB")
    all_fields = update_fields + fk_fields
    if not request:
        raise BadRequest()

    data = request.get_json()

    try:
        object_id = data.get("id")

        if not object_id:
            raise NotFound(f"Missing object id")

        obj = current_app.cache.fetch(model_class, object_id)
        if not obj:
            raise NotFound(f"{model_class.__name__} not found.")

        obj = db.session.merge(obj)

        for field in all_fields:
            if field in data:
                if field in update_fields:
                    setattr(obj, field, data[field])
                elif field in fk_fields:
                    setattr(obj, f"_{field}", data[field].get("id"))

        db.session.commit()
        if current_app.cache.contains(model_class):
            current_app.cache.update(db.session, model_class)

        return obj

    except Exception as e:
        db.session.rollback()
        raise BadRequest(str(e))


def _get_level_costs() -> list[LevelCost]:
    costs: list[LevelCost] = sorted(
        current_app.cache.fetch(LevelCost), key=lambda c: c.id
    )

    if not costs:
        raise NotFound("Level costs not found")

    return costs


def _get_code_conversion() -> list[CodeConversion]:
    points: list[CodeConversion] = sorted(
        current_app.cache.fetch(CodeConversion), key=lambda c: c.id
    )

    if not points:
        raise NotFound("Code Conversions not found")

    return points


def _get_activity_points() -> list[ActivityPoints]:
    points: list[ActivityPoints] = sorted(
        current_app.cache.fetch(ActivityPoints), key=lambda a: a.id
    )

    if not points:
        raise NotFound("Activity Points not found")

    return points


def _get_activities() -> list[Activity]:
    activities: list[Activity] = sorted(
        current_app.cache.fetch(Activity), key=lambda a: a.id
    )

    if not activities:
        raise NotFound("No Activities found")

    return activities


def _get_message(
    message_id: int = None, full_load: bool = False
) -> Optional[Union[BotMessage, RefMessage, list[RefMessage]]]:
    db: SQLAlchemy = current_app.config.get("DB")
    messages = current_app.cache.fetch(RefMessage)

    if message_id:
        message = next((m for m in messages if m._message_id == message_id), None)

        if not message:
            raise NotFound("Message not found")

        if full_load:
            discord_message = current_app.discord.request(
                f"/channels/{message.channel_id}/messages/{message.message_id}"
            )

            if "id" not in discord_message:
                db.session.delete(message)
                db.session.commit()
                current_app.cache.update(db.session, RefMessage)
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
        m = messages

    return m
