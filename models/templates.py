from typing import Any, Dict, Optional

from fastapi import Request, HTTPException
from fastapi.templating import Jinja2Templates
from starlette.responses import Response

from helpers.auth_helpers import is_admin
from models.cache import ResoluteCache
from models.exceptions import Forbidden
from models.resolute import ContentSource, PowerAlignment, PowerType


def build_select_option(objects: [], value_attr: str = "id", label_attr: str = "value"):
    return [
        {"value": getattr(o, value_attr), "label": getattr(o, label_attr)}
        for o in objects
    ]


def build_generic_option(values: []):
    return [{"value": v, "label": v} for v in values]


class ResoluteJinja(Jinja2Templates):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set up Jinja2 environment globals
        self.env.globals.update({"current_user": None, "request": None})

        # Add custom filter to convert None to null
        self.env.filters["null_if_none"] = lambda x: "" if x is None else x

        # Configure Jinja2 to render None as null globally
        self.env.finalize = lambda x: "" if x is None else x

    async def TemplateResponse(
        self,
        name: str,
        context: Dict[str, Any],
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        media_type: Optional[str] = None,
        background=None,
        **kwargs,
    ) -> Response:
        """
        Override TemplateResponse to automatically inject current_user and request
        """

        request: Request = context.get("request")
        current_user = None

        if request and hasattr(request.app, "discord"):
            try:
                current_user = await request.app.discord.user(request)
            except (HTTPException, Exception):
                current_user = None

        context.update({"current_user": current_user, "request": request})

        admin = False
        try:
            await is_admin(request)
            admin = True
        except (Forbidden, Exception):
            admin = False

        # Options setup
        options = {}
        cache: ResoluteCache = request.app.cache
        for attempt in range(2):
            try:
                options["power-type"] = build_select_option(
                    cache.fetch(PowerType, db=request.app.db)
                )
                options["alignment"] = build_select_option(
                    cache.fetch(PowerAlignment, db=request.app.db)
                )
                options["content-source"] = build_select_option(
                    cache.fetch(ContentSource, db=request.app.db), "id", "name"
                )
                options["sizes"] = build_generic_option(
                    ["Tiny", "Small", "Medium", "Large", "Huge", "Gargantuan"]
                )
                options["stats"] = build_generic_option(
                    [
                        "Strength",
                        "Dexterity",
                        "Constitution",
                        "Intelligence",
                        "Wisdom",
                        "Charisma",
                        "Any",
                    ]
                )
                break
            except Exception as e:
                request.app.db.rollback()

                if attempt == 1:
                    options = {
                        "power-type": [],
                        "alignment": [],
                        "content-source": [],
                        "sizes": [],
                        "stats": [],
                    }

        if add_options := kwargs.get("options"):
            options.update(add_options)

        self.env.globals.update(
            {
                "current_user": current_user,
                "request": request,
                "is_admin": admin,
                "options": options,
            }
        )

        # Call the parent TemplateResponse method
        return super().TemplateResponse(
            name=name,
            context=context,
            status_code=status_code,
            headers=headers,
            media_type=media_type,
            background=background,
        )
