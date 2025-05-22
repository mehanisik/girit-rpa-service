# app/services/bot_service.py
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.models.bot_model import BotConfiguration
# We'll define Pydantic-like input classes here for type hinting the service layer,
# or you can use Marshmallow schemas if you prefer to pass them around.
# For simplicity now, let's assume dictionaries or Pydantic-like structures for `_in` objects.

# Pydantic-like structures for service layer input (can be actual Pydantic models)
class BotConfigCreateData:
    def __init__(self, name: str, script_identifier: str, description: Optional[str] = None,
                 parameter_schema: Optional[Dict[str, Any]] = None,
                 default_parameters: Optional[Dict[str, Any]] = None,
                 is_enabled: bool = True):
        self.name = name
        self.description = description
        self.script_identifier = script_identifier
        self.parameter_schema = parameter_schema
        self.default_parameters = default_parameters
        self.is_enabled = is_enabled

class BotConfigUpdateData:
    def __init__(self, name: Optional[str] = None, description: Optional[str] = None,
                 script_identifier: Optional[str] = None,
                 parameter_schema: Optional[Dict[str, Any]] = None,
                 default_parameters: Optional[Dict[str, Any]] = None,
                 is_enabled: Optional[bool] = None):
        self.name = name
        self.description = description
        self.script_identifier = script_identifier
        self.parameter_schema = parameter_schema
        self.default_parameters = default_parameters
        self.is_enabled = is_enabled
        # Helper to get only provided fields for update
        self.update_dict = {k: v for k, v in self.__dict__.items() if v is not None and k != 'update_dict'}


def get_bot_config_by_id(db: Session, bot_id: UUID) -> Optional[BotConfiguration]:
    return db.query(BotConfiguration).filter(BotConfiguration.id == bot_id).first()

def get_bot_config_by_name(db: Session, name: str) -> Optional[BotConfiguration]:
    return db.query(BotConfiguration).filter(BotConfiguration.name == name).first()

def get_all_bot_configs(db: Session, skip: int = 0, limit: int = 100, is_enabled: Optional[bool] = None) -> List[BotConfiguration]:
    query = db.query(BotConfiguration)
    if is_enabled is not None:
        query = query.filter(BotConfiguration.is_enabled == is_enabled)
    return query.order_by(BotConfiguration.name).offset(skip).limit(limit).all()

def create_bot_config(db: Session, bot_in_data: Dict[str, Any], creator_id: Optional[UUID] = None) -> BotConfiguration:
    # Check if bot with the same name already exists
    existing_bot = get_bot_config_by_name(db, name=bot_in_data["name"])
    if existing_bot:
        raise ValueError(f"Bot configuration with name '{bot_in_data['name']}' already exists.")

    db_bot = BotConfiguration(
        name=bot_in_data["name"],
        description=bot_in_data.get("description"),
        script_identifier=bot_in_data["script_identifier"],
        parameter_schema=bot_in_data.get("parameter_schema"),
        default_parameters=bot_in_data.get("default_parameters"),
        is_enabled=bot_in_data.get("is_enabled", True),
        created_by=creator_id
    )
    db.add(db_bot)
    db.commit()
    db.refresh(db_bot)
    return db_bot

def update_bot_config(db: Session, db_bot: BotConfiguration, bot_in_data: Dict[str, Any]) -> BotConfiguration:
    update_data = {k: v for k, v in bot_in_data.items() if v is not None}
    if 'name' in update_data and update_data['name'] != db_bot.name:
        existing_bot_with_new_name = get_bot_config_by_name(db, name=update_data['name'])
        if existing_bot_with_new_name:
            raise ValueError(f"Another bot configuration with name '{update_data['name']}' already exists.")
    for key, value in update_data.items():
        setattr(db_bot, key, value)
    db.commit()
    db.refresh(db_bot)
    return db_bot

def delete_bot_config(db: Session, bot_id: UUID) -> bool:
    db_bot = get_bot_config_by_id(db, bot_id=bot_id)
    if db_bot:
        db.delete(db_bot)
        db.commit()
        return True
    return False