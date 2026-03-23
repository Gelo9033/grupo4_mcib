import os
import urllib.parse
import urllib.request


def _enviar_texto_telegram(texto: str) -> None:
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = urllib.parse.urlencode(
        {
            "chat_id": chat_id,
            "text": texto,
        }
    ).encode("utf-8")

    req = urllib.request.Request(url, data=payload, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=4):
            pass
    except Exception:
        # No rompe el login si Telegram falla
        pass


def enviar_alerta_telegram(usuario: str, ip: str) -> None:
    texto = (
        "ALERTA API BANK\n"
        "Intento fallido de login\n"
        f"Usuario: {usuario}\n"
        f"IP: {ip}"
    )
    _enviar_texto_telegram(texto)


def enviar_alerta_saldo_insuficiente(usuario: str, monto: float, saldo: float) -> None:
    texto = (
        "ALERTA API BANK\n"
        "Intento de transferencia sin fondos\n"
        f"Usuario: {usuario}\n"
        f"Monto intento: {monto}\n"
        f"Saldo disponible: {saldo}"
    )
    _enviar_texto_telegram(texto)