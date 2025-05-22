# app/models/job_model.py
from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from uuid import uuid4
from datetime import datetime, timezone

# Import BotConfiguration if you need to define the relationship explicitly here,
# otherwise Flask-SQLAlchemy can often infer it from the ForeignKey string.
# from .bot_model import BotConfiguration

class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    bot_config_id = db.Column(PG_UUID(as_uuid=True), db.ForeignKey("bot_configurations.id"), nullable=False, index=True)
    status = db.Column(db.String(50), nullable=False, default='pending', index=True) # e.g., pending, queued, running, success, failed, cancelled
    parameters_used = db.Column(JSONB, nullable=True) # Use JSONB for better querying in PostgreSQL
    enqueued_at = db.Column(db.DateTime(timezone=True), nullable=True)
    started_at = db.Column(db.DateTime(timezone=True), nullable=True)
    completed_at = db.Column(db.DateTime(timezone=True), nullable=True)
    result_summary = db.Column(db.Text, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    error_details = db.Column(JSONB, nullable=True) # For structured errors like tracebacks
    progress_percent = db.Column(db.Integer, default=0, nullable=True)
    progress_message = db.Column(db.Text, nullable=True)
    triggered_by_user_id = db.Column(PG_UUID(as_uuid=True), nullable=True) # User who started the job
    retry_count = db.Column(db.Integer, default=0, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


    # Relationship to BotConfiguration (optional but good for ORM features)
    # The backref creates a `jobs` attribute on BotConfiguration instances
    bot_configuration = db.relationship("BotConfiguration", backref=db.backref("jobs", lazy=True))

    # Relationship to JobLog (one-to-many: one Job has many JobLogs)
    logs = db.relationship("JobLog", backref="job", lazy="dynamic", cascade="all, delete-orphan")
    # lazy="dynamic" means logs will be a query object, not loaded immediately
    # cascade="all, delete-orphan" means if a Job is deleted, its logs are also deleted

    def __repr__(self):
        return f"<Job {self.id} - Status: {self.status}>"


class JobLog(db.Model):
    __tablename__ = "job_logs"

    id = db.Column(db.BigInteger, primary_key=True) # Using BigInteger for potentially high volume
    job_id = db.Column(PG_UUID(as_uuid=True), db.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    log_level = db.Column(db.String(20), nullable=False, default='INFO') # e.g., INFO, DEBUG, ERROR, SCRIPT_STDOUT
    message = db.Column(db.Text, nullable=False)
    source = db.Column(db.String(100), nullable=True) # e.g., worker, script_name.py

    # job relationship is defined by the backref in Job model

    def __repr__(self):
        return f"<JobLog {self.id} [{self.log_level}] Job: {self.job_id}>"