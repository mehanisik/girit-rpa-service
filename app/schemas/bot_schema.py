from app.extensions import ma
from app.models.bot_model import BotConfiguration
from marshmallow import fields, validate, EXCLUDE 
from uuid import UUID


class ParameterSchemaItemSchema(ma.Schema):
    type = fields.Str(required=True, validate=validate.OneOf(["string", "integer", "boolean", "file", "text"]))
    label = fields.Str(required=True)
    required = fields.Bool(load_default=False) 
    default_value = fields.Raw(data_key="default", attribute="default_value", load_default=None) 
    description = fields.Str(load_default=None) 
    options = fields.List(fields.Str(), load_default=None) 

    class Meta:
        unknown = EXCLUDE


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
        load_default=None 
    )
    default_parameters = fields.Dict(
        keys=fields.Str(),
        values=fields.Raw(),
        allow_none=True,
        load_default=None 
    )
    is_enabled = fields.Bool(load_default=True) 
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    created_by_user_id_display = fields.UUID(data_key="created_by", attribute="created_by", dump_only=True, allow_none=True)

bot_config_schema = BotConfigurationSchema()
bot_configs_schema = BotConfigurationSchema(many=True)

bot_config_create_schema = BotConfigurationSchema(
    exclude=("id", "created_at", "updated_at", "created_by_user_id_display")
)

bot_config_update_schema = BotConfigurationSchema(
    partial=True, 
    exclude=("id", "created_at", "updated_at", "created_by_user_id_display")
)