from abc import ABC
from typing import Type

from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import scoped_session, Session

from constants import DISCORD_GUILD_ID
from models.G0T0 import *
from models.general import Content

import uuid


def normalize_id(id):
    """
    Normalize the ID to the appropriate type (int, uuid.UUID, or str).
    If the ID is a string, attempt to convert it to an int or UUID.
    """
    if isinstance(id, int):
        return id  # Already an integer
    if isinstance(id, uuid.UUID):
        return id  # Already a UUID
    if isinstance(id, str):
        try:
            # Try converting to an integer
            return int(id)
        except ValueError:
            pass
        try:
            # Try converting to a UUID
            return uuid.UUID(id)
        except ValueError:
            pass
    # If all conversions fail, return the string as-is
    return id


class ResoluteCache(ABC):
    initialized: bool = False
    cache = {}

    def __init__(self):
        self.cache = {}

    def initialize(self, force: bool = False):
        db: SQLAlchemy = current_app.config.get("DB")
        if not self.initialized or force:
            # Objects
            self.update(db.session, G0T0Guild)
            self.update(db.session, RefMessage)
            self.update(db.session, Activity)
            self.update(db.session, ActivityPoints)
            self.update(db.session, CodeConversion)
            self.update(db.session, LevelCost)
            self.update(db.session, Content)
            self.update(db.session, Power)
            self.update(db.session, Species)
            self.update(db.session, PrimaryClass)
            self.update(db.session, Archetype)
            self.update(db.session, Equipment)
            self.update(db.session, EnhancedItem)
            self.update(db.session, Feat)
            self.update(db.session, Background)

            # Categories
            self.update(db.session, ContentSource)
            self.update(db.session, PowerAlignment)
            self.update(db.session, PowerType)
            self.update(db.session, EquipmentCategory)
            self.update(db.session, EquipmentSubCategory)
            self.update(db.session, EnhancedItemType)
            self.update(db.session, EnhancedItemSubtype)
            self.initialized = True

    def contains(self, cls):
        return cls in self.cache

    def fetch(self, cls, id=None):
        if id:
            norm_id = normalize_id(id)
            return next((i for i in self.cache.get(cls) if i.id == norm_id), None)
        return self.cache.get(cls)

    def update(self, session: scoped_session[Session], cls: Type):
        if cls is G0T0Guild:
            self.cache[G0T0Guild] = (
                session.query(G0T0Guild)
                .filter(G0T0Guild._id == int(DISCORD_GUILD_ID))
                .first()
            )
        elif cls is RefMessage:
            self.cache[RefMessage] = (
                session.query(RefMessage)
                .filter(RefMessage._guild_id == int(DISCORD_GUILD_ID))
                .all()
            )
        else:
            self.cache[cls] = session.query(cls).all()
