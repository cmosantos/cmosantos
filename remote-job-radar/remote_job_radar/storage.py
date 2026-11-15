import json
import logging
from pathlib import Path

LOGGER = logging.getLogger(__name__)


def load_sent_job_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        LOGGER.exception("Erro ao ler histórico de vagas enviadas: %s", path)
        return set()

    if isinstance(data, dict) and isinstance(data.get("sent_job_ids"), list):
        return {str(job_id) for job_id in data["sent_job_ids"]}

    return set()


def save_sent_job_ids(path: Path, sent_job_ids: set[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = {"sent_job_ids": sorted(sent_job_ids)}
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
