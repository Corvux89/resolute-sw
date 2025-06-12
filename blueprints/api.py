from typing import Optional, Union
from urllib.parse import unquote
from flask import Blueprint, current_app, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, asc, func, or_

from constants import DISCORD_GUILD_ID
from helpers.G0T0 import trigger_compendium_reload, trigger_guild_reload
from helpers.auth_helper import is_admin
from models.general import Content
from models.discord import DiscordChannel
from models.G0T0 import (
    Activity,
    ActivityPoints,
    Archetype,
    BotMessage,
    Character,
    CharacterClass,
    CodeConversion,
    ContentSource,
    EnhancedItem,
    EnhancedItemSubtype,
    EnhancedItemType,
    Equipment,
    EquipmentCategory,
    EquipmentSubCategory,
    Feat,
    G0T0Guild,
    LevelCost,
    Player,
    Power,
    PowerType,
    PrimaryClass,
    RefMessage,
    Species,
)
from models.exceptions import BadRequest, NotFound
from sqlalchemy.orm import joinedload


api_blueprint = Blueprint("api", __name__)


@api_blueprint.get("/guild")
def get_guild():
    guild = _get_guild()
    return jsonify(guild)


@api_blueprint.patch("/guild")
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

    content: Content = db.session.query(Content).filter(Content.key == key).first()

    content.content = payload.get("content")

    db.session.commit()

    return jsonify(200)


@api_blueprint.get("/powers")
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

@api_blueprint.post("/powers")
@is_admin
def new_power():
    db: SQLAlchemy = current_app.config.get("DB")
    data = request.get_json()
    try:
        power: Power = Power.from_json(data)
        db.session.add(power)
        db.session.commit()
    except:
        raise BadRequest()

    return jsonify(200)

@api_blueprint.patch('/powers')
@is_admin
def update_power():
    db: SQLAlchemy = current_app.config.get("DB")
    data = request.get_json()
    try:
        # 1. Require an ID in the payload
        power_id = data.get("id")
        if not power_id:
            raise BadRequest("Missing power id for update.")

        # 2. Fetch the existing Power
        power: Power = db.session.query(Power).filter(Power.id == power_id).first()
        if not power:
            raise NotFound("Power not found.")

        # 3. Update fields (handle nested objects for FKs)
        for field in [
            "name", "pre_requisite", "casttime", "range", "description",
            "concentration", "level", "duration"
        ]:
            if field in data:
                setattr(power, field, data[field])

        # Foreign keys (handle nested objects)
        if "type" in data and data["type"]:
            power._type = data["type"].get("id")
        if "source" in data and data["source"]:
            power._source = data["source"].get("id")
        if "alignment" in data and data["alignment"]:
            power._alignment = data["alignment"].get("id")

        db.session.commit()
    except:
        raise BadRequest()
    return jsonify(200)

@api_blueprint.delete('/powers/<power_id>')
@is_admin
def delete_power(power_id):
    db: SQLAlchemy = current_app.config.get("DB")
    power: Power = db.session.query(Power).filter(Power.id == power_id).first()

    if not power:
        raise NotFound()
    
    db.session.delete(power)
    db.session.commit()

    return jsonify(200)

@api_blueprint.get('/species')
def get_species():
    db: SQLAlchemy = current_app.config.get("DB")

    query = db.session.query(Species)

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

        query = query.filter(Species._source == source.id)

    filter_map = {
        "name": Species.value,
        "size": Species.size,
    }

    for arg, column in filter_map.items():
        if value := request.args.get(arg):
            query = query.filter(column.ilike(f"%{value.lower()}%"))

    species = query.all()

    if not species:
        raise NotFound("No species found")
    
    return jsonify(species)

@api_blueprint.post('/species')
@is_admin
def new_species():
    db: SQLAlchemy = current_app.config.get("DB")
    data = request.get_json()

    try:
        species: Species = Species.from_json(data)
        db.session.add(species)
        db.session.commit()
    except Exception as e:
        raise BadRequest()
    
    return jsonify(200)

@api_blueprint.patch('/species')
@is_admin
def update_species():
    db: SQLAlchemy = current_app.config.get("DB")
    data = request.get_json()

    try:
        species_id = data.get('id')
        if not species_id:
            raise BadRequest("Missing Species id for update")
        
        species: Species = db.session.query(Species).filter(Species.id == species_id).first()

        if not species:
            raise NotFound("Species not found")
        
        for field in ["value","skin_options", "hair_options", "eye_options", "distinctions", "height_average", "height_mod", 
                      "weight_average", "weight_mod", "homeworld", "flavortext", "language", "image_url", "size", "traits"]:
            if field in data:
                setattr(species, field, data[field])

        if "source" in data and data["source"]:
            species._source = data["source"].get("id")

        db.session.commit()
    except NotFound:
        raise NotFound()
    except Exception as e:
        raise BadRequest()
    
    return jsonify(200)

