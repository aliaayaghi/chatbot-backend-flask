from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from app.database import init_db
from app.routes.chats import chats_bp
from app.routes.auth import auth_bp, init_auth
from datetime import timedelta
import os

load_dotenv()


def create_app():
    app = Flask(__name__)

    # JWT configuration
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    app.config["JWT_HEADER_NAME"] = "Authorization"
    app.config["JWT_HEADER_TYPE"] = "Bearer"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)
    

    # Allow requests from your Next.js frontend
    CORS(app, resources={r"/*": {"origins": os.getenv("FRONTEND_URL")}})

    # Initialize extensions
    JWTManager(app)
    init_db(app)
    init_auth(app)

    # Register blueprints
    app.register_blueprint(chats_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api")

    return app