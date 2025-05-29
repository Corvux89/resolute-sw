import os
from flask import Blueprint, current_app, render_template, send_from_directory, url_for
from flask_sqlalchemy import SQLAlchemy

from models.exceptions import NotFound
from models.general import Content

resolute_blueprint = Blueprint("resolute", __name__)


@resolute_blueprint.route('/house_rules', methods=["GET"])
def house_rules():
    db: SQLAlchemy = current_app.config.get("DB")
    content: Content = db.session.query(Content).filter(Content.key == "house-rules").first()
    return render_template("shell.html", content=content)

@resolute_blueprint.route('/content_rulings', methods=["GET"])
def content_rulings():
    content = Content(key="content-rulings", content="Coming Soon")
    return render_template("shell.html", content=content)

@resolute_blueprint.route('/errata', methods=["GET"])
def errata():
    pdf_url = url_for("resolute.pdf_link", key="errata")
    return render_template("shell.html", pdf_url=pdf_url)

@resolute_blueprint.route('/pdf/<key>')
def pdf_link(key):
    if key=="errata":
        return send_from_directory(
            os.path.join('blueprints', 'Resolute'),
            "Resolute Errata Document - The Homebrewery.pdf"
            )
    
    raise NotFound()
