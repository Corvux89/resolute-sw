import uuid
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY, BIGINT

from models.general import IntAttributeMixin, render_markdown

base = declarative_base()


class GenericCategory(base):
    __abstract__ = True
    __exceptions__: List[str] = []
    id = Column(Integer, primary_key=True, index=True)
    value = Column(String)

class GenericObject(base):
    __abstract__ = True
    __exceptions__: List[str] = []

class OptionalColumn(Column):
    def __init__(self, **kwargs):
        kwargs.setdefault('type_', String)
        kwargs.setdefault('nullable', True)
        super().__init__(**kwargs)

class GenericSchema(BaseModel):  
    class Config:
        from_attributes=True

class GenericCategorySchema(GenericSchema):
    id: int
    value: str

# --------------------------- #
# Categories
# --------------------------- #
class ContentSource(GenericObject):
    __tablename__ = "c_content_source"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)        
    abbreviation = Column(String, nullable=True)

class ContentSourceSchema(GenericSchema):
    id: int
    name: str
    abbreviation: Optional[str] = None

class PowerAlignment(GenericCategory):
    __tablename__ = "c_power_alignment"

class PowerAlignmentSchema(GenericCategorySchema):
    pass

class PowerType(GenericCategory):
    __tablename__ = "c_power_type"

class PowerTypeSchema(GenericCategorySchema):
    pass

# --------------------------- #
# Objects
# --------------------------- #
class ResoluteGuild(GenericObject, IntAttributeMixin):
    __tablename__ = "guilds"
    _id =  Column("id", BIGINT, primary_key=True, index=True)
    _admin_role = Column("admin_role", BIGINT, nullable=True)

    @property
    def id(self): 
        return str(self._id)
    
    @property
    def admin_role(self):
        return str(self._admin_role)
    
    @admin_role.setter
    def admin_role(self, value):
        self.set_int_attribute("_admin_role", value)
    
    

class WebContent(GenericObject):
    __tablename__="web_content"
    __exceptions__ = ["id", "key"]
    key = Column(String, primary_key=True, index=True)
    id = Column(String, index=True, unique=True)
    content = Column(String)

    @property
    def html_content(self):
        return render_markdown(self.content)


class WebContentSchema(GenericSchema):
    key: str
    id: str
    content: str

class WebContentFullSchema(WebContentSchema):
    html_content: str

class Species(GenericObject):
    __tablename__ = "c_character_species"
    __exceptions__ = ["id"]
    id = Column(Integer, primary_key=True, index=True)
    value = Column(String)
    skin_options = OptionalColumn()
    hair_options = OptionalColumn()
    eye_options = OptionalColumn()
    distinctions = OptionalColumn()
    height_average = OptionalColumn()
    height_mod = OptionalColumn()
    weight_average = OptionalColumn()
    weight_mod = OptionalColumn()
    homeworld = OptionalColumn()
    flavortext = OptionalColumn()
    traits = OptionalColumn()
    language = OptionalColumn()
    image_url = OptionalColumn()
    size = OptionalColumn()
    _source = Column("source", Integer, ForeignKey("c_content_source.id"), nullable=True)

    source = relationship("ContentSource", lazy="joined")

    @property
    def html_flavortext(self):
        return render_markdown(self.flavortext)
    
    @property
    def html_traits(self):
        return render_markdown(self.traits)
    
class SpeciesSchema(GenericSchema):
    id: Optional[int] = None
    value: str
    skin_options: Optional[str] = None
    hair_options: Optional[str] = None
    eye_options: Optional[str] = None
    distinctions: Optional[str] = None
    height_average: Optional[str] = None
    height_mod: Optional[str] = None
    weight_average: Optional[str] = None
    weight_mod: Optional[str] = None
    homeworld: Optional[str] = None
    flavortext: Optional[str] = None
    html_flavortext: Optional[str] = None
    traits: Optional[str] = None
    html_traits: Optional[str] = None
    language: Optional[str] = None
    image_url: Optional[str] = None
    size: Optional[str] = None
    source: Optional[ContentSourceSchema] = None

class PrimaryClass(GenericObject):
    __tablename__ = "c_character_class"
    __exceptions__ = ["id"]

    id = Column(Integer, primary_key=True, index=True)
    value = Column(String)
    summary = OptionalColumn()
    primary_ability = OptionalColumn()
    flavortext = OptionalColumn()
    level_changes = OptionalColumn()
    hit_die = OptionalColumn(type_=Integer)
    level_1_hp = OptionalColumn()
    higher_hp = OptionalColumn()
    armor_prof = OptionalColumn()
    weapon_prof = OptionalColumn()
    tool_prof = OptionalColumn()
    saving_throws = OptionalColumn()
    skill_choices = OptionalColumn()
    starting_equipment = OptionalColumn()
    features = OptionalColumn()
    archetype_flavor = OptionalColumn()
    image_url = OptionalColumn()
    _caster_type = Column("caster_type", ForeignKey("c_power_type.id"), nullable=True)
    _source = Column("source", Integer, ForeignKey("c_content_source.id"), nullable=True)

    source = relationship("ContentSource")
    caster_type = relationship("PowerType")

    @property
    def html_flavortext(self):
        return render_markdown(self.flavortext)
    
    @property
    def html_features(self):
        return render_markdown(self.features)
    
    @property
    def html_level_table(self):
        return render_markdown(self.level_changes)
    
    @property
    def html_starting_equip(self):
        return render_markdown(self.starting_equipment)
    
class PrimaryClassSchema(GenericSchema):
    id: Optional[int] = None
    value: str
    summary: Optional[str] = None
    primary_ability: Optional[str] = None
    flavortext: Optional[str] = None
    html_flavortext: Optional[str] = None
    level_changes: Optional[str] = None
    html_level_table: Optional[str] = None
    hit_die: Optional[int] = None
    level_1_hp: Optional[str] = None
    higher_hp: Optional[str] = None
    armor_prof: Optional[str] = None
    weapon_prof: Optional[str] = None
    tool_prof: Optional[str] = None
    saving_throws: Optional[str] = None
    skill_choices: Optional[str] = None
    starting_equipment: Optional[str] = None
    html_starting_equip: Optional[str] = None
    features: Optional[str] = None
    html_features: Optional[str] = None
    archetype_flavor: Optional[str] = None
    image_url: Optional[str] = None
    source: Optional[ContentSourceSchema] = None
    caster_type: Optional[PowerTypeSchema] = None    

class Feature(GenericObject):
    __tablename__ = "feats"
    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4())
    name = Column(String)
    prerequisite = OptionalColumn()
    text = OptionalColumn()
    _source = Column("source", Integer, ForeignKey("c_content_source.id"), nullable=True)
    attributes = OptionalColumn(type_=ARRAY(String), default=[])

    source = relationship("ContentSource", lazy="joined")

    @property
    def html_text(self):
        return render_markdown(self.text)

class FeatureSchema(GenericSchema):
    id: uuid.UUID
    name: str
    prerequisite: str
    text: str
    source: ContentSourceSchema
    html_text: str
