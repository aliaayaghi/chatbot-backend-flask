from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database import db
from app.models.chat import Chat

chats_bp = Blueprint("chats", __name__)


@chats_bp.route("/chats", methods=["GET"])
@jwt_required()
def get_chats():
    user_id = get_jwt_identity()
    # Only return chats belonging to this user
    chats = Chat.query.filter_by(user_id=user_id)\
                      .order_by(Chat.timestamp.desc()).all()
    return jsonify({ "chats": [c.to_dict() for c in chats] }), 200


@chats_bp.route("/chats", methods=["POST"])
@jwt_required()
def create_chat():
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data or not data.get("id") or not data.get("title"):
        return jsonify({ "error": "id and title are required" }), 400

    chat = Chat(
        id=data["id"],
        title=data["title"],
        timestamp=data.get("timestamp"),
        user_id=user_id,       # ← attach to this user
    )
    chat.messages = data.get("messages", [])
    chat.history = data.get("history", [])

    db.session.add(chat)
    db.session.commit()

    return jsonify({ "chat": chat.to_dict() }), 201


@chats_bp.route("/chats/<chat_id>", methods=["PUT"])
@jwt_required()
def update_chat(chat_id):
    user_id = get_jwt_identity()
    chat = Chat.query.filter_by(id=chat_id, user_id=user_id).first()

    # 404 if not found OR belongs to someone else
    if not chat:
        return jsonify({ "error": "Chat not found" }), 404

    data = request.get_json()
    if "messages" in data:
        chat.messages = data["messages"]
    if "history" in data:
        chat.history = data["history"]
    if "timestamp" in data:
        chat.timestamp = data["timestamp"]

    db.session.commit()
    return jsonify({ "chat": chat.to_dict() }), 200


@chats_bp.route("/chats/<chat_id>", methods=["DELETE"])
@jwt_required()
def delete_chat(chat_id):
    user_id = get_jwt_identity()
    chat = Chat.query.filter_by(id=chat_id, user_id=user_id).first()

    if not chat:
        return jsonify({ "error": "Chat not found" }), 404

    db.session.delete(chat)
    db.session.commit()
    return jsonify({ "message": "deleted" }), 200