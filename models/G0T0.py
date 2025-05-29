import json
import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import BigInteger, ForeignKey, DateTime, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.postgresql import ARRAY

from constants import DISCORD_GUILD_ID
from helpers.general_helpers import get_channels_from_cache
from models.discord import MemberAttributeMixin
from models.general import BaseModel, IntAttributeMixin

db = SQLAlchemy()


class Activity(db.Model, BaseModel):
    __tablename__ = "c_activity"
    id: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[str]
    cc: Mapped[int]
    diversion: Mapped[bool]
    points: Mapped[int]
    credit_ratio: Mapped[float]

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.value = kwargs.get("value")
        self.cc = kwargs.get("cc", 0)
        self.diversion = kwargs.get("diversion", False)
        self.points = kwargs.get("points", 0)
        self.credit_ratio = kwargs.get("credit_ratio")


class ActivityPoints(db.Model, BaseModel):
    __tablename__ = "c_activity_points"
    id: Mapped[int] = mapped_column(primary_key=True)
    points: Mapped[int]

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.points = kwargs.get("points", 0)


class CodeConversion(db.Model, BaseModel):
    __tablename__ = "c_code_conversion"
    id: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[int]

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.value = kwargs.get("value", 0)


class LevelCost(db.Model, BaseModel):
    __tablename__ = "c_level_costs"
    id: Mapped[int] = mapped_column(primary_key=True)
    cc: Mapped[int]

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.cc = kwargs.get("cc", 0)


class Faction(db.Model, BaseModel):
    __tablename__ = "c_factions"
    id: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[str]

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.value = kwargs.get("value")


class PrimaryClass(db.Model, BaseModel):
    __tablename__ = "c_character_class"
    id: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[str]

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.value = kwargs.get("value")


class Archetype(db.Model, BaseModel):
    __tablename__ = "c_character_archetype"
    id: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[str]
    parent: Mapped[int]

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.value = kwargs.get("value")
        self.parent = kwargs.get("parent")


class Species(db.Model, BaseModel):
    __tablename__ = "c_character_species"
    id: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[str]

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.value = kwargs.get("value")


class Store(db.Model, BaseModel, IntAttributeMixin):
    __tablename__ = "store"
    _sku: Mapped[int] = mapped_column("sku", primary_key=True)
    user_cost: Mapped[float]

    def __init__(self, **kwargs):
        self._sku = kwargs.get("sku")
        self.user_cost = kwargs.get("user_cost", 0)

    @property
    def sku(self):
        return str(self._sku)

    @sku.setter
    def sku(self, value):
        self.set_int_attribute("sku", value)


class Financial(db.Model, BaseModel):
    __tablename__ = "financial"
    monthly_goal: Mapped[float] = mapped_column(primary_key=True)
    monthly_total: Mapped[float] = mapped_column(primary_key=True)
    reserve: Mapped[float] = mapped_column(primary_key=True)
    month_count: Mapped[int] = mapped_column(primary_key=True)
    last_reset: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))

    def __init__(self, **kwargs):
        self.monthly_goal = kwargs.get("monthly_goal", 0)
        self.monthly_total = kwargs.get("monthly_total", 0)
        self.reserve = kwargs.get("reserve", 0)
        self.month_count = kwargs.get("month_count", 0)
        self.last_reset = kwargs.get("last_reset")


