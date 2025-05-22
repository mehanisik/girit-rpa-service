from flask import Blueprint, request, jsonify 
from app.extensions import db
from app.schemas.bot_schema import (
    bot_config_schema,
    bot_configs_schema,
    bot_config_create_schema,
    bot_config_update_schema
)
from app.services import bot_service
from core.auth import token_required, admin_required, AuthenticatedUser 
from uuid import UUID
from marshmallow import ValidationError

bots_bp = Blueprint("bots", __name__)

@bots_bp.route("/", methods=["POST"])
@admin_required 
def create_bot_configuration(current_user: AuthenticatedUser):
    json_data = request.get_json()
    if not json_data:
        return jsonify({"message": "No input data provided"}), 400

    try:
        data = bot_config_create_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    creator_id = current_user.id if current_user and hasattr(current_user, 'id') else None

    try:
        new_bot = bot_service.create_bot_config(db=db.session, bot_in_data=data, creator_id=creator_id)
        return bot_config_schema.dump(new_bot), 201
    except ValueError as e:
        return jsonify({"message": str(e)}), 409
    except Exception as e:
        db.session.rollback()
        print(f"Error creating bot: {e}")
        return jsonify({"message": "An internal error occurred"}), 500


@bots_bp.route("/", methods=["GET"])
@token_required 
def get_bot_configurations(current_user: AuthenticatedUser): 
   
    skip = request.args.get("skip", 0, type=int)
    limit = request.args.get("limit", 100, type=int)
    is_enabled_str = request.args.get("is_enabled", type=str)
    is_enabled = None
    if is_enabled_str is not None:
        is_enabled = is_enabled_str.lower() in ['true', '1', 't']

    bots = bot_service.get_all_bot_configs(db=db.session, skip=skip, limit=limit, is_enabled=is_enabled)
    return bot_configs_schema.dump(bots), 200


@bots_bp.route("/<uuid:bot_id>", methods=["GET"])
@token_required 
def get_bot_configuration(current_user: AuthenticatedUser, bot_id: UUID): 
    bot = bot_service.get_bot_config_by_id(db=db.session, bot_id=bot_id)
    if not bot:
        return jsonify({"message": "Bot configuration not found"}), 404
    return bot_config_schema.dump(bot), 200


@bots_bp.route("/<uuid:bot_id>", methods=["PUT"])
@admin_required 
def update_bot_configuration(current_user: AuthenticatedUser, bot_id: UUID): 
    json_data = request.get_json()
    if not json_data:
        return jsonify({"message": "No input data provided"}), 400

    try:
        data_to_update = bot_config_update_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    bot = bot_service.get_bot_config_by_id(db=db.session, bot_id=bot_id)
    if not bot:
        return jsonify({"message": "Bot configuration not found"}), 404

    try:
        updated_bot = bot_service.update_bot_config(db=db.session, db_bot=bot, bot_in_data=data_to_update)
        return bot_config_schema.dump(updated_bot), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 409
    except Exception as e:
        db.session.rollback()
        print(f"Error updating bot: {e}")
        return jsonify({"message": "An internal error occurred"}), 500


@bots_bp.route("/<uuid:bot_id>", methods=["DELETE"])
@admin_required 
def delete_bot_configuration(current_user: AuthenticatedUser, bot_id: UUID): 
    success = bot_service.delete_bot_config(db=db.session, bot_id=bot_id)
    if not success:
        return jsonify({"message": "Bot configuration not found or could not be deleted"}), 404
    return '', 204