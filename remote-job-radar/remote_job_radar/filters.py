from datetime import datetime, timedelta, timezone
from typing import Any

ALLOWED_LOCATION_KEYWORDS = [
    "brazil",
    "brasil",
    "latam",
    "latin america",
    "south america",
    "americas",
    "worldwide",
    "global",
    "anywhere",
    "remote",
]

REGION_RESTRICTION_KEYWORDS = [
    "united states only",
    "us only",
    "usa only",
    "canada only",
    "europe only",
    "eu only",
    "european union only",
]

EXCLUDED_ROLE_KEYWORDS = [
    "director",
    "head of",
    "vp",
    "vice president",
    "senior manager",
    "sales",
    "account executive",
    "software engineer",
    "software developer",
    "full stack",
    "frontend",
    "backend",
]

ONSITE_OR_HYBRID_KEYWORDS = [
    "on-site",
    "onsite",
    "in office",
    "presencial",
    "híbrido",
    "hybrid",
]


def is_within_last_24_hours(published_at: str | None, now: datetime | None = None) -> bool:
    published_dt = _parse_datetime(published_at)
    if not published_dt:
        return False

    reference = now or datetime.now(timezone.utc)
    return reference - published_dt <= timedelta(hours=24)


def is_remote_location_allowed(job: dict[str, Any]) -> bool:
    if bool(job.get("worldwide", False)):
        return True

    location_text = _combine_job_text(job, fields=("location", "description"))
    return any(keyword in location_text for keyword in ALLOWED_LOCATION_KEYWORDS)


def is_region_restricted(job: dict[str, Any]) -> bool:
    location_text = _combine_job_text(job, fields=("location", "description"))
    return any(keyword in location_text for keyword in REGION_RESTRICTION_KEYWORDS)


def is_excluded_role(job: dict[str, Any]) -> bool:
    title_text = str(job.get("title", "")).lower()
    return any(keyword in title_text for keyword in EXCLUDED_ROLE_KEYWORDS)


def is_onsite_or_hybrid(job: dict[str, Any]) -> bool:
    full_text = _combine_job_text(job, fields=("title", "location", "description"))
    return any(keyword in full_text for keyword in ONSITE_OR_HYBRID_KEYWORDS)


def _combine_job_text(job: dict[str, Any], fields: tuple[str, ...]) -> str:
    chunks = [str(job.get(field, "")) for field in fields]
    return " ".join(chunks).lower()


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None

    normalized = value.strip().replace("Z", "+00:00")

    try:
        dt = datetime.fromisoformat(normalized)
    except ValueError:
        return None

    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(timezone.utc)
