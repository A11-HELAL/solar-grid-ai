"""Scheduled batch jobs: replay_job, soiling_job, and forecast_job."""

from datetime import date


def replay_job(target_date: date, plant_id: str = "dka_01") -> None:
    """Replay historical day into database measurements table."""
    raise NotImplementedError("worker.jobs.replay_job is a stub")


def soiling_job(target_date: date, plant_id: str = "dka_01") -> None:
    """Execute daily soiling evaluation and update health table."""
    raise NotImplementedError("worker.jobs.soiling_job is a stub")


def forecast_job(as_of_date: date, plant_id: str = "dka_01") -> None:
    """Generate 24-hour day-ahead forecast with guardrails and soiling derating."""
    raise NotImplementedError("worker.jobs.forecast_job is a stub")