@api_blueprint.delete('/species/<species_id>')
@is_admin
def delete_species(species_id):
    db: SQLAlchemy = current_app.config.get("DB")
    species: Species = db.session.query(Species).filter(Species.id == species_id).first()

    if not species:
        raise NotFound()
    
    if db.session.query(Character).filter(and_(
        Character.active == True,
        Character._species == species.id
    )).count() > 0:
        raise BadRequest("Current active characters have that species set")
    
    db.session.delete(species)
    db.session.commit()

    return jsonify(200)

@api_blueprint.get('/classes')
def get_classes():
    db: SQLAlchemy = current_app.config.get("DB")
    query = db.session.query(PrimaryClass)

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

        query = query.filter(PrimaryClass._source == source.id)

    filter_map = {
        "name": PrimaryClass.value,
    }

    for arg, column in filter_map.items():
        if value := request.args.get(arg):
            query = query.filter(column.ilike(f"%{value.lower()}%"))

    classes = query.all()

    if not classes:
        raise NotFound("No Classes found")
    return jsonify(classes)

@api_blueprint.post('/classes')
@is_admin
def new_class():
    db: SQLAlchemy = current_app.config.get("DB")
    data = request.get_json()

    try:
        prim_class: PrimaryClass = PrimaryClass.from_json(data)
        db.session.add(prim_class)
        db.session.commit()
    except Exception as e:
        raise BadRequest()
    
    return jsonify(200)
    
@api_blueprint.patch('/classes')
@is_admin
def update_class():
    db: SQLAlchemy = current_app.config.get("DB")
    data = request.get_json()

    try:
        if not (class_id := data.get('id')):
            raise BadRequest()
        
        prim_class: PrimaryClass = db.session.query(PrimaryClass).filter(PrimaryClass.id == class_id).first()

        if not prim_class:
            raise NotFound()
        
        for field in ["value", "summary", "primary_ability", "flavortext", "level_changes", "hit_die", "level_1_hp", "higher_hp", "armor_prof",
                      "weapon_prof", "tool_prof", "saving_throws", "skill_choices", "starting_equipment", "features", "archetype_flavor", "image_url"]:
            if field in data:
                setattr(prim_class, field, data[field])

        if "source" in data and data["source"]:
            prim_class._source = data["source"].get('id')
        if "caster_type" in data and data["caster_type"]:
            prim_class._caster_type = data["caster_type"].get('id')

        db.session.commit()
    except NotFound:
        raise NotFound()
    except Exception as e:
        raise BadRequest()
    
    return jsonify(200)

@api_blueprint.delete('/classes/<class_id>')
@is_admin
def delete_class(class_id):
    db: SQLAlchemy = current_app.config.get("DB")
    prim_class: PrimaryClass = db.session.query(PrimaryClass).filter(PrimaryClass.id == class_id).first()

    if not prim_class:
        raise NotFound()
    
    if (db.session.query(CharacterClass)
        .join(Character, CharacterClass.character_id == Character.id)
        .filter(and_(
            CharacterClass.active == True,
            Character.active == True,
            CharacterClass._primary_class == class_id
        )).count() > 0
        ):
        raise BadRequest("Current active character have that class set")
    
    db.session.delete(prim_class)
    db.session.commit()

    return jsonify(200)

@api_blueprint.get("/archetypes")
def get_archetypes():
    db: SQLAlchemy = current_app.config.get("DB")
    query = db.session.query(Archetype)

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

        query = query.filter(Archetype._source == source.id)

    if request.args.get('class'):
        prim_class: PrimaryClass = (
            db.session.query(PrimaryClass)
            .filter(
                PrimaryClass.value.ilike(f"%{request.args.get('class').lower()}%")
            ).first()
        )

        if not prim_class:
            raise NotFound(f"Primary class '{request.args.get('class')}' not found")
        
        query = query.filter(Archetype.parent == prim_class.id) 

    if request.args.get('caster'):
        caster_type: PowerType = (
            db.session.query(PowerType)
            .filter(
                PowerType.value.ilike(f"%{request.args.get('caster').lower()}%")
                ).first()
            )
        
        if not caster_type:
            raise NotFound("Caster type not found")
        
        query = query.filter(Archetype._caster_type == caster_type.id)


    filter_map = {
        "name": Archetype.value,
    }

    for arg, column in filter_map.items():
        if value := request.args.get(arg):
            query = query.filter(column.ilike(f"%{value.lower()}%"))

    archetypes = query.all()

    if not archetypes:
        raise NotFound()
    
    return jsonify(archetypes)

