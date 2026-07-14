import logging
import os
import sys
from pathlib import Path

from remote_job_radar.collector import fetch_himalayas_jobs
from remote_job_radar.filters import (
    is_excluded_role,
    is_onsite_or_hybrid,
    is_region_restricted,
    is_remote_location_allowed,
    is_within_last_24_hours,
)
from remote_job_radar.scorer import calculate_compatibility_score
from remote_job_radar.storage import load_sent_job_ids, save_sent_job_ids
from remote_job_radar.telegram_client import format_job_message, send_telegram_alert

LOGGER = logging.getLogger("remote_job_radar")
MIN_SCORE = 70
REQUEST_TIMEOUT = 15
HISTORY_FILE = Path(__file__).parent / "data" / "sent_jobs.json"


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def main() -> int:
    setup_logging()

    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not telegram_bot_token or not telegram_chat_id:
        LOGGER.error(
            "Variáveis de ambiente ausentes. Defina TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID."
        )
        return 1

    sent_job_ids = load_sent_job_ids(HISTORY_FILE)
    LOGGER.info("Histórico carregado com %s vagas já enviadas.", len(sent_job_ids))

    try:
        jobs = fetch_himalayas_jobs(timeout=REQUEST_TIMEOUT)
    except Exception:
        LOGGER.exception("Falha ao coletar vagas na API da Himalayas.")
        return 1

    LOGGER.info("Vagas coletadas: %s", len(jobs))

    eligible_jobs = []
    for job in jobs:
        if job["id"] in sent_job_ids:
            continue
        if not is_within_last_24_hours(job.get("published_at")):
            continue
        if not is_remote_location_allowed(job):
            continue
        if is_region_restricted(job):
            continue
        if is_excluded_role(job):
            continue
        if is_onsite_or_hybrid(job):
            continue

        score, reasons = calculate_compatibility_score(job)
        if score < MIN_SCORE:
            continue

        job["score"] = score
        job["reasons"] = reasons
        eligible_jobs.append(job)

    if not eligible_jobs:
        LOGGER.info("Nenhuma vaga compatível encontrada nesta execução.")
        return 0

    LOGGER.info("Vagas elegíveis para envio: %s", len(eligible_jobs))

    new_sent_ids = set(sent_job_ids)
    sent_count = 0
    for job in eligible_jobs:
        message = format_job_message(job)
        success = send_telegram_alert(
            bot_token=telegram_bot_token,
            chat_id=telegram_chat_id,
            message=message,
            timeout=REQUEST_TIMEOUT,
        )
        if success:
            new_sent_ids.add(job["id"])
            sent_count += 1

    if sent_count > 0:
        save_sent_job_ids(HISTORY_FILE, new_sent_ids)
        LOGGER.info("Envio concluído. %s novas vagas enviadas.", sent_count)
    else:
        LOGGER.warning("Nenhuma mensagem foi enviada com sucesso ao Telegram.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