class G0T0Guild(db.Model, BaseModel, IntAttributeMixin):
    __tablename__ = "guilds"
    _id: Mapped[int] = mapped_column("id", primary_key=True)
    max_level: Mapped[int]
    weeks: Mapped[int]
    last_reset: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))
    max_characters: Mapped[int]
    div_limit: Mapped[int]
    ping_announcement: Mapped[bool]
    handicap_cc: Mapped[int]
    reward_threshold: Mapped[int]
    weekly_announcement: Mapped[list[str]] = mapped_column(
        "weekly_announcement", ARRAY(String)
    )

    # User Roles
    _entry_role: Mapped[int] = mapped_column("entry_role")
    _member_role: Mapped[int] = mapped_column("member_role")
    _tier_2_role: Mapped[int] = mapped_column("tier_2_role")
    _tier_3_role: Mapped[int] = mapped_column("tier_3_role")
    _tier_4_role: Mapped[int] = mapped_column("tier_4_role")
    _tier_5_role: Mapped[int] = mapped_column("tier_5_role")
    _tier_6_role: Mapped[int] = mapped_column("tier_6_role")
    _admin_role: Mapped[int] = mapped_column("admin_role")
    _staff_role: Mapped[int] = mapped_column("staff_role")
    _bot_role: Mapped[int] = mapped_column("bot_role")
    _quest_role: Mapped[int] = mapped_column("quest_role")

    # Channels
    _application_channel: Mapped[int] = mapped_column("application_channel")
    _market_channel: Mapped[int] = mapped_column("market_channel")
    _announcement_channel: Mapped[int] = mapped_column("announcement_channel")
    _staff_channel: Mapped[int] = mapped_column("staff_channel")
    _help_channel: Mapped[int] = mapped_column("help_channel")
    _arena_board_channel: Mapped[int] = mapped_column("arena_board_channel")
    _exit_channel: Mapped[int] = mapped_column("exit_channel")
    _entrance_channel: Mapped[int] = mapped_column("entrance_channel")
    _activity_points_channel: Mapped[int] = mapped_column("activity_points_channel")
    _rp_post_channel: Mapped[int] = mapped_column("rp_post_channel")
    _dev_channels: Mapped[list[int]] = mapped_column(
        "dev_channels",
        ARRAY(BigInteger),
    )

    def __init__(self, **kwargs):
        self._id = DISCORD_GUILD_ID
        self.max_level = kwargs.get("max_level")
        self.weeks = kwargs.get("weeks")
        self.last_reset = datetime.datetime.fromisoformat(kwargs.get("last_reset"))
        self.max_characters = kwargs.get("max_characters")
        self.div_limit = kwargs.get("div_limit")
        self.weekly_announcement = kwargs.get("weekly_announcement")
        self.ping_announcement = kwargs.get("ping_announcement")
        self.handicap_cc = kwargs.get("handicap_cc")
        self.reward_threshold = kwargs.get("reward_threshold")

        self._entry_role = kwargs.get("entry_role")
        self._member_role = kwargs.get("member_role")
        self._tier_2_role = kwargs.get("tier_2_role")
        self._tier_3_role = kwargs.get("tier_3_role")
        self._tier_4_role = kwargs.get("tier_4_role")
        self._tier_5_role = kwargs.get("tier_5_role")
        self._tier_6_role = kwargs.get("tier_6_role")
        self._admin_role = kwargs.get("admin_role")
        self._staff_role = kwargs.get("staff_role")
        self._bot_role = kwargs.get("bot_role")
        self._quest_role = kwargs.get("quest_role")

        self._application_channel = kwargs.get("application_channel")
        self._market_channel = kwargs.get("market_channel")
        self._announcement_channel = kwargs.get("announcement_channel")
        self._staff_channel = kwargs.get("staff_channel")
        self._help_channel = kwargs.get("help_channel")
        self._arena_board_channel = kwargs.get("arena_board_channel")
        self._exit_channel = kwargs.get("exit_channel")
        self._entrance_channel = kwargs.get("entrance_channel")
        self._activity_points_channel = kwargs.get("activity_points_channel")
        self._rp_post_channel = kwargs.get("rp_post_channel")
        self._dev_channels = kwargs.get("dev_channels", [])

    @property
    def id(self) -> str:
        return str(self._id)

    @property
    def entry_role(self) -> str:
        return str(self._entry_role)

    @entry_role.setter
    def entry_role(self, value):
        self.set_int_attribute("_entry_role", value)

    @property
    def admin_role(self) -> str:
        return str(self._admin_role)

    @admin_role.setter
    def admin_role(self, value):
        self.set_int_attribute("_admin_role", value)

    @property
    def staff_role(self) -> str:
        return str(self._staff_role)

    @staff_role.setter
    def staff_role(self, value):
        self.set_int_attribute("_staff_role", value)

    @property
    def bot_role(self) -> str:
        return str(self._bot_role)

    @bot_role.setter
    def bot_role(self, value):
        self.set_int_attribute("_bot_role", value)

    @property
    def quest_role(self) -> str:
        return str(self._quest_role)

    @quest_role.setter
    def quest_role(self, value):
        self.set_int_attribute("_quest_role", value)

    @property
    def member_role(self) -> str:
        return str(self._member_role)

    @member_role.setter
    def member_role(self, value):
        self.set_int_attribute("_member_role", value)

    @property
    def tier_2_role(self) -> str:
        return str(self._tier_2_role)

    @tier_2_role.setter
    def tier_2_role(self, value):
        self.set_int_attribute("_tier_2_role", value)

    @property
    def tier_3_role(self) -> str:
        return str(self._tier_3_role)

    @tier_3_role.setter
    def tier_3_role(self, value):
        self.set_int_attribute("_tier_3_role", value)

    @property
    def tier_4_role(self) -> str:
        return str(self._tier_4_role)

    @tier_4_role.setter
    def tier_4_role(self, value):
        self.set_int_attribute("_tier_4_role", value)

    @property
    def tier_5_role(self) -> str:
        return str(self._tier_5_role)

    @tier_5_role.setter
    def tier_5_role(self, value):
        self.set_int_attribute("_tier_5_role", value)

    @property
    def tier_6_role(self) -> str:
        return str(self._tier_6_role)

    @tier_6_role.setter
    def tier_6_role(self, value):
        self.set_int_attribute("_tier_6_role", value)

    @property
    def application_channel(self) -> str:
        return str(self._application_channel)

    @application_channel.setter
    def application_channel(self, value):
        self.set_int_attribute("_application_channel", value)

    @property
    def market_channel(self) -> str:
        return str(self._market_channel)

    @market_channel.setter
    def market_channel(self, value):
        self.set_int_attribute("_market_channel", value)

    @property
    def announcement_channel(self) -> str:
        return str(self._announcement_channel)

    @announcement_channel.setter
    def announcement_channel(self, value):
        self.set_int_attribute("_announcement_channel", value)

    @property
    def staff_channel(self) -> str:
        return str(self._staff_channel)

    @staff_channel.setter
    def staff_channel(self, value):
        self.set_int_attribute("_staff_channel", value)

    @property
    def help_channel(self) -> str:
        return str(self._help_channel)

    @help_channel.setter
    def help_channel(self, value):
        self.set_int_attribute("_help_channel", value)

    @property
    def arena_board_channel(self) -> str:
        return str(self._arena_board_channel)

    @arena_board_channel.setter
    def arena_board_channel(self, value):
        self.set_int_attribute("_arena_board_channel", value)

    @property
    def exit_channel(self) -> str:
        return str(self._exit_channel)

    @exit_channel.setter
    def exit_channel(self, value):
        self.set_int_attribute("_exit_channel", value)

    @property
    def entrance_channel(self) -> str:
        return str(self._entrance_channel)

    @entrance_channel.setter
    def entrance_channel(self, value):
        self.set_int_attribute("_entrance_channel", value)

    @property
    def activity_points_channel(self) -> str:
        return str(self._activity_points_channel)

    @activity_points_channel.setter
    def activity_points_channel(self, value):
        self.set_int_attribute("_activity_points_channel", value)

    @property
    def rp_post_channel(self) -> str:
        return str(self._rp_post_channel)

    @rp_post_channel.setter
    def rp_post_channel(self, value):
        self.set_int_attribute("_rp_post_channel", value)

    @property
    def dev_channels(self) -> list[str]:
        return [str(c) for c in self._dev_channels] if self._dev_channels else []

    @dev_channels.setter
    def dev_channels(self, value):
        try:
            self._dev_channels = [int(c) for c in value]
        except:
            self._dev_channels = []


