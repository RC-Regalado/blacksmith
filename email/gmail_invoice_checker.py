#!/usr/bin/env python3
"""
gmail_invoice_checker.py

Revisa la bandeja de Gmail en busca de correos de facturas, notificaciones
de consumo o gastos, extrae montos/metadatos y los envía por POST a un
servidor REST configurado en config.json.

Pensado para ejecutarse una vez al día vía cron o systemd timer.
"""

import base64
import json
import logging
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.json"
TOKEN_PATH = BASE_DIR / "token.json"
CREDENTIALS_PATH = BASE_DIR / "credentials.json"
SEEN_IDS_PATH = BASE_DIR / "seen_ids.json"
LOG_PATH = BASE_DIR / "gmail_invoice_checker.log"

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# Regex para detectar montos: $123.45, $ 1,234.56, 123.45 USD, "total: 45.00", etc.
AMOUNT_REGEX = re.compile(
    r"(?:\$|USD|GTQ|MXN|EUR|€)\s?(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)"
    r"|(?:total|monto|importe|a pagar|saldo)\s*[:\-]?\s*\$?\s?(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)",
    re.IGNORECASE,
)

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
console = logging.StreamHandler(sys.stdout)
console.setLevel(logging.INFO)
logging.getLogger().addHandler(console)


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        logging.error("No se encontró config.json en %s", CONFIG_PATH)
        sys.exit(1)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_seen_ids() -> set:
    if SEEN_IDS_PATH.exists():
        with open(SEEN_IDS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return set(data.get("ids", []))
    return set()


def save_seen_ids(ids: set):
    # Nos quedamos solo con los últimos 2000 para que el archivo no crezca sin límite
    trimmed = list(ids)[-2000:]
    with open(SEEN_IDS_PATH, "w", encoding="utf-8") as f:
        json.dump({"ids": trimmed}, f)


def get_gmail_service():
    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_PATH.exists():
                logging.error(
                    "Falta credentials.json (descárgalo desde Google Cloud Console). "
                    "Ver README.md para instrucciones."
                )
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_PATH), SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "w", encoding="utf-8") as token_file:
            token_file.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def get_message_body(payload: dict) -> str:
    """Extrae el texto plano de un mensaje de Gmail, recorriendo partes anidadas."""
    if "parts" in payload:
        texts = []
        for part in payload["parts"]:
            texts.append(get_message_body(part))
        return "\n".join(t for t in texts if t)

    if payload.get("mimeType") == "text/plain" and "data" in payload.get("body", {}):
        data = payload["body"]["data"]
        return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

    if payload.get("mimeType") == "text/html" and "data" in payload.get("body", {}):
        data = payload["body"]["data"]
        html = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
        # Limpieza muy básica de HTML para poder buscar montos en el texto
        return re.sub(r"<[^>]+>", " ", html)

    return ""


def extract_amounts(text: str) -> list:
    amounts = []
    for match in AMOUNT_REGEX.finditer(text):
        raw = match.group(1) or match.group(2)
        if raw:
            amounts.append(raw)
    # quitar duplicados manteniendo orden
    seen = set()
    unique = []
    for a in amounts:
        if a not in seen:
            seen.add(a)
            unique.append(a)
    return unique


def get_header(headers: list, name: str) -> str:
    for h in headers:
        if h.get("name", "").lower() == name.lower():
            return h.get("value", "")
    return ""


def fetch_candidate_messages(service, query: str, max_results: int) -> list:
    results = (
        service.users()
        .messages()
        .list(userId="me", q=query, maxResults=max_results)
        .execute()
    )
    return results.get("messages", [])


def process_message(service, msg_id: str) -> dict:
    msg = (
        service.users()
        .messages()
        .get(userId="me", id=msg_id, format="full")
        .execute()
    )
    headers = msg["payload"].get("headers", [])
    subject = get_header(headers, "Subject")
    sender = get_header(headers, "From")
    date = get_header(headers, "Date")
    body_text = get_message_body(msg["payload"])
    amounts = extract_amounts(subject + "\n" + body_text)

    return {
        "message_id": msg_id,
        "subject": subject,
        "sender": sender,
        "date": date,
        "snippet": msg.get("snippet", ""),
        "amounts_detected": amounts,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


def send_to_rest(endpoint: str, payload: dict, timeout: int = 10) -> bool:
    try:
        resp = requests.post(endpoint, json=payload, timeout=timeout)
        resp.raise_for_status()
        return True
    except requests.RequestException as e:
        logging.error("Falló el envío al servidor REST para %s: %s", payload.get("message_id"), e)
        return False


def main():
    config = load_config()
    query = config.get("gmail_query", "newer_than:1d (factura OR invoice OR consumo OR recibo OR \"estado de cuenta\")")
    rest_endpoint = config["rest_endpoint"]
    max_results = config.get("max_results", 50)

    seen_ids = load_seen_ids()
    service = get_gmail_service()

    candidates = fetch_candidate_messages(service, query, max_results)
    logging.info("Encontrados %d correos candidatos con query: %s", len(candidates), query)

    new_count = 0
    for m in candidates:
        msg_id = m["id"]
        if msg_id in seen_ids:
            continue

        data = process_message(service, msg_id)
        sent_ok = send_to_rest(rest_endpoint, data)

        if sent_ok:
            logging.info(
                "Enviado: '%s' de %s | montos detectados: %s",
                data["subject"], data["sender"], data["amounts_detected"]
            )
        seen_ids.add(msg_id)
        new_count += 1

    save_seen_ids(seen_ids)
    logging.info("Procesamiento completo. %d correos nuevos procesados.", new_count)


if __name__ == "__main__":
    main()
