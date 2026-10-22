import hashlib
import logging
from datetime import datetime, timezone
from typing import Any

import requests

LOGGER = logging.getLogger(__name__)
HIMALAYAS_JOBS_API_URL = "https://himalayas.app/jobs/api"


def fetch_himalayas_jobs(timeout: int = 15, max_pages: int = 5, limit: int = 20) -> list[dict[str, Any]]:
    jobs: list[dict[str, Any]] = []

    for page in range(max_pages):
        offset = page * limit
        params = {"limit": limit, "offset": offset}

        try:
            response = requests.get(HIMALAYAS_JOBS_API_URL, params=params, timeout=timeout)
            response.raise_for_status()
        except requests.RequestException:
            LOGGER.exception("Erro ao consultar Himalayas (offset=%s).", offset)
            raise

        payload = response.json()
        raw_jobs = _extract_jobs_from_payload(payload)
        if not raw_jobs:
            break

        normalized_jobs = [_normalize_job(raw_job) for raw_job in raw_jobs]
        jobs.extend(job for job in normalized_jobs if job)

    return jobs


def _extract_jobs_from_payload(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return payload

    if isinstance(payload, dict):
        for key in ("jobs", "results", "data"):
            value = payload.get(key)
            if isinstance(value, list):
                return value

    return []


def _normalize_job(raw_job: dict[str, Any]) -> dict[str, Any]:
    title = _first_non_empty(raw_job, ["title", "job_title"]) or "Sem título"
    company = _extract_company_name(raw_job)
    location = _extract_location_text(raw_job)
    description = _extract_description(raw_job)
    source_url = _first_non_empty(
        raw_job,
        ["apply_url", "url", "job_url", "application_url", "short_url"],
    )

    published_raw = _first_non_empty(
        raw_job,
        ["posted_at", "published_at", "created_at", "publishedAt", "postedAt"],
    )
    published_at = _normalize_datetime_to_iso(published_raw)

    raw_id = _first_non_empty(raw_job, ["id", "_id", "job_id", "slug"])
    job_id = str(raw_id) if raw_id else _build_fallback_job_id(title, company, source_url)

    return {
        "id": job_id,
        "title": title,
        "company": company,
        "location": location,
        "description": description,
        "source": "Himalayas",
        "source_url": source_url or "",
        "published_at": published_at,
        "worldwide": bool(raw_job.get("worldwide", False)),
    }


def _extract_company_name(raw_job: dict[str, Any]) -> str:
    company = raw_job.get("company")
    if isinstance(company, dict):
        return str(company.get("name") or company.get("company_name") or "Empresa não informada")
    if isinstance(company, str) and company.strip():
        return company.strip()

    return str(_first_non_empty(raw_job, ["company_name", "companyName"]) or "Empresa não informada")


def _extract_location_text(raw_job: dict[str, Any]) -> str:
    pieces: list[str] = []

    for key in ("location", "location_name", "locationName"):
        value = raw_job.get(key)
        if isinstance(value, str) and value.strip():
            pieces.append(value.strip())

    for key in ("location_restrictions", "locationRestrictions", "candidate_regions", "candidateRegions"):
        value = raw_job.get(key)
        if isinstance(value, list):
            cleaned = [str(item).strip() for item in value if str(item).strip()]
            pieces.extend(cleaned)

    timezone_restrictions = raw_job.get("timezone_restrictions") or raw_job.get("timezoneRestrictions")
    if isinstance(timezone_restrictions, list):
        cleaned_tz = [str(item).strip() for item in timezone_restrictions if str(item).strip()]
        pieces.extend(cleaned_tz)

    return " | ".join(dict.fromkeys(pieces)) if pieces else "Remote"


def _extract_description(raw_job: dict[str, Any]) -> str:
    description = _first_non_empty(raw_job, ["description", "excerpt", "summary"])
    return str(description) if description else ""


def _normalize_datetime_to_iso(value: Any) -> str:
    if value is None:
        return ""

    if isinstance(value, (int, float)):
        dt = datetime.fromtimestamp(value, tz=timezone.utc)
        return dt.isoformat()

    if isinstance(value, str):
        text = value.strip()
        if not text:
            return ""

        normalized = text.replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(normalized)
        except ValueError:
            return text

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        return dt.isoformat()

    return ""


def _build_fallback_job_id(title: str, company: str, source_url: str | None) -> str:
    base = f"{title}|{company}|{source_url or ''}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def _first_non_empty(raw_job: dict[str, Any], keys: list[str]) -> str | None:
    for key in keys:
        value = raw_job.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
        if value and not isinstance(value, (dict, list)):
            return str(value)
    return None
