import traceback
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.tasks.celery_app import celery_app
from app.config import settings
from app.models import Job, JobStatus, Log, Campaign
from app.services.multilogin_service import MultiloginServiceSync


def get_sync_session() -> Session:
    engine = create_engine(settings.sync_database_url)
    return Session(engine)


def add_log(session: Session, job_id: str, status: str, message: str, error_trace: str = None):
    log = Log(job_id=job_id, status=status, message=message, error_trace=error_trace)
    session.add(log)
    session.commit()


@celery_app.task(
    name="app.tasks.worker.execute_job",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def execute_job(self, job_id: str):
    """Execute a single automation job via Multilogin + Playwright."""
    session = get_sync_session()
    multilogin = MultiloginServiceSync()

    try:
        job = session.get(Job, job_id)
        if not job:
            return f"Job {job_id} not found"

        campaign = session.get(Campaign, job.campaign_id)
        if not campaign:
            return f"Campaign not found for job {job_id}"

        # Mark as running
        job.status = JobStatus.running
        job.started_at = datetime.utcnow()
        session.commit()

        add_log(session, job_id, "running", "Job started")

        entry_data = job.entry_data or {}
        username = entry_data.get("username", "")
        password = entry_data.get("password", "")

        # Get a profile ID from the client's profile group
        # For now, use the profile group as the profile ID
        # In production, you'd pick from a pool of profiles
        profile_id = campaign.client_id  # TODO: map to actual Multilogin profile ID

        # Start Multilogin profile
        add_log(session, job_id, "running", f"Starting Multilogin profile: {profile_id}")

        try:
            start_response = multilogin.start_profile(str(profile_id))
            ws_endpoint = multilogin.get_ws_endpoint(start_response)
        except Exception as e:
            raise Exception(f"Failed to start Multilogin profile: {e}")

        try:
            # Connect Playwright and perform automation
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                browser = p.chromium.connect_over_cdp(ws_endpoint)
                context = browser.contexts[0] if browser.contexts else browser.new_context()
                page = context.new_page()

                # Navigate to target URL
                add_log(session, job_id, "running", f"Navigating to {campaign.target_url}")
                page.goto(campaign.target_url, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(2000)

                # --- AUTOMATION LOGIC ---
                # This is where the actual automation steps go.
                # For now, just navigate and take a screenshot as proof.
                # In production, customize this per campaign type.
                add_log(session, job_id, "running", f"Performing automation for {username}")

                # Example: fill login form if present
                # page.fill('input[name="email"]', username)
                # page.fill('input[name="password"]', password)
                # page.click('button[type="submit"]')
                # page.wait_for_timeout(3000)

                page.wait_for_timeout(2000)
                page.close()

        finally:
            # Always stop the profile
            multilogin.stop_profile(str(profile_id))

        # Mark success
        job.status = JobStatus.success
        job.completed_at = datetime.utcnow()
        session.commit()
        add_log(session, job_id, "success", "Job completed successfully")

        return f"Job {job_id} completed"

    except Exception as e:
        error_msg = str(e)
        error_tb = traceback.format_exc()

        if session.is_active:
            job = session.get(Job, job_id)
            if job:
                job.error_message = error_msg
                if self.request.retries < self.max_retries:
                    job.status = JobStatus.retrying
                    job.retry_count = self.request.retries + 1
                else:
                    job.status = JobStatus.failed
                    job.completed_at = datetime.utcnow()
                session.commit()

            add_log(session, job_id, "failed", error_msg, error_tb)

        # Retry with exponential backoff
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))

        return f"Job {job_id} failed: {error_msg}"

    finally:
        session.close()
