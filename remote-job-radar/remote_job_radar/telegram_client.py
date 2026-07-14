import logging
from typing import Any

import requests

LOGGER = logging.getLogger(__name__)


def format_job_message(job: dict[str, Any]) -> str:
    reasons = job.get("reasons") or ["Compatível com o perfil informado"]
    reasons_lines = "\n".join(f"- {reason}" for reason in reasons)

    return (
        "🚨 Nova vaga compatível (Remote Job Radar)\n\n"
        f"Cargo: {job.get('title', 'Não informado')}\n"
        f"Empresa: {job.get('company', 'Não informada')}\n"
        f"Localização: {job.get('location', 'Não informada')}\n"
        f"Pontuação: {job.get('score', 0)}\n"
        f"Data de publicação: {job.get('published_at', 'Não informada')}\n"
        f"Fonte: {job.get('source', 'Himalayas')}\n"
        f"Principais motivos de compatibilidade:\n{reasons_lines}\n\n"
        f"Link direto: {job.get('source_url', 'Não informado')}"
    )


def send_telegram_alert(bot_token: str, chat_id: str, message: str, timeout: int = 15) -> bool:
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": message,
        "disable_web_page_preview": True,
    }

    try:
        response = requests.post(url, json=payload, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException:
        LOGGER.exception("Falha ao enviar mensagem para o Telegram.")
        return False

    return True
