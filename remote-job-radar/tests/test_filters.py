from datetime import datetime, timedelta, timezone

from remote_job_radar.filters import (
    is_excluded_role,
    is_onsite_or_hybrid,
    is_region_restricted,
    is_remote_location_allowed,
    is_within_last_24_hours,
)


def test_accepts_recent_job():
    now = datetime(2026, 1, 10, 12, 0, tzinfo=timezone.utc)
    published_at = (now - timedelta(hours=3)).isoformat()

    assert is_within_last_24_hours(published_at, now=now)


def test_rejects_old_job():
    now = datetime(2026, 1, 10, 12, 0, tzinfo=timezone.utc)
    published_at = (now - timedelta(hours=30)).isoformat()

    assert not is_within_last_24_hours(published_at, now=now)


def test_accepts_allowed_remote_location():
    job = {"location": "Remote - Brazil", "description": ""}
    assert is_remote_location_allowed(job)


def test_rejects_region_restricted_location():
    job = {"location": "United States only", "description": ""}
    assert is_region_restricted(job)


def test_rejects_excluded_role():
    job = {"title": "Senior Manager, Support Operations"}
    assert is_excluded_role(job)


def test_rejects_hybrid_or_onsite():
    job = {"title": "IT Support Analyst", "location": "Hybrid in São Paulo", "description": ""}
    assert is_onsite_or_hybrid(job)