@api_blueprint.post('/archetypes')
@is_admin
def new_archetype():
    db: SQLAlchemy = current_app.config.get("DB")
    data = request.get_json()

    try:
        arch: Archetype = Archetype.from_json(data)
        db.session.add(arch)
        db.session.commit()
    except Exception as e:
        raise BadRequest(e)
    
    return jsonify(200)

@api_blueprint.patch('/archetypes')
@is_admin
def update_archetypes():
    db: SQLAlchemy = current_app.config.get("DB")
    data = request.get_json()

    try:
        if not (a_id := data.get('id')):
            raise BadRequest("No object ID specified")
        
        arch = db.session.query(Archetype).filter(Archetype.id == a_id).first()

        if not arch:
            raise NotFound("Archetype not found")
        
        for field in ["value", "level_table", "image_url", "flavortext"]:
            if field in data:
                setattr(arch, field, data[field])

        if "source" in data and data["source"]:
            arch._source = data["source"].get('id')
        if "caster_type" in data and data["caster_type"]:
            arch._caster_type = data["caster_type"].get('id')

        db.session.commit()        
    except NotFound as e:
        raise NotFound(e)
    except Exception as e:
        raise BadRequest(e)
    
    return jsonify(200)

@api_blueprint.delete('/archetypes/<arch_id>')
@is_admin
def delete_archetype(arch_id):
    db: SQLAlchemy = current_app.config.get("DB")
    arch: Archetype = db.session.query(Archetype).filter(Archetype.id == arch_id).first()

    if not arch:
        raise NotFound()
    
    if (db.session.query(CharacterClass)
        .join(Character, CharacterClass.character_id == Character.id)
        .filter(and_(
            CharacterClass.active == True,
            Character.active == True,
            CharacterClass._archetype == arch_id
        )).count() > 0
        ):
        raise BadRequest("Current active character(s) have that archetype set")
    
    db.session.delete(arch)
    db.session.commit()

    return jsonify(200)

@api_blueprint.get('/equipment')
def get_equipment():
    db: SQLAlchemy = current_app.config.get("DB")
    query = db.session.query(Equipment)

    if request.args.get('type'):
        if request.args.get('type') == "adventuring":
            query = query.filter(~Equipment._category.in_([3,4]))
        else:
            equip_type: EquipmentCategory = (
                db.session.query(EquipmentCategory)
                .filter(func.lower(EquipmentCategory.value) == unquote(request.args.get('type')).lower())
                .first()
            )

            if not equip_type:
                raise NotFound("Equipment type not found")
            query = query.filter(Equipment._category == equip_type.id)

    equipment = query.all()

    if not equipment:
        raise NotFound()
    
    return jsonify(equipment)

@api_blueprint.post('/equipment')
@is_admin
def new_equipment():
    db: SQLAlchemy = current_app.config.get("DB")
    data = request.get_json()

    try:
       equipment: Equipment = Equipment.from_json(data)
       db.session.add(equipment) 
       db.session.commit()
    except Exception as e:
        raise BadRequest()

    return jsonify(200)

@api_blueprint.patch('/equipment')
@is_admin
def update_equipment():
    db: SQLAlchemy = current_app.config.get("DB")
    data = request.get_json()

    try:
        if not (a_id := data.get('id')):
            raise BadRequest("No object ID specified")
        
        equipment: Equipment = db.session.query(Equipment).filter(Equipment.id == a_id).first()

        if not equipment:
            raise NotFound("Equipment not found")
        
        for field in ["name", "description", "cost", "weight", "dmg_number_of_die", "dmg_die_type",
                      "dmg_type", "properties", "ac", "stealth_dis"]:
            if field in data:
                setattr(equipment, field, data[field])

        if "source" in data and data["source"]:
            equipment._source = data["source"].get('id')
        if "sub_category" in data and data["sub_category"]:
            sub_category = db.session.query(EquipmentSubCategory).filter(EquipmentSubCategory.id == data["sub_category"].get('id')).first()

            if sub_category.parent != equipment._category:
                raise BadRequest()
            equipment._sub_category = sub_category.id

        db.session.commit()        
    except NotFound as e:
        raise NotFound(e)
    except Exception as e:
        raise BadRequest(e)
    
    return jsonify(200)

@api_blueprint.delete('/equipment/<equip_id>')
@is_admin
def delete_equipment(equip_id):
    db: SQLAlchemy = current_app.config.get("DB")
    equipment: Equipment = db.session.query(Equipment).filter(Equipment.id == equip_id).first()

    if not equipment:
        raise NotFound()
    
    db.session.delete(equipment)
    db.session.commit()

    return jsonify(200)

