from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from uuid import uuid4
from datetime import datetime, timezone

class BotConfiguration(db.Model):
    __tablename__ = "bot_configurations"

    id = db.Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = db.Column(db.String(150), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    script_identifier = db.Column(db.String(255), nullable=False, index=True)
    parameter_schema = db.Column(db.JSON, nullable=True)
    default_parameters = db.Column(db.JSON, nullable=True)
    is_enabled = db.Column(db.Boolean, nullable=False, default=True)
    created_by = db.Column(PG_UUID(as_uuid=True), nullable=True)
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<BotConfiguration {self.name}>"