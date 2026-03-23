from flask_sqlalchemy import SQLAlchemy
import os

# Create one single db instance
# This gets imported by everything that needs the database
db = SQLAlchemy()


def init_db(app):
    # Tell SQLAlchemy where the database file lives
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

    # Don't send a signal every time data changes (saves memory)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,        # tests connection before using it
        "pool_recycle": 300,          # recycle connections every 5 minutes
        "pool_size": 5,               # max 5 connections in the pool
        "max_overflow": 2,            # allow 2 extra connections if needed
    }

    # Connect the db instance to this Flask app
    db.init_app(app)

    # Create all tables if they don't exist yet
    with app.app_context():
        from app.models.user import User
        from app.models.chat import Chat
        db.create_all()