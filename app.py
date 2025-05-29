from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy

from flask import Flask, redirect, render_template, request, session, url_for
from flask_bootstrap import Bootstrap
from flask_talisman import Talisman

from blueprints.auth import auth_blueprint
from blueprints.api import api_blueprint
from blueprints.Resolute import resolute_blueprint

from constants import (
    DB_URI,
    DISCORD_BOT_TOKEN,
    DISCORD_CLIENT_ID,
    DISCORD_REDIRECT_URI,
    DISCORD_SECRET_KEY,
    WEB_DEBUG,
    SECRET_KEY,
)
from helpers import get_csp
from helpers.error_handlers import register_handlers
from models.discord import DiscordBot
from models.exceptions import UnderConstruction
from models.general import CustomJSONProvider, User

app = Flask(__name__)

app.secret_key = SECRET_KEY
app.json = CustomJSONProvider(app)

app.config.update(DEBUG=WEB_DEBUG)
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False
app.config["DISCORD_CLIENT_ID"] = DISCORD_CLIENT_ID
app.config["DISCORD_REDIRECT_URI"] = DISCORD_REDIRECT_URI
app.config["DISCORD_CLIENT_SECRET"] = DISCORD_SECRET_KEY
app.config["DISCORD_BOT_TOKEN"] = DISCORD_BOT_TOKEN

# OAuth Providers
app.config["OAUTH2_PROVIDERS"] = {
    "discord": {
        "client_id": DISCORD_CLIENT_ID,
        "client_secret": DISCORD_SECRET_KEY,
        "authorize_url": "https://discord.com/oauth2/authorize",
        "token_url": "https://discord.com/api/oauth2/token",
        "scopes": ["identify", "email", "guilds"],
        "userinfo": {
            "url": "https://discord.com/api/users/@me",
            "id": lambda json: json["id"],
            "email": lambda json: json["email"],
            "username": lambda json: json["username"],
            "global_name": lambda json: (
                json["global_name"] if json["global_name"] != "" else json["username"]
            ),
            "avatar": lambda json: json["avatar"] if json["avatar"] != "" else None,
        },
    }
}

app.config["DB"] = db = SQLAlchemy(app)
app.config["login"] = login = LoginManager(app)
app.discord = DiscordBot(app)

@app.before_request
def require_login():
    # Allow unauthenticated access to login, static files, and OAuth callback
    allowed_routes = [
        'auth.login', 'auth.callback', 'static'
    ]

    if request.endpoint is None or request.endpoint in allowed_routes:
        return
    elif not current_user.is_authenticated:
        return redirect(url_for('auth.login', provider="discord", next=request.path))
    elif not current_user.is_admin:
        raise UnderConstruction()


@app.route("/")
def homepage():
    return render_template("home.html")

@login.user_loader
def load_user(_):
    print(request.headers)
    return app.discord.fetch_user()

@login.request_loader
def load_user_from_request(_):
    if "Authorization" in request.headers:
        session["OAUTH2_TOKEN"] = request.headers.get('Authorization').replace("Bearer ", "")
        user =  User.fetch_user('discord')
        return user


@login.unauthorized_handler
def unauthorized():
    return redirect(url_for("auth.login", provider="discord", next=request.path))


csp = get_csp()

Bootstrap(app)
talisman = Talisman(
    app,
    content_security_policy=csp,
    content_security_policy_nonce_in=["script-src", "style-src"],
)

app.register_blueprint(auth_blueprint, url_prefix="/auth")
app.register_blueprint(api_blueprint, url_prefix="/api")
app.register_blueprint(resolute_blueprint, url_prefix="/")
register_handlers(app)

if __name__ == "__main__":
    app.run()
