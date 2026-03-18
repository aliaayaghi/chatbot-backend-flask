from flask_sqlalchemy import SQLAlchemy

# Create one single db instance
# This gets imported by everything that needs the database
db = SQLAlchemy()


def init_db(app):
    # Tell SQLAlchemy where the database file lives
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///chats.db"

    # Don't send a signal every time data changes (saves memory)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Connect the db instance to this Flask app
    db.init_app(app)

    # Create all tables if they don't exist yet
    with app.app_context():
        from app.models.chat import Chat
        db.create_all()