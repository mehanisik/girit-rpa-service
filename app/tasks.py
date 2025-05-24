from .celery_app import celery
from .extensions import db
from app.models.job_model import Job, JobLog
from app.models.bot_model import BotConfiguration
import time
import importlib
from datetime import datetime, timezone
import os
import traceback 
from uuid import UUID 


def _add_job_log(job_id: UUID, level: str, message: str, source: str = "worker"):
    """Adds a log entry for a given job."""
    try:
        log_entry = JobLog(job_id=job_id, log_level=level, message=message, source=source)
        db.session.add(log_entry)
        db.session.commit()
    except Exception as e:
        print(f"Error adding job log for job {job_id}: {e}")
        db.session.rollback()


@celery.task(bind=True, name="app.tasks.execute_rpa_bot", acks_late=True, reject_on_worker_lost=True)
def execute_rpa_bot_task(self, job_id_str: str):
    """
    Celery task to execute an RPA bot.
    `acks_late=True` means the task message will be acknowledged after the task returns,
    not when it's pulled from the queue. If the worker crashes, the task can be redelivered.
    `reject_on_worker_lost=True` works with acks_late to ensure redelivery if worker dies.
    """
    job_id = UUID(job_id_str) 
    job = db.session.get(Job, job_id)

    if not job:
        print(f"CRITICAL: Job with ID {job_id_str} not found in execute_rpa_bot_task.")
        return {"status": "error", "message": "Job not found in database"}

    bot_config = db.session.get(BotConfiguration, job.bot_config_id)
    if not bot_config:
        job.status = "failed"
        job.error_message = f"BotConfiguration with ID {job.bot_config_id} not found for Job {job_id_str}."
        job.completed_at = datetime.now(timezone.utc)
        db.session.commit()
        _add_job_log(job_id, "ERROR", job.error_message)
        return {"status": "error", "message": job.error_message, "job_id": job_id_str}

    if not bot_config.is_enabled:
        job.status = "failed"
        job.error_message = f"Bot '{bot_config.name}' (ID: {bot_config.id}) is disabled. Job {job_id_str} cannot run."
        job.completed_at = datetime.now(timezone.utc)
        db.session.commit()
        _add_job_log(job_id, "ERROR", job.error_message)
        return {"status": "error", "message": job.error_message, "job_id": job_id_str}

    job.status = "running"
    job.started_at = datetime.now(timezone.utc)
    job.celery_task_id = self.request.id 
    db.session.commit()
    _add_job_log(job_id, "INFO", f"Job {job_id_str} status: RUNNING. Bot: {bot_config.name}. Celery Task ID: {self.request.id}")

    try:
        _add_job_log(job_id, "INFO", f"Attempting to run script: {bot_config.script_identifier} for Job {job_id_str}.")

        
        
        if not bot_config.script_identifier or '.' not in bot_config.script_identifier:
            raise ValueError(f"Invalid script_identifier format: '{bot_config.script_identifier}'. Expected 'module_name.function_name'.")

        module_name_rel, function_name = bot_config.script_identifier.rsplit('.', 1)
        full_module_name = f"rpa_scripts.{module_name_rel}"

        _add_job_log(job_id, "DEBUG", f"Importing module: {full_module_name}, function: {function_name}")
        
        rpa_module = importlib.import_module(full_module_name)
        rpa_function = getattr(rpa_module, function_name)

        _add_job_log(job_id, "INFO", f"Successfully imported RPA function. Executing now for Job {job_id_str}.")

        result_summary = rpa_function(
            job_id_str=str(job.id),
            parameters=job.parameters_used,
            input_files_metadata=job.input_files, 
            job_log_func=_add_job_log
        )

        job.status = "success"
        job.result_summary = str(result_summary) if result_summary else "Execution completed without explicit result summary."
        _add_job_log(job_id, "INFO", f"Job {job_id_str} completed successfully. Result: {job.result_summary}")

    except ModuleNotFoundError as e:
        job.status = "failed"
        error_msg = f"Failed to import RPA script module: {str(e)}. Ensure '{full_module_name}' exists and rpa_scripts directory is in PYTHONPATH."
        job.error_message = error_msg
        job.error_details = {"traceback": traceback.format_exc(), "module_path_searched": full_module_name}
        _add_job_log(job_id, "ERROR", error_msg)
        _add_job_log(job_id, "DEBUG", f"Traceback: {traceback.format_exc()}")
        print(f"ModuleNotFoundError in task for job {job_id_str}: {e}\n{traceback.format_exc()}")

    except AttributeError as e:
        job.status = "failed"
        error_msg = f"Failed to find function '{function_name}' in module '{full_module_name}': {str(e)}."
        job.error_message = error_msg
        job.error_details = {"traceback": traceback.format_exc()}
        _add_job_log(job_id, "ERROR", error_msg)
        _add_job_log(job_id, "DEBUG", f"Traceback: {traceback.format_exc()}")
        print(f"AttributeError in task for job {job_id_str}: {e}\n{traceback.format_exc()}")

    except Exception as e:
        job.status = "failed"
        error_msg = f"Error during bot execution for Job {job_id_str}: {str(e)}"
        job.error_message = error_msg
        job.error_details = {"traceback": traceback.format_exc()} 
        _add_job_log(job_id, "ERROR", error_msg)
        _add_job_log(job_id, "DEBUG", f"Traceback: {traceback.format_exc()}")
        print(f"Exception in task for job {job_id_str}: {e}\n{traceback.format_exc()}") 
    finally:
        job.completed_at = datetime.now(timezone.utc)
        db.session.commit() 

    return {"job_id": str(job_id), "status": job.status, "result": job.result_summary}