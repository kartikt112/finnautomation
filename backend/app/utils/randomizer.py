import random
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo
from app.config import settings

DUTCH_TZ = ZoneInfo("Europe/Amsterdam")


def generate_random_times(target_date: date, count: int | None = None) -> list[datetime]:
    """Generate random execution times for a given date within the allowed window."""
    if count is None:
        count = random.randint(settings.DAILY_JOBS_MIN, settings.DAILY_JOBS_MAX)

    start_hour = settings.SCHEDULE_START_HOUR
    end_hour = settings.SCHEDULE_END_HOUR
    total_minutes = (end_hour - start_hour) * 60

    times = set()
    attempts = 0
    while len(times) < count and attempts < 100:
        random_minutes = random.randint(0, total_minutes - 1)
        hour = start_hour + random_minutes // 60
        minute = random_minutes % 60
        second = random.randint(0, 59)
        t = datetime(target_date.year, target_date.month, target_date.day, hour, minute, second, tzinfo=DUTCH_TZ)
        times.add(t)
        attempts += 1

    return sorted(times)


def pick_random_entry(excel_data: list[dict]) -> dict:
    """Pick a random entry from the Excel data."""
    return random.choice(excel_data)
