from flask import Blueprint, request, jsonify
from app.database import db
from app.models.chat import Chat

# A Blueprint is a mini Flask app — a group of related routes
# This keeps chat routes isolated from any future routes (auth, users etc)
chats_bp = Blueprint("chats", __name__)


# GET /chats — return all chats, newest first
@chats_bp.route("/chats", methods=["GET"])
def get_chats():
    chats = Chat.query.order_by(Chat.timestamp.desc()).all()
    return jsonify({ "chats": [c.to_dict() for c in chats] }), 200


# POST /chats — create a new chat
@chats_bp.route("/chats", methods=["POST"])
def create_chat():
    data = request.get_json()

    # Validate — make sure required fields are present
    if not data or not data.get("id") or not data.get("title"):
        return jsonify({ "error": "id and title are required" }), 400

    chat = Chat(
        id=data["id"],
        title=data["title"],
        timestamp=data.get("timestamp"),
    )
    chat.messages = data.get("messages", [])
    chat.history = data.get("history", [])

    db.session.add(chat)
    db.session.commit()

    return jsonify({ "chat": chat.to_dict() }), 201


# PUT /chats/<id> — update an existing chat
@chats_bp.route("/chats/<chat_id>", methods=["PUT"])
def update_chat(chat_id):
    # 404 if chat doesn't exist
    chat = Chat.query.get_or_404(chat_id)
    data = request.get_json()

    if "messages" in data:
        chat.messages = data["messages"]
    if "history" in data:
        chat.history = data["history"]
    if "timestamp" in data:
        chat.timestamp = data["timestamp"]

    db.session.commit()

    return jsonify({ "chat": chat.to_dict() }), 200


# DELETE /chats/<id> — delete a chat
@chats_bp.route("/chats/<chat_id>", methods=["DELETE"])
def delete_chat(chat_id):
    chat = Chat.query.get_or_404(chat_id)
    db.session.delete(chat)
    db.session.commit()
    return jsonify({ "message": "deleted" }), 200