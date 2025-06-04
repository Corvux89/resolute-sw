import json

from flask import Blueprint, current_app, render_template, request
from flask_sqlalchemy import SQLAlchemy

from helpers.general_helpers import perform_search
from models.exceptions import NotFound
from models.general import Content, ContentSource, PowerAlignment, PowerType

resolute_blueprint = Blueprint("resolute", __name__)


@resolute_blueprint.route("/house_rules", methods=["GET"])
def house_rules():
    return render_template("shell.html", content=_get_content())


@resolute_blueprint.route("/content_rulings", methods=["GET"])
def content_rulings():
    return render_template("shell.html", content=_get_content())


@resolute_blueprint.route("/errata", methods=["GET"])
def errata():
    return render_template("shell.html", content=_get_content())


@resolute_blueprint.route("/tech_powers", methods=["GET"])
def tech_powers():
    return render_template("powers.html", title="Tech Powers", options=_get_options())


@resolute_blueprint.route("/force_powers", methods=["GET"])
def force_powers():
    return render_template("powers.html", title="Force Powers", options=_get_options())

@resolute_blueprint.route("/search", methods=["GET"])
def search():
    query = request.args.get('q', '')

    results = perform_search(query)

    return render_template("search_results.html", query=query, results=results)
    pass


# --------------------------- #
# Private Methods
# --------------------------- #

def _get_content() -> Content:
    db: SQLAlchemy = current_app.config.get("DB")
    content: Content = (
        db.session.query(Content).filter(Content.key == request.path.replace("/","")).first()
    )

    if not content:
        raise NotFound()
    
    return content

def _get_options():
    db: SQLAlchemy = current_app.config.get("DB")
    options = {}

    power_type = db.session.query(PowerType).all()
    sources = db.session.query(ContentSource).all()
    alignments = db.session.query(PowerAlignment).all()

    options["power-type"] = [{"value": p.id, "label": p.value} for p in power_type]
    options["content-source"] = [{"value": s.id, "label": s.name} for s in sources]
    options["alignment"] = [{"value": a.id, "label": a.value} for a in alignments]

    return options