class RefMessage(db.Model, BaseModel, IntAttributeMixin):
    __tablename__ = "ref_messages"
    _guild_id: Mapped[int] = mapped_column("guild_id")
    _message_id: Mapped[int] = mapped_column("message_id", primary_key=True)
    _channel_id: Mapped[int] = mapped_column("channel_id")
    title: Mapped[str]

    def __init__(self, **kwargs):
        self._guild_id = kwargs.get("guild_id", DISCORD_GUILD_ID)
        self._message_id = kwargs.get("message_id")
        self._channel_id = kwargs.get("channel_id")
        self.title = kwargs.get("title")

    @property
    def channel_name(self):
        channels = get_channels_from_cache()
        return next(
            (c.get("name") for c in channels if c.get("id") == self.channel_id), None
        )

    @property
    def guild_id(self):
        return str(self._guild_id)

    @guild_id.setter
    def guild_id(self, value):
        self.set_int_attribute("_guild_id", value)

    @property
    def message_id(self):
        return str(self._message_id)

    @message_id.setter
    def message_id(self, value):
        self.set_int_attribute("_message_id", value)

    @property
    def channel_id(self):
        return str(self._channel_id)

    @channel_id.setter
    def channel_id(self, value):
        self.set_int_attribute("_channel_id", value)