@api_blueprint.get('/enhanced_items')
def get_enhanced_items():
    db: SQLAlchemy = current_app.config.get("DB")
    query = db.session.query(EnhancedItem)

    if request.args.get('type'):
        if request.args.get('type').lower() == 'other':
            query = query.filter(~EnhancedItem._type.in_([3,7,5,4]))
        else:
            i_type: EnhancedItemType = (
                db.session.query(EnhancedItemType)
                .filter(func.lower(EnhancedItemType.value) == unquote(request.args.get('type')).lower())
                .first()
            )

            if not i_type:
                raise NotFound("Enhanced Item Type no found")
            query = query.filter(EnhancedItem._type == i_type.id)

    filter_map = {
        "name": EnhancedItem.name,
        "prereq": EnhancedItem.prerequisite,
    }

    for arg, column in filter_map.items():
        if value := request.args.get(arg):
            query = query.filter(column.ilike(f"%{value.lower()}%"))

    items = query.all()

    if not items:
        raise NotFound()
    
    return jsonify(items)

@api_blueprint.post('/enhanced_items')
@is_admin
def new_enhanced_item():
    db: SQLAlchemy = current_app.config.get("DB")
    data = request.get_json()

    try:
        e_item: EnhancedItem = EnhancedItem.from_json(data)
        db.session.add(e_item)
        db.session.commit()
    except Exception as e:
        raise BadRequest()
    
    return jsonify(200)

@api_blueprint.patch('/enhanced_items')
@is_admin
def update_enhanced_item():
    db: SQLAlchemy = current_app.config.get("DB")
    data = request.get_json()

    try:
        if not (a_id := data.get('id')):
            raise BadRequest("No object ID specified")
        
        e_item = db.session.query(EnhancedItem).filter(EnhancedItem.id == a_id).first()

        if not e_item:
            raise NotFound("Equipment not found")
        
        for field in ["name", "attunemtn", "text", "prerequisite", "subtype_ft", "cost"]:
            if field in data:
                setattr(e_item, field, data[field])

        if "source" in data and data["source"]:
            e_item._source = data["source"].get('id')
        if "subtype" in data and data["subtype"]:
            subtype: EnhancedItemSubtype = db.session.query(EnhancedItemSubtype).filter(EnhancedItemSubtype.id == data["subtype"].get('id')).first()

            if not subtype or (subtype and subtype.parent != e_item.type.id):
                raise BadRequest("Subtype is not valid")
            
            e_item._subtype = subtype.id
        if "rarity" in data and data["rarity"]:
            e_item._rarity = data["rarity"].get('id')

        db.session.commit()        
    except NotFound as e:
        raise NotFound(e)
    except Exception as e:
        raise BadRequest(e)
    
    return jsonify(200)

@api_blueprint.delete('/enhanced_items/<e_id>')
@is_admin
def delete_enhanced_item(e_id):
    db: SQLAlchemy = current_app.config.get("DB")
    e_item: EnhancedItem = db.session.query(EnhancedItem).filter(EnhancedItem.id == e_id).first()

    if not e_item:
        raise NotFound()
    
    db.session.delete(e_item)
    db.session.commit()

    return jsonify(200)

@api_blueprint.get('/feats')
def get_feats():
    db: SQLAlchemy = current_app.config.get("DB")
    query = db.session.query(Feat)

    feats = query.all()

    if not feats:
        raise NotFound()
    
    filter_map = {
        "name": Feat.name,
        "prereq": Feat.prerequisite,
    }

    for arg, column in filter_map.items():
        if value := request.args.get(arg):
            query = query.filter(column.ilike(f"%{value.lower()}%"))
    
    return jsonify(feats)

@api_blueprint.post('/feats')
@is_admin
def new_feat():
    db: SQLAlchemy = current_app.config.get("DB")
    data = request.get_json()

    try:
        feat: Feat = Feat.from_json(data)
        db.session.add(feat)
        db.session.commit()
    except Exception as e:
        raise BadRequest()
    
    return jsonify(200)

@api_blueprint.patch('/feats')
@is_admin
def update_feat():
    db: SQLAlchemy = current_app.config.get("DB")
    data = request.get_json()

    try:
        if not (a_id := data.get('id')):
            raise BadRequest("No object ID specified")
        
        feat: Feat = db.session.query(Feat).filter(Feat.id == a_id).first()

        if not feat:
            raise NotFound("Feat not found")
        
        for field in ["name", "prerequisite", "text", "attributes"]:
            if field in data:
                setattr(feat, field, data[field])

        if "source" in data and data["source"]:
            feat._source = data["source"].get('id')

        db.session.commit()        
    except NotFound as e:
        raise NotFound(e)
    except Exception as e:
        raise BadRequest(e)
    
    return jsonify(200)

@api_blueprint.delete('/feats/<f_id>')
@is_admin
def delete_feat(f_id):
    db: SQLAlchemy = current_app.config.get("DB")
    feat: Feat = db.session.query(Feat).filter(Feat.id == f_id).first()

    if not feat:
        raise NotFound()
    
    db.session.delete(feat)
    db.session.commit()

    return jsonify(200)



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
