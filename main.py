import os
from collections.abc import Callable
from functools import wraps
from typing import Any, ParamSpec, TypeVar, cast

from flask import Flask, Response, jsonify, request
from flask.typing import ResponseReturnValue
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager,
    get_jwt,
    verify_jwt_in_request,
)
from jwt import PyJWKClient

from db import db
from models import User

F = TypeVar("F", bound=Callable[..., Any])
P = ParamSpec("P")
T = TypeVar("T", bound=ResponseReturnValue)


def admin_required() -> Callable[[F], F]:
    def wrapper(fn: F) -> F:
        @wraps(fn)
        def decorator(*args: P.args, **kwargs: P.kwargs) -> T:
            verify_jwt_in_request()
            claims = get_jwt()
            # Auth0 custom claims usually require the full namespace URL
            roles = claims.get("https://social-insper.com/roles", [])
            if isinstance(roles, list) and "ADMIN" in roles:
                return fn(*args, **kwargs)
            return cast(
                "T",
                (jsonify(msg="Apenas ADMIN pode executar esta ação"), 403),
            )

        return cast("F", decorator)

    return wrapper


def user_required() -> Callable[[F], F]:
    def wrapper(fn: F) -> F:
        @wraps(fn)
        def decorator(*args: P.args, **kwargs: P.kwargs) -> T:
            verify_jwt_in_request()
            claims = get_jwt()
            roles = claims.get("https://social-insper.com/roles", [])
            if isinstance(roles, list) and (
                "USER" in roles or "ADMIN" in roles
            ):
                return fn(*args, **kwargs)
            return cast(
                "T",
                (jsonify(msg="Apenas USER pode executar esta ação"), 403),
            )

        return cast("F", decorator)

    return wrapper


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)

    postgres_user = os.environ.get("POSTGRES_USER", "appuser")
    postgres_password = os.environ.get("POSTGRES_PASSWORD", "apppass")
    postgres_url = os.environ.get("POSTGRES_URL", "localhost")
    db_uri = f"postgresql://{postgres_user}:{postgres_password}@{postgres_url}:5432/users"
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "SQLALCHEMY_DATABASE_URI", db_uri
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN")
    AUTH0_AUDIENCE = os.environ.get("AUTH0_AUDIENCE")

    if not AUTH0_DOMAIN or not AUTH0_AUDIENCE:
        raise ValueError("AUTH0_DOMAIN and AUTH0_AUDIENCE must be set")

    app.config["JWT_ALGORITHM"] = "RS256"
    app.config["JWT_DECODE_AUDIENCE"] = AUTH0_AUDIENCE
    app.config["JWT_DECODE_ISSUER"] = f"https://{AUTH0_DOMAIN}/"
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]

    jwt_manager = JWTManager(app)
    db.init_app(app)

    jwks_client = PyJWKClient(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json")

    @jwt_manager.decode_key_loader
    def decode_key_loader(jwks_header, jwks_payload):
        # print(request.headers.get("Authorization").split(" ")[1])
        signing_key = jwks_client.get_signing_key_from_jwt(
            request.headers.get("Authorization").split(" ")[1]
        )

        return signing_key.key

    @app.route("/users", methods=["POST"])
    @admin_required()
    def create_user() -> tuple[Response, int]:
        data = request.json
        user = User(name=data["name"], email=data["email"])
        db.session.add(user)
        db.session.commit()
        return jsonify(
            {"id": str(user.id), "name": user.name, "email": user.email}
        ), 201

    @app.route("/users/<uuid:user_id>", methods=["GET"])
    @user_required()
    def get_user(user_id) -> tuple[Response, int]:
        user = User.query.get_or_404(user_id)
        return jsonify(
            {"id": str(user.id), "name": user.name, "email": user.email}
        ), 200

    @app.route("/users/<string:email>/email", methods=["GET"])
    @user_required()
    def get_user_by_email(email: str) -> tuple[Response, int]:
        user = User.query.filter_by(email=email).first_or_404()
        return jsonify(
            {"id": str(user.id), "name": user.name, "email": user.email}
        ), 200

    @app.route("/users/<uuid:user_id>", methods=["DELETE"])
    @admin_required()
    def delete_user(user_id) -> tuple[str, int]:
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return "", 204

    @app.route("/users", methods=["GET"])
    @user_required()
    def list_users() -> tuple[Response, int]:
        users = User.query.all()
        user_list = [
            {"id": str(user.id), "name": user.name, "email": user.email}
            for user in users
        ]
        return jsonify(user_list), 200

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