class Character(db.Model, BaseModel):
    __tablename__ = "characters"
    id: Mapped[int] = mapped_column(primary_key=True)
    _guild_id: Mapped[int] = mapped_column(
        "guild_id", ForeignKey("players.guild_id"), nullable=False
    )
    _player_id: Mapped[int] = mapped_column(
        "player_id", ForeignKey("players.id"), nullable=False
    )
    _species: Mapped[int] = mapped_column(
        "species", ForeignKey("c_character_species.id"), nullable=False
    )
    credits: Mapped[int]
    _faction: Mapped[int] = mapped_column(
        "faction", ForeignKey("c_factions.id"), nullable=True
    )
    name: Mapped[str]
    level: Mapped[int]
    active: Mapped[bool]

    classes = relationship(
        "CharacterClass",
        lazy="select",
        primaryjoin="and_(Character.id == CharacterClass.character_id, CharacterClass.active == True)",
    )

    _species_record = relationship("Species", foreign_keys=[_species], lazy="joined")

    _faction_record = relationship("Faction")

    @property
    def faction(self):
        return self._faction_record

    @property
    def species(self):
        return self._species_record

    @property
    def player_id(self):
        return str(self._player_id)

    @property
    def guild_id(self):
        return str(self._guild_id)


class CharacterClass(db.Model, BaseModel):
    __tablename__ = "character_class"
    id: Mapped[int] = mapped_column(primary_key=True)
    character_id: Mapped[int] = mapped_column(
        ForeignKey("characters.id"), nullable=False
    )
    _primary_class: Mapped[int] = mapped_column(
        "primary_class", ForeignKey("c_character_class.id"), nullable=False
    )
    _archetype: Mapped[int] = mapped_column(
        "archetype", ForeignKey("c_character_archetype.id"), nullable=True
    )
    active: Mapped[bool]

    _primary_class_record = relationship(
        "PrimaryClass",
        foreign_keys=[_primary_class],
        lazy="joined",
    )

    _archetype_record = relationship(
        "Archetype", foreign_keys=[_archetype], lazy="joined"
    )

    @property
    def primary_class(self):
        return self._primary_class_record

    @property
    def archetype(self):
        return self._archetype_record


