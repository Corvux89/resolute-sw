from abc import ABC
from typing import Type

from fastapi import FastAPI
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import scoped_session, Session

from constants import DISCORD_GUILD_ID
from models import *

import uuid

from models.resolute import *


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

    def __init__(self, app: FastAPI):
        self.cache = {}
        self.initialized = False

        if app:
            self.initialize(app)

    def initialize(self, app: FastAPI, force: bool = False):
        db = app.db
        if not self.initialized or force:
            # Objects
            self._update(db, ResoluteGuild)
            self._update(db, Feature)
            self._update(db, WebContent)
            self._update(db, Species)
            self._update(db, PrimaryClass)

            # Categories
            self._update(db, ContentSource)
            self._update(db, PowerAlignment)
            self._update(db, PowerType)
            self.initialized = True

    def contains(self, cls):
        return cls in self.cache

    def fetch(self, cls, id=None, **kwargs):
        if id:
            norm_id = normalize_id(id)
            obj =  next((i for i in self.cache.get(cls) if i.id == norm_id), None)

            if not obj and (db := kwargs.get('db', None)):
                obj = db.query(cls).filter(cls.id == norm_id).first()

            return obj

        return self.cache.get(cls)

    def _update(self, session: scoped_session[Session], cls: Type):
        if cls is ResoluteGuild:
            self.cache[ResoluteGuild] = (
                session.query(ResoluteGuild)
                .filter(ResoluteGuild._id == int(DISCORD_GUILD_ID))
                .first()
            )
        else:
            self.cache[cls] = session.query(cls).all()

    def update(self, session: scoped_session[Session], cls: Type):
        if cls in self.cache:
            self._update(session, cls)