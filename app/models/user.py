from app.database import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False)

    # Nullable because Google users don't have a password
    password_hash = db.Column(db.String(255), nullable=True)

    # How did they sign up — "email" or "google"
    auth_provider = db.Column(db.String(20), nullable=False, default="email")

    # Google's unique ID for this user — only set for Google users
    google_id = db.Column(db.String(100), nullable=True, unique=True)

    # Relationship — one user has many chats
    chats = db.relationship("Chat", backref="owner", lazy=True,
                            cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "auth_provider": self.auth_provider,
        }