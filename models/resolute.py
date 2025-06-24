import uuid
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import BIGINT, ARRAY

from models.general import FeatureHyperlinkExtension, IntAttributeMixin, render_markdown

base = declarative_base()


class GenericCategory(base):
    __abstract__ = True
    __exceptions__: List[str] = []
    id = Column(Integer, primary_key=True, index=True)
    value = Column(String)

class GenericObject(base):
    __abstract__ = True
    __exceptions__: List[str] = []

def OptionalStringColumn(*args, **kwargs):
    kwargs.setdefault('nullable', True)
    return Column(String, *args, **kwargs)

def OptionalIntegerColumn(*args, **kwargs):
    kwargs.setdefault('nullable', True)
    return Column(Integer, *args, **kwargs)

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
    skin_options = OptionalStringColumn()
    hair_options = OptionalStringColumn()
    eye_options = OptionalStringColumn()
    distinctions = OptionalStringColumn()
    height_average = OptionalStringColumn()
    height_mod = OptionalStringColumn()
    weight_average = OptionalStringColumn()
    weight_mod = OptionalStringColumn()
    homeworld = OptionalStringColumn()
    flavortext = OptionalStringColumn()
    traits = OptionalStringColumn()
    language = OptionalStringColumn()
    image_url = OptionalStringColumn()
    size = OptionalStringColumn()
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
    summary = OptionalStringColumn()
    primary_ability = OptionalStringColumn()
    flavortext = OptionalStringColumn()
    level_changes = OptionalStringColumn()
    hit_die = OptionalIntegerColumn()
    level_1_hp = OptionalStringColumn()
    higher_hp = OptionalStringColumn()
    armor_prof = OptionalStringColumn()
    weapon_prof = OptionalStringColumn()
    tool_prof = OptionalStringColumn()
    saving_throws = OptionalStringColumn()
    skill_choices = OptionalStringColumn()
    starting_equipment = OptionalStringColumn()
    features = OptionalStringColumn()
    archetype_flavor = OptionalStringColumn()
    image_url = OptionalStringColumn()
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

class Archetype(GenericObject):
    __tablename__ = "c_character_archetype"
    __exceptions__ = ["id"]

    id = Column(Integer, primary_key=True, index=True)
    value = Column(String)
    parent = Column(Integer, ForeignKey("c_character_class.id"))
    flavortext = OptionalStringColumn()
    level_table = OptionalStringColumn()
    image_url = OptionalStringColumn()
    _caster_type = Column("caster_type", Integer, ForeignKey("c_power_type.id"), nullable=True)
    _source = Column("source", Integer, ForeignKey("c_content_source.id"), nullable=True)

    _parent_class = relationship("PrimaryClass", lazy="joined")
    caster_type = relationship("PowerType", lazy="joined")
    source = relationship("ContentSource", lazy="joined")

    @property
    def parent_name(self):
        return self._parent_class.value if self._parent_class else None
    
    @property
    def html_flavortext(self):
        return render_markdown(self.flavortext)
    
    @property
    def html_level_table(self):
        return render_markdown(self.level_table)
    
class ArchetypeSchema(GenericSchema):
    id: Optional[int] = None
    value: str
    parent: int
    parent_name: Optional[str] = None
    flavortext: Optional[str] = None
    html_flavortext: Optional[str] = None
    level_table: Optional[str] = None
    html_level_table: Optional[str] = None
    caster_type: Optional[PowerTypeSchema] = None
    source: Optional[ContentSourceSchema] = None

class Background(GenericObject):
    __tablename__ = "backgrounds"
    __exceptions__ = ["id"]

    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String)
    flavortext = OptionalStringColumn()
    flavor_name = OptionalStringColumn()
    flavor_description = OptionalStringColumn()
    skills = OptionalStringColumn()
    tools = OptionalStringColumn()
    languages = OptionalStringColumn()
    equipment = OptionalStringColumn()
    suggested_characteristics = OptionalStringColumn()
    feature_name = OptionalStringColumn()
    feature_text = OptionalStringColumn()
    feats = OptionalStringColumn()
    personality = OptionalStringColumn()
    ideal = OptionalStringColumn()
    flaw = OptionalStringColumn()
    bond = OptionalStringColumn()
    _source = Column("source", Integer, ForeignKey("c_content_source.id"), nullable=True)

    source = relationship("ContentSource", lazy="joined")

    @property
    def html_flavortext(self):
        return render_markdown(self.flavortext)
    
    @property
    def html_flavor_description(self):
        return render_markdown(self.flavor_description)
    
    @property
    def html_feats(self):
        return render_markdown(self.feats, [FeatureHyperlinkExtension()])

    @property
    def html_bond(self):
        return render_markdown(self.bond)

    @property
    def html_flaw(self):
        return render_markdown(self.flaw)

    @property
    def html_ideal(self):
        return render_markdown(self.ideal)
    
    @property
    def html_personality(self):
        return render_markdown(self.personality)

class BackgroundSchema(GenericSchema):
    id: Optional[uuid.UUID] = None
    name: str
    flavortext: Optional[str] = None
    html_flavortext: Optional[str] = None
    flavor_name: Optional[str] = None
    flavor_description: Optional[str] = None
    html_flavor_description: Optional[str] = None
    skills: Optional[str] = None
    tools: Optional[str] = None
    languages: Optional[str] = None
    equipment: Optional[str] = None
    suggested_characteristics: Optional[str] = None
    feature_name: Optional[str] = None
    feature_text: Optional[str] = None
    feats: Optional[str] = None
    html_feats: Optional[str] = None
    personality: Optional[str] = None
    html_personality: Optional[str] = None
    ideal: Optional[str] = None
    html_ideal: Optional[str] = None
    flaw: Optional[str] = None
    html_flaw: Optional[str] = None
    bond: Optional[str] = None
    html_bond: Optional[str] = None
    source: Optional[ContentSourceSchema] = None

class Feature(GenericObject):
    __tablename__ = "feats"
    __exceptions__ = ["id"]

    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    name =  Column(String)
    prerequisite = OptionalStringColumn()
    text = OptionalStringColumn()
    attributes = Column(ARRAY(String), nullable=True, default=[])
    _source = Column("source", Integer, ForeignKey("c_content_source.id"), nullable=True)

    source = relationship("ContentSource", lazy="joined")

    @property
    def html_text(self):
        return render_markdown(self.text)
    
class FeatureSchema(GenericSchema):
    id: Optional[uuid.UUID] = None
    name: str
    prerequisite: Optional[str] = None
    text: Optional[str] = None
    html_text: Optional[str] = None
    attributes: Optional[List[str]] = []
    source: Optional[ContentSourceSchema] = None


