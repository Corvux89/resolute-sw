import os

from flask import (
    Blueprint,
    Flask,
    current_app,
    redirect,
    render_template,
    request,
    jsonify,
    url_for,
)
from flask_login import login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, desc, asc, or_
from helpers.auth_helper import is_admin, is_admin
from helpers.general_helpers import (
    get_entitlements_from_cache,
    get_roles_from_cache,
)
from helpers.G0T0 import (
    log_search_filter,
    trigger_compendium_reload,
)
from models.discord import (
    DiscordEntitlement,
    DiscordMember,
    DiscordRole,
)
from models.exceptions import BadRequest, NotFound
from models.G0T0 import (
    Activity,
    ActivityPoints,
    Character,
    CodeConversion,
    Faction,
    Financial,
    LevelCost,
    Log,
    Player,
    Store,
)
from sqlalchemy.orm import joinedload


G0T0_blueprint = Blueprint("G0T0", __name__)
app = Flask(__name__)


@G0T0_blueprint.route("/", methods=["GET"])
@login_required
def main():
    if is_admin():
        tab_folder = "templates/G0T0/tabs"

        tabs = [
            f"/G0T0/tabs/{file}"
            for file in os.listdir(tab_folder)
            if file.endswith(".html")
        ]

        return render_template("G0T0/main.html", tabs=tabs)

    return redirect(url_for("G0T0.profile"))


@G0T0_blueprint.route("/profile", methods=["GET"])
@login_required
def profile():
    return render_template("G0T0/profile.html")


@G0T0_blueprint.route("/terms")
def terms():
    return render_template("G0T0/terms.html")


@G0T0_blueprint.route("/privacy")
def privacy():
    return render_template("G0T0/privacy.html")

@G0T0_blueprint.route("/api/logs/<int:guild_id>", methods=["GET"])
@is_admin
def get_logs(guild_id: int):
    db: SQLAlchemy = current_app.config.get("DB")
    limit = request.args.get("limit", default=None, type=int)
    query = (
        db.session.query(Log)
        .filter(Log._guild_id == guild_id)
        .join(Activity)
        .outerjoin(Faction)
        .outerjoin(Character)
        .options(
            joinedload(Log._activity_record),
            joinedload(Log._faction_record),
            joinedload(Log._character_record),
        )
    )

    if limit:
        query = query.limit(limit)

    logs: list[Log] = query.all()

    return jsonify(logs)


@G0T0_blueprint.route("/api/logs/<guild_id>", methods=["POST"])
@is_admin
def sort_logs(guild_id: int):
    db: SQLAlchemy = current_app.config.get("DB")
    query = (
        db.session.query(Log)
        .filter(Log._guild_id == guild_id)
        .join(Activity)
        .outerjoin(Faction)
        .outerjoin(Character)
        .options(
            joinedload(Log._activity_record),
            joinedload(Log._faction_record),
            joinedload(Log._character_record),
        )
    )

    draw = int(request.json.get("draw", 1))
    start = int(request.json.get("start", 0))
    length = int(request.json.get("length", 10))
    order = request.json.get("order", [])
    search_value = request.json.get("search", {}).get("value", "")
    column_index = int(order[0].get("column", 0)) if len(order) > 0 else 0
    column_dir = order[0].get("dir", "asc") if len(order) > 0 else "desc"

    recordsTotal = query.count()

    if search_value:
        query = query.filter(or_(*log_search_filter(search_value, guild_id)))

    # Query Sorting
    columns = [
        Log.id,
        Log.created_ts,
        None,
        None,
        Character.name,
        Activity.value,
        Log.notes,
        Log.invalid,
    ]
    column = columns[column_index]
    if column:
        query = (
            query.order_by(desc(column))
            if column_dir == "desc"
            else query.order_by(asc(column))
        )

    # Finish out the query
    filtered_records = query.count()
    logs = query.all()

    # Post query sorting because they're discord attributes
    if column_index == 2:  # Author
        logs = sorted(
            logs,
            key=lambda log: (
                DiscordMember(**log.author).member_display_name if log.author else "zzz"
            ),
            reverse=(column_dir == "desc"),
        )

    elif column_index == 3:  # Player
        logs = sorted(
            logs,
            key=lambda log: (
                DiscordMember(**log.member).member_display_name if log.member else "zzz"
            ),
            reverse=(column_dir == "desc"),
        )

    # Limit
    logs = logs[start : start + length]

    response = {
        "draw": draw,
        "recordsTotal": recordsTotal,
        "recordsFiltered": filtered_records,
        "data": logs,
    }

    return jsonify(response)