class Player(db.Model, BaseModel, MemberAttributeMixin):
    __tablename__ = "players"
    _id: Mapped[int] = mapped_column("id", primary_key=True)
    cc: Mapped[int]
    div_cc: Mapped[int]
    _guild_id: Mapped[int] = mapped_column("guild_id", primary_key=True)
    points: Mapped[int]
    activity_points: Mapped[int]
    handicap_amount: Mapped[int]
    _statistics: Mapped[str] = mapped_column("statistics")

    characters = relationship(
        "Character",
        lazy="select",
        primaryjoin="and_(Player._id == Character._player_id, Player._guild_id == Character._guild_id, Character.active == True)",
    )

    __table_args__ = (db.PrimaryKeyConstraint("id", "guild_id"),)

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.guild_id = kwargs.get("guild_id", DISCORD_GUILD_ID)
        self.cc = kwargs.get("cc")
        self.div_cc = kwargs.get("div_cc")
        self.points = kwargs.get("points")
        self.activity_points = kwargs.get("activity_points")
        self.handicap_amount = kwargs.get("handicap_amount")
        self.statistics = kwargs.get("statistics", {})

    @property
    def id(self):
        return str(self._id)

    @property
    def guild_id(self):
        return str(self._guild_id)

    @property
    def member(self):
        return self.get_member_attribute(self.id)

    @hybrid_property
    def statistics(self):
        try:
            return json.loads(self._statistics)
        except:
            return {}

    @statistics.setter
    def stats(self, value):
        self.statistics = json.dumps(value)


class Log(db.Model, BaseModel, IntAttributeMixin, MemberAttributeMixin):
    __tablename__ = "log"
    id: Mapped[int] = mapped_column(primary_key=True)
    _activity: Mapped[int] = mapped_column(
        "activity", ForeignKey("c_activity.id"), nullable=False
    )
    notes: Mapped[str]
    character_id: Mapped[int] = mapped_column(
        ForeignKey("characters.id"), nullable=True
    )
    _player_id: Mapped[int] = mapped_column("player_id")
    _author: Mapped[int] = mapped_column("author")
    _guild_id: Mapped[int] = mapped_column("guild_id")
    cc: Mapped[int]
    credits: Mapped[int]
    renown: Mapped[int]
    _faction: Mapped[int] = mapped_column(
        "faction", ForeignKey("c_factions.id"), nullable=True
    )
    invalid: Mapped[bool]
    created_ts: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))

    _activity_record = relationship("Activity")
    _faction_record = relationship("Faction")
    _character_record = relationship("Character")

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self._activity = kwargs.get("activity")
        self.notes = kwargs.get("notes")
        self.character_id = kwargs.get("character_id")
        self._player_id = kwargs.get("character_id")
        self._author = kwargs.get("author")
        self._guild_id = kwargs.get("guild_id")
        self.cc = kwargs.get("cc")
        self.credits = kwargs.get("credits")
        self.renown = kwargs.get("renown")
        self._faction = kwargs.get("faction")
        self.invalid = kwargs.get("invalid")
        self.created_ts = kwargs.get("created_ts")

    @property
    def activity(self):
        return self._activity_record

    @activity.setter
    def activity(self, value):
        self.set_int_attribute("_activity", value)

    @property
    def faction(self):
        return self._faction_record

    @faction.setter
    def faction(self, value):
        self.set_int_attribute("_faction", value)

    @property
    def guild_id(self):
        return self._guild_id

    @guild_id.setter
    def guild_id(self, value):
        self.set_int_attribute("_guild_id", value)

    @property
    def member(self):
        return self.get_member_attribute(self.player_id)

    @property
    def author(self):
        return self.get_member_attribute(str(self._author))

    @property
    def character(self):
        return self._character_record

    @property
    def player_id(self):
        return str(self._player_id)

    @player_id.setter
    def player_id(self, value):
        self.set_int_attribute("_player_id", value)


class BotMessage(BaseModel):
    def __init__(
        self,
        message_id: str,
        channel_id: str,
        channel_name: str,
        title: str,
        content: str,
        **kwargs,
    ):
        self.message_id = message_id
        self.channel_id = channel_id
        self.channel_name = channel_name
        self.content = content
        self.title = title
        self.pin = kwargs.get("pin", False)
        self.error = kwargs.get("error", "")
