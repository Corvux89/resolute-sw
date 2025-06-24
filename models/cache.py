from abc import ABC
from typing import Type, TypedDict, Dict, Optional

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import scoped_session, Session

from constants import DISCORD_GUILD_ID
from models import *

import uuid

from models.resolute import *

# Global cache instance - will be set by ResoluteCache itself
_global_cache_instance = None

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

class SchemaMap(TypedDict):
    db_object: Type
    schema: Optional[Type] = None

OBJECT_MAP: Dict[Type, SchemaMap] = {
    ResoluteGuild: {'db_object': ResoluteGuild},
    WebContent: {'db_object': WebContent, 'schema': WebContentFullSchema},
    Species: {'db_object': Species, 'schema': SpeciesSchema},
    PrimaryClass: {'db_object': PrimaryClass, 'schema': PrimaryClassSchema},
    Archetype: {'db_object': Archetype, 'schema': ArchetypeSchema},
    Feature: {'db_object': Feature, 'schema': FeatureSchema},
    Background: {'db_object': Background, 'schema': BackgroundSchema},
    Maneuver: {'db_object': Maneuver, 'schema': ManeuverSchema}
}

CATEGORY_MAP: Dict[Type, SchemaMap] = {
    ContentSource: {'db_object': ContentSource, 'schema': ContentSourceSchema},
    PowerAlignment: {'db_object': PowerAlignment, 'schema': PowerAlignmentSchema},
    PowerType: {'db_object': PowerType, 'schema': PowerTypeSchema},
    ManeuverType: {'db_object': ManeuverType, 'schema': ManeuverTypeSchema},
}

OBJECT_MAP.update(CATEGORY_MAP)

class ResoluteCache(ABC):
    initialized: bool = False
    cache = {}

    def __init__(self, app: FastAPI):
        self.cache = {}
        self.initialized = False

        if app:
            self.initialize(app)
        
        # Automatically register this instance as the global cache
        self._set_global_instance()

    @classmethod
    def get_global_instance(cls):
        """Get the global cache instance"""
        return _global_cache_instance
    
    @classmethod
    def is_global_available(cls) -> bool:
        """Check if global cache is available"""
        return _global_cache_instance is not None
    
    @classmethod
    def is_global_initialized(cls) -> bool:
        """Check if global cache is available and initialized"""
        return (_global_cache_instance is not None and 
                getattr(_global_cache_instance, 'initialized', False))
    
    def _set_global_instance(self):
        """Set this instance as the global cache"""
        global _global_cache_instance
        _global_cache_instance = self

    def initialize(self, app: FastAPI, force: bool = False):
        db = app.db
        if not self.initialized or force:
            for cls in OBJECT_MAP.keys():
                self._update(db, cls)
            self.initialized = True
    
    def contains(self, cls):
        return cls in self.cache

    def fetch(self, cls: Type, id=None, **kwargs):
        obj = None
        if id:
            norm_id = normalize_id(id)
            obj =  next((i for i in self.cache.get(cls) if i.id == norm_id), None)

            if not obj and (db := kwargs.get('db', None)):
                obj = db.query(cls).filter(cls.id == norm_id).first()

            return obj
        
        if name := kwargs.get('name'):
            return next((i for i in self.cache.get(cls) if name.lower() == i.name.lower()), None)

        if value := kwargs.get('value'):
            return next((i for i in self.cache.get(cls) if value.lower() == i.value.lower()), None)        
        
        if key := kwargs.get('key'):
            return next((i for i in self.cache.get(cls) if key.lower() == i.key.lower()), None)
        
        return self.cache.get(cls)
      
    def get_model(self, cls, schema: BaseModel):
        objects = self.fetch(cls)
        result = []
        
        for obj in objects:
            try:
                result.append(schema.model_validate(obj).model_dump())
            except Exception as e:
                continue

        return jsonable_encoder(result)

    def _update(self, session: scoped_session[Session], cls):
        if cls is ResoluteGuild:
            self.cache[ResoluteGuild] = (
                session.query(ResoluteGuild)
                .filter(ResoluteGuild._id == int(DISCORD_GUILD_ID))
                .first()
            )
        else:
            self.cache[cls] = session.query(cls).all()
        
        # Check if this class has a schema in OBJECT_MAP and update it
        if cls in OBJECT_MAP and 'schema' in OBJECT_MAP[cls]:
            schema = OBJECT_MAP[cls]['schema']
            self.cache[schema] = self.get_model(cls, schema)

    def update(self, session: scoped_session[Session], cls):
        if cls in self.cache:
            self._update(session, cls)
            # Global instance is automatically updated since it's the same object
    
    # Global cache convenience methods
    @classmethod
    def global_fetch(cls, model_cls, id=None, **kwargs):
        """Fetch from the global cache instance"""
        if _global_cache_instance:
            return _global_cache_instance.fetch(model_cls, id, **kwargs)
        return None
    
    @classmethod
    def global_contains(cls, model_cls) -> bool:
        """Check if the global cache contains a model class"""
        if _global_cache_instance:
            return _global_cache_instance.contains(model_cls)
        return False
    
    @classmethod
    def global_get_model(cls, model_cls, schema):
        """Get model from global cache instance"""
        if _global_cache_instance:
            return _global_cache_instance.get_model(model_cls, schema)
        return []
    
    @classmethod
    def global_update(cls, session, model_cls):
        """Update a model class in the global cache"""
        if _global_cache_instance:
            _global_cache_instance.update(session, model_cls)