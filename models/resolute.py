import uuid
from typing import Optional, Type
from pydantic import BaseModel
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY, BIGINT
from sqlalchemy.ext.declarative import DeclarativeMeta

from models.general import IntAttributeMixin, render_markdown

base = declarative_base()


class GenericCategory(base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    value = Column(String)        

# --------------------------- #
# Categories
# --------------------------- #
class ContentSource(base):
    __tablename__ = "c_content_source"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)        
    abbreviation = Column(String, nullable=True)

class ContentSourceSchema(BaseModel):
    id: int
    name: str
    abbreviation: Optional[str] = None

    class Config:
        orm_mode=True

# --------------------------- #
# Objects
# --------------------------- #
class ResoluteGuild(base, IntAttributeMixin):
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
    
    

class WebContent(base):
    __tablename__="web_content"
    key = Column(String, primary_key=True, index=True)
    id = Column(String, index=True, unique=True)
    content = Column(String)
    title = Column(String)

    @property
    def html_content(self):
        return render_markdown(self.content)


class WebContentSchema(BaseModel):
    key: str
    id: str
    content: str
    title: str

    class Config:
        orm_mode=True

class WebContentFullSchema(WebContentSchema):
    html_content: str

class Species(base):
    __tablename__ = "c_character_species"
    id = Column(Integer, primary_key=True, index=True)
    value = Column(String)
    skin_options = Column(String, nullable=True)
    hair_options = Column(String, nullable=True)
    eye_options = Column(String, nullable=True)
    distinctions = Column(String, nullable=True)
    height_average = Column(String, nullable=True)
    height_mod = Column(String, nullable=True)
    weight_average = Column(String, nullable=True)
    weight_mod = Column(String, nullable=True)
    homeworld = Column(String, nullable=True)
    flavortext = Column(String, nullable=True)
    traits = Column(String, nullable=True)
    language = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    size = Column(String, nullable=True)
    _source = Column("source", Integer, ForeignKey("c_content_source.id"), nullable=True)

    source = relationship("ContentSource", lazy="joined")

    @property
    def html_flavortext(self):
        return render_markdown(self.flavortext)
    
    @property
    def html_traits(self):
        return render_markdown(self.traits)
    
class SpeciesSchema(BaseModel):
    id: int
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

    class Config:
        orm_mode=True


class Feature(base):
    __tablename__ = "feats"
    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4())
    name = Column(String, nullable=False)
    prerequisite = Column(String, nullable=True)
    text = Column(String, nullable = True)
    _source = Column("source", Integer, ForeignKey("c_content_source.id"), nullable=True)
    attributes = Column(ARRAY(String), nullable=True, default=[])

    source = relationship("ContentSource", lazy="joined")

    @property
    def html_text(self):
        return render_markdown(self.text)

class FeatureSchema(BaseModel):
    id: uuid.UUID
    name: str
    prerequisite: str
    text: str
    source: ContentSourceSchema
    html_text: str

    class Config:
        orm_mode=True
