from app.database import db
from datetime import datetime
import json


class Chat(db.Model):
    # Table name in the database
    __tablename__ = "chats"

    # Columns
    id = db.Column(db.String, primary_key=True)
    # Add this line with your other columns
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.Float, nullable=False,
                          default=lambda: datetime.now().timestamp() * 1000)
    

    # Messages and history are arrays of objects
    # SQLite doesn't have an array type so we store them as JSON strings
    _messages = db.Column("messages", db.Text, nullable=False, default="[]")
    _history = db.Column("history", db.Text, nullable=False, default="[]")

    # These properties automatically convert between Python list and JSON string
    @property
    def messages(self):
        return json.loads(self._messages)

    @messages.setter
    def messages(self, value):
        self._messages = json.dumps(value)

    @property
    def history(self):
        return json.loads(self._history)

    @history.setter
    def history(self, value):
        self._history = json.dumps(value)

    def to_dict(self):
        # Converts this object into a plain dictionary
        # so it can be sent as JSON in API responses
        return {
            "id": self.id,
            "title": self.title,
            "timestamp": self.timestamp,
            "messages": self.messages,
            "history": self.history,
        }