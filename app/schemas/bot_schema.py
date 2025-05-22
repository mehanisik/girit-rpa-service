# app/schemas/bot_schema.py
from app.extensions import ma
from app.models.bot_model import BotConfiguration
from marshmallow import fields, validate, EXCLUDE # Removed ValidationError for now, route handles it
from uuid import UUID

# Nested schema for parameter_schema items
class ParameterSchemaItemSchema(ma.Schema):
    type = fields.Str(required=True, validate=validate.OneOf(["string", "integer", "boolean", "file", "text"]))
    label = fields.Str(required=True)
    required = fields.Bool(load_default=False) # Use load_default instead of missing
    # Use 'data_key' to map JSON 'default' to Python 'default_value' attribute
    default_value = fields.Raw(data_key="default", attribute="default_value", load_default=None) # Use load_default
    description = fields.Str(load_default=None) # Use load_default
    options = fields.List(fields.Str(), load_default=None) # For dropdowns/radio buttons

    class Meta:
        unknown = EXCLUDE


# Main schema for BotConfiguration
class BotConfigurationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = BotConfiguration
        load_instance = True
        exclude = ("created_by",)

    id = fields.UUID(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=3, max=150))
    script_identifier = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    parameter_schema = fields.Dict(
        keys=fields.Str(),
        values=fields.Nested(ParameterSchemaItemSchema),
        allow_none=True,
        load_default=None # Use load_default
    )
    default_parameters = fields.Dict(
        keys=fields.Str(),
        values=fields.Raw(),
        allow_none=True,
        load_default=None # Use load_default
    )
    is_enabled = fields.Bool(load_default=True) # Example: defaults to True if not in input JSON during load
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    # Using attribute to map, data_key for JSON key name.
    created_by_user_id_display = fields.UUID(data_key="created_by", attribute="created_by", dump_only=True, allow_none=True)

# Schemas for different operations
bot_config_schema = BotConfigurationSchema()
bot_configs_schema = BotConfigurationSchema(many=True)

bot_config_create_schema = BotConfigurationSchema(
    exclude=("id", "created_at", "updated_at", "created_by_user_id_display")
)

bot_config_update_schema = BotConfigurationSchema(
    partial=True, # This means all fields are optional during load for updates
    exclude=("id", "created_at", "updated_at", "created_by_user_id_display")
)