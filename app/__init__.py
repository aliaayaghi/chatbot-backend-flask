from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from app.database import init_db
from app.routes.chats import chats_bp

load_dotenv()


def create_app():
    app = Flask(__name__)

    # Allow requests from your Next.js frontend
    CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

    # Set up the database
    init_db(app)

    # Register the chats blueprint with a /api prefix
    # So all routes become /api/chats instead of just /chats
    app.register_blueprint(chats_bp, url_prefix="/api")

    return app