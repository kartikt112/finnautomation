from app.tasks.celery_app import celery_app
from app.services.scheduler_service import generate_daily_jobs, get_pending_jobs_for_now


@celery_app.task(name="app.tasks.scheduler.generate_daily_jobs_task")
def generate_daily_jobs_task():
    """Runs daily at 00:05. Generates 2-3 random jobs per active campaign."""
    count = generate_daily_jobs()
    return f"Generated {count} jobs for today"


@celery_app.task(name="app.tasks.scheduler.dispatch_pending_jobs_task")
def dispatch_pending_jobs_task():
    """Runs every 5 minutes. Dispatches any pending jobs whose scheduled_time has passed."""
    from app.tasks.worker import execute_job

    job_ids = get_pending_jobs_for_now()
    for job_id in job_ids:
        execute_job.delay(job_id)
    return f"Dispatched {len(job_ids)} jobs"
