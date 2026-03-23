from celery import Celery
from celery.schedules import crontab
from app.config import settings

celery_app = Celery(
    "finautomation",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Amsterdam",
    enable_utc=True,
    worker_concurrency=2,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

celery_app.conf.beat_schedule = {
    "daily-job-generator": {
        "task": "app.tasks.scheduler.generate_daily_jobs_task",
        "schedule": crontab(minute=5, hour=0),  # 00:05 daily
    },
    "dispatch-pending-jobs": {
        "task": "app.tasks.scheduler.dispatch_pending_jobs_task",
        "schedule": crontab(minute="*/5"),  # Every 5 minutes
    },
}

celery_app.autodiscover_tasks(["app.tasks"])
