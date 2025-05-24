# Girit RPA Service (Flask Backend)

This is the Flask backend service for the Girit RPA (Robotic Process Automation) management dashboard. It provides an API for managing bot configurations, creating and monitoring RPA jobs, and handling asynchronous execution of these jobs.

## Project Goals

*   Allow administrators to define and manage RPA bot configurations.
*   Enable administrators to initiate RPA jobs with specific parameters and uploaded files.
*   Execute RPA jobs asynchronously using Python scripts.
*   Track the status, progress, results, and logs of each job.
*   Provide features to cancel, rerun, and reschedule jobs.
*   Offer a secure and robust API for the Next.js frontend dashboard.

## Technology Stack

*   **Backend:** Python, Flask
*   **Database:** PostgreSQL
*   **ORM:** SQLAlchemy (via Flask-SQLAlchemy)
*   **Migrations:** Alembic (via Flask-Migrate)
*   **Task Queue:** Celery
*   **Message Broker:** Redis
*   **Serialization/Validation:** Marshmallow (via Flask-Marshmallow)
*   **CORS:** Flask-CORS
*   **Deployment (Planned):** Docker, Railway/Fly.io or similar

## Development Plan & Progress Checklist

### Phase 1: Core Asynchronous Job Execution & Basic API

*   [x] **Task 1.1: Setup Celery & Redis Broker**
    *   [x] Add `celery[redis]` and `Werkzeug` to `requirements.txt`.
    *   [x] Create `app/celery_app.py`.
    *   [x] Update `core/config.py` with Celery/Redis, Upload, Admin Auth settings.
    *   [x] Update `.env` with actual values for new settings (generate password hash).
    *   [x] Update `app/__init__.py` for Celery init, `jobs_bp` registration, `app.tasks` import.
    *   [x] Create `app/tasks.py` with basic `execute_rpa_bot_task` and `_add_job_log` helper.
    *   [x] Create `rpa_scripts/` directory with `__init__.py` and `placeholder_bot.py`.
    *   [ ] Test: Flask app starts, Celery worker starts & discovers tasks.

*   [ ] **Task 1.2: Enhance `Job` Model**
    *   [ ] Add `celery_task_id`, `input_files`, `scheduled_at`, `rerun_of_job_id` fields to `Job` model.
    *   [ ] Generate and apply database migration.

*   [ ] **Task 1.3: Implement Simplified Admin Authentication**
    *   [ ] Modify `core/auth.py` for HTTP Basic Authentication against config credentials.
    *   [ ] Test auth on an existing bot endpoint.

*   [ ] **Task 1.4: Create `Job` Schemas**
    *   [ ] In `app/schemas/job_schema.py`: Define `JobCreateSchema`, `JobSchema`, `JobLogSchema`.

*   [ ] **Task 1.5: Implement `JobService` (Initial Version)**
    *   [ ] In `app/services/job_service.py`:
        *   [ ] `create_job()`: Creates `Job` DB record, enqueues Celery task, updates `Job` with `celery_task_id`.
        *   [ ] `get_job_by_id()`
        *   [ ] `get_all_jobs()`
        *   [ ] `add_job_log()`

*   [ ] **Task 1.6: Implement `Job` Creation API Endpoint (`POST /api/v1/jobs/`)**
    *   [ ] In `app/routes/jobs.py`: Create blueprint and `POST /` route.
    *   [ ] Handle `multipart/form-data` for parameters and file uploads.
    *   [ ] Save uploaded files to `settings.UPLOAD_FOLDER`.
    *   [ ] Call `job_service.create_job`.
    *   [ ] Return serialized `Job` (201).
    *   [ ] Test: Create job via API, check DB, Celery worker, placeholder script execution.

*   [ ] **Task 1.7: Implement `Job` Read API Endpoints (`GET /api/v1/jobs/`, `GET /api/v1/jobs/<id>`)**
    *   [ ] In `app/routes/jobs.py`: Implement `GET /` and `GET /<uuid:job_id>`.
    *   [ ] Test: Retrieve job lists and individual job details.

### Phase 2: Enhancing Job Control and RPA Integration

*   [ ] **Task 2.1: Implement Job Cancellation**
    *   [ ] `JobService`: `request_cancel_job()` (revoke queued, set 'cancelling' for running).
    *   [ ] API: `POST /api/v1/jobs/<uuid:job_id>/cancel`.
    *   [ ] Celery Task: Periodically check `Job.status` for 'cancelling'.
    *   [ ] RPA Scripts: Design to be cancellation-aware.

*   [ ] **Task 2.2: Implement Job Rerun**
    *   [ ] `JobService`: `rerun_job()` (create new `Job`, enqueue new task).
    *   [ ] API: `POST /api/v1/jobs/<uuid:job_id>/rerun` (allow new params/files).

*   [ ] **Task 2.3: Refine RPA Script Invocation & Logging**
    *   [ ] `app/tasks.py`: Improve dynamic import, error handling, parameter/file passing.
    *   [ ] Standardize `job_service.add_job_log` usage from RPA scripts.
    *   [ ] Develop 1-2 actual RPA scripts (e.g., Selenium, Excel reader) and integrate.
    *   [ ] Ensure extensive logging from RPA scripts.

### Phase 3: Advanced Features & Production Readiness

*   [ ] **Task 3.1: Implement Simple Job Reschedule ("Run At")**
    *   [ ] `JobService`: `schedule_job()` (creates `Job` with `status='scheduled'`).
    *   [ ] API: `POST /api/v1/jobs/schedule` (or similar).
    *   [ ] Scheduler Process (Celery Beat or APScheduler): Periodically queries for scheduled jobs and enqueues them.

*   [ ] **Task 3.2: Robust Error Handling & Input Validation**
    *   [ ] Review all API endpoints for comprehensive error handling.
    *   [ ] Strengthen input validation in Marshmallow schemas and services.
    *   [ ] Ensure Celery tasks handle unexpected failures gracefully.

*   [ ] **Task 3.3: Testing**
    *   [ ] Write unit tests for service functions and complex logic.
    *   [ ] Write integration tests for API endpoints.

*   [ ] **Task 3.4: Configuration for Production**
    *   [ ] Finalize `.env.example`.
    *   [ ] Consider object storage (S3, MinIO) for `UPLOAD_FOLDER`.

*   [ ] **Task 3.5: Dockerization**
    *   [ ] Create `Dockerfile`.
    *   [ ] Create `docker-compose.yml` for local development.
    *   [ ] Handle RPA script dependencies (e.g., browser drivers) in `Dockerfile`.

*   [ ] **Task 3.6: Documentation**
    *   [ ] Update this `README.md` with setup, API usage, deployment instructions.
    *   [ ] Document RPA script creation guidelines.

## Setup & Running Locally

**(To be filled in as development progresses)**

1.  **Prerequisites:**
    *   Python 3.x
    *   PostgreSQL
    *   Redis
    *   Poetry or pip for dependency management

2.  **Clone the repository:**
    ```bash
    git clone <your_repository_url>
    cd mehanisik-girit-rpa-service
    ```

3.  **Set up a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Set up environment variables:**
    *   Copy `.env.example` (once created) to `.env`.
    *   Fill in your database credentials, Redis URL, `ADMIN_USERNAME`, `ADMIN_PASSWORD_HASH`, etc.

6.  **Initialize the database:**
    ```bash
    flask db init  # Only if migrations folder doesn't exist
    flask db migrate -m "Initial migration"
    flask db upgrade
    ```

7.  **Run the Flask application:**
    ```bash
    python run.py
    ```
    The API will be available at `http://localhost:8000`.

8.  **Run the Celery worker (in a separate terminal):**
    ```bash
    # Ensure Redis is running
    PYTHONPATH=$(pwd) celery -A app.celery_app.celery worker -l info -P gevent
    ```

## API Endpoints

**(To be documented as they are built - e.g., using Swagger/OpenAPI or manually)**

*   `/api/v1/health/`
*   `/api/v1/bots/`
*   `/api/v1/jobs/`
    *   ...

## RPA Script Development

**(Guidelines on how to create new RPA scripts and integrate them)**

---