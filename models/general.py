from __future__ import annotations

import markdown
import bleach
from typing import Type, TYPE_CHECKING
from xml.etree.ElementTree import Element
from markdown import Extension
from markdown.preprocessors import Preprocessor
from sqlalchemy.orm import DeclarativeMeta
from pydantic import BaseModel
import logging

from fastapi.encoders import jsonable_encoder

if TYPE_CHECKING:
    from models.cache import ResoluteCache

def custom_encoder(obj, **kwargs):
    if isinstance(obj, list):
        return [custom_encoder(item, **kwargs) for item in obj]
    
    if hasattr(obj, "__dict__"):
        # Use __dict__ instead of dir() for better performance
        # and only get non-private attributes that aren't callable
        filtered_dict = {}
        obj_dict = obj.__dict__
        obj_class = obj.__class__
        
        for k, v in obj_dict.items():
            if not k.startswith("_"):
                try:
                    filtered_dict[k] = jsonable_encoder(v, **kwargs)
                except Exception:
                    pass
        
        # Also check for properties (computed attributes)
        for attr_name in dir(obj_class):
            if (not attr_name.startswith("_") and 
                isinstance(getattr(obj_class, attr_name, None), property) and
                attr_name not in filtered_dict):
                try:
                    attr_value = getattr(obj, attr_name)
                    filtered_dict[attr_name] = jsonable_encoder(attr_value, **kwargs)
                except Exception:
                    pass
        
        return filtered_dict
    else:  
        return jsonable_encoder(obj, **kwargs)
    
class MonsterBlockExtension(Extension):
    def extendMarkdown(self, md):
        md.preprocessors.register(MonsterBlockPreProcessor(md), "monster_block", 175)

class HTTPError(BaseModel):
    detail: str
    class Config:
        json_schema_extra = {
            "eample": {"detail": "HTTPException Raised"}
        }


class MonsterBlockPreProcessor(Preprocessor):
    def run(self, lines):
        new_lines = []
        inside_monster_block = False
        monster_content = []

        for line in lines:
            if line.strip() == ":::monster":
                inside_monster_block = True
                monster_content = []
            elif line.strip() == ":::" and inside_monster_block:
                inside_monster_block = False
                new_lines.append(self.render_monster_block(monster_content))
            elif inside_monster_block:
                monster_content.append(line)
            else:
                new_lines.append(line)

        return new_lines

    def render_monster_block(self, content):
        html = '<div class="monster-block">'
        html += markdown.markdown("\n".join(content), extensions=["tables"])
        html += "</div>"
        return html

class FeatureHyperlinkPattern(markdown.inlinepatterns.Pattern):
    cache: ResoluteCache

    def __init__(self, cache: ResoluteCache, *args, **kwargs):
        super().__init__(r"\[\[(.*?)\]\]", *args, **kwargs)
        self.cache = cache

    def handleMatch(self, m):
        from models.resolute import Feature

        raw_text = m.group(0)  # Get the full match
        text = raw_text.strip("[]")  # Extract text manually

        feat: Feature = next(
            (
                f
                for f in self.cache.fetch(Feature)
                if f.name.lower() == text.lower()
            ),
            None,
        )

        if feat:
            el = Element("span")
            el.set("class", "info-link")
            el.set("data-name", feat.name)
            el.set("data-text", feat.html_text)
            el.text = text
            return el
        else:
            print(f"No feat found for: '{text}'")  # Debugging statement
            # Return plain text if no matching database item is found
            return markdown.util.AtomicString(text)


class FeatureHyperlinkExtension(Extension):
    cache: ResoluteCache

    def __init__(self, cache: ResoluteCache, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache = cache

    def extendMarkdown(self, md):
        md.inlinePatterns.register(FeatureHyperlinkPattern(self.cache), "hyperlink", 175)


def render_markdown(text: str, add_extension: list = []) -> str:
    if not text:
        return ""

    extensions = ["tables", "sane_lists", "toc", MonsterBlockExtension()]

    if add_extension:
        extensions += add_extension

    render = markdown.markdown(text, extensions=extensions)

    allowed_tags = frozenset(
        set(bleach.sanitizer.ALLOWED_TAGS)
        | {"div", "span", "table", "thead", "tbody", "tr", "th", "td", "p", "h1", "h2", "h3", "h4", "h5", "h6", "br"}
    )
    allowed_attributes = {"*": ["class", "id", "data-*", "data-name", "data-text"], "a": ["href", "title"]}

    sterilized =  bleach.clean(
        render, tags=allowed_tags, attributes=allowed_attributes, strip=True
    )

    return sterilized

class IntAttributeMixin:
    def set_int_attribute(self, attr_name, value):
        try:
            setattr(self, attr_name, value)
        except (ValueError, TypeError):
            setattr(self, attr_name, None)