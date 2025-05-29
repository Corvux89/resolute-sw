from flask import Blueprint, current_app, redirect, request, session, url_for
from flask_login import login_user, logout_user
import jwt
from requests_oauthlib import OAuth2Session

from models.exceptions import NotFound, UnauthorizedAccessError

auth_blueprint = Blueprint("auth", __name__)


def redirect_dest(fallback):
    dest = request.args.get("next")
    return redirect(url_for(dest)) if dest else redirect(fallback)


@auth_blueprint.route("/login/<provider>")
def login(provider):
    provider_data = current_app.config["OAUTH2_PROVIDERS"].get(provider)

    if provider_data is None:
        raise NotFound 

    data = {"redirect": request.args.get("next", "homepage")}

    oauth_session = OAuth2Session(
        client_id=provider_data["client_id"],
        state=jwt.encode(data, current_app.config["SECRET_KEY"], algorithm="HS256"),
        scope=provider_data["scopes"],
        redirect_uri=url_for("auth.callback", provider=provider, _external=True),
    )

    authorization_url, state = oauth_session.authorization_url(
        provider_data["authorize_url"]
    )
    session["OAUTH2_STATE"] = state

    return redirect(authorization_url)


@auth_blueprint.route("/callback/<provider>")
def callback(provider):
    provider_data = current_app.config["OAUTH2_PROVIDERS"].get(provider)

    if provider_data is None:
        raise NotFound

    try:
        if request.args["state"] != session.get("OAUTH2_STATE"):
            raise UnauthorizedAccessError()

        if "code" not in request.args:
            raise UnauthorizedAccessError()

        oauth_session = OAuth2Session(
            client_id=provider_data["client_id"],
            state=session.get("OAUTH2_STATE"),
            redirect_uri=url_for("auth.callback", provider=provider, _external=True),
        )

        token = oauth_session.fetch_token(
            provider_data["token_url"],
            client_secret=provider_data["client_secret"],
            authorization_response=request.url,
        )

        if not (access_token := token.get("access_token")):
            raise UnauthorizedAccessError()

        session["OAUTH2_TOKEN"] = access_token
        user = current_app.discord.fetch_user()

        login_user(user)
        data = jwt.decode(
            session.get("OAUTH2_STATE"),
            current_app.config["SECRET_KEY"],
            algorithms=["HS256"],
        )

    except Exception as e:
        print(f"Issue with callback: {e}")
        return redirect(url_for("homepage"))

    return redirect(data.get("redirect", url_for("homepage")))


@auth_blueprint.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("homepage"))


