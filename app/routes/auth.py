from flask import Blueprint, request, jsonify, redirect, url_for, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from authlib.integrations.flask_client import OAuth
from app.database import db
from app.models.user import User
import os

auth_bp = Blueprint("auth", __name__)
bcrypt = Bcrypt()
oauth = OAuth()


def init_auth(app):
    """Call this from create_app to initialize bcrypt and oauth with the app"""
    bcrypt.init_app(app)
    oauth.init_app(app)

    # Register Google as an OAuth provider
    oauth.register(
        name="google",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )


# ─── Email / Password ─────────────────────────────────────────────────────────

@auth_bp.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data or not data.get("email") or not data.get("password"):
        return jsonify({ "error": "Email and password are required" }), 400

    # Check if email already exists
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({ "error": "Email already registered" }), 409

    # Hash the password — never store plain text
    password_hash = bcrypt.generate_password_hash(data["password"]).decode("utf-8")

    user = User(
        email=data["email"],
        password_hash=password_hash,
        auth_provider="email"
    )
    db.session.add(user)
    db.session.commit()

    # Create a token immediately so they're logged in after registering
    token = create_access_token(identity=str(user.id))

    return jsonify({
        "token": token,
        "user": user.to_dict()
    }), 201


@auth_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data or not data.get("email") or not data.get("password"):
        return jsonify({ "error": "Email and password are required" }), 400

    user = User.query.filter_by(email=data["email"]).first()

    # Check user exists and password matches the hash
    if not user or not user.password_hash:
        return jsonify({ "error": "Invalid credentials" }), 401

    if not bcrypt.check_password_hash(user.password_hash, data["password"]):
        return jsonify({ "error": "Invalid credentials" }), 401

    token = create_access_token(identity=str(user.id))

    return jsonify({
        "token": token,
        "user": user.to_dict()
    }), 200


# ─── Google OAuth ──────────────────────────────────────────────────────────────

@auth_bp.route("/auth/google")
def google_login():
    # Build the callback URL and redirect user to Google's login page
    redirect_uri = url_for("auth.google_callback", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@auth_bp.route("/auth/google/callback")
def google_callback():
    # Google redirects here after user logs in
    # Exchange the code Google sent for an actual token
    token = oauth.google.authorize_access_token()

    # Get the user's info from Google
    userinfo = token.get("userinfo")
    email = userinfo["email"]
    google_id = userinfo["sub"]  # Google's unique ID for this user

    # Check if this Google account already exists
    user = User.query.filter_by(google_id=google_id).first()

    if not user:
        # Check if this email exists with a different provider
        existing = User.query.filter_by(email=email).first()
        if existing:
            # Link the Google ID to the existing account
            existing.google_id = google_id
            existing.auth_provider = "google"
            db.session.commit()
            user = existing
        else:
            # Brand new user — create their account
            user = User(
                email=email,
                google_id=google_id,
                auth_provider="google"
            )
            db.session.add(user)
            db.session.commit()

    # Issue a JWT just like email login
    jwt_token = create_access_token(identity=str(user.id))

    # Redirect to frontend with token in URL
    # Frontend reads it and stores it
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    return redirect(f"{frontend_url}/auth/callback?token={jwt_token}")


# ─── Current User ──────────────────────────────────────────────────────────────

@auth_bp.route("/auth/me", methods=["GET"])
@jwt_required()
def get_me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({ "error": "User not found" }), 404
    return jsonify({ "user": user.to_dict() }), 200