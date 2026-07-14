from typing import Any

from remote_job_radar.filters import is_remote_location_allowed

TARGET_ROLE_KEYWORDS = [
    "technical support",
    "support engineer",
    "it support",
    "application support",
    "saas support",
    "cloud support",
    "service desk",
    "help desk",
    "customer support",
    "operations support",
    "support specialist",
    "support analyst",
    "l1",
    "l2",
    "n1",
    "n2",
]

PROFILE_SKILL_KEYWORDS = [
    "microsoft 365",
    "exchange online",
    "outlook",
    "microsoft teams",
    "entra id",
    "active directory",
    "glpi",
    "zabbix",
    "grafana",
    "troubleshooting",
    "incident",
    "sla",
    "documentation",
    "escalation",
    "powershell",
    "python",
    "api",
    "cloud",
    "azure",
    "aws",
]


def calculate_compatibility_score(job: dict[str, Any]) -> tuple[int, list[str]]:
    title_text = str(job.get("title", "")).lower()
    description_text = str(job.get("description", "")).lower()

    score = 0
    reasons: list[str] = []

    title_matches = [keyword for keyword in TARGET_ROLE_KEYWORDS if keyword in title_text]
    if title_matches:
        title_points = min(40, len(title_matches) * 20)
        score += title_points
        reasons.append(f"Título alinhado ({', '.join(title_matches[:3])})")

    skill_matches = [keyword for keyword in PROFILE_SKILL_KEYWORDS if keyword in description_text]
    if skill_matches:
        skill_points = min(40, len(skill_matches) * 5)
        score += skill_points
        reasons.append(f"Skills citadas ({', '.join(skill_matches[:4])})")

    if is_remote_location_allowed(job):
        score += 20
        reasons.append("Localização remota compatível")

    final_score = max(0, min(100, score))
    return final_score, reasons[:4]
