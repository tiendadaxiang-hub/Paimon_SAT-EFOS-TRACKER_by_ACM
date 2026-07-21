"""
notifier.py — Notificaciones opcionales por correo cuando hay cambios en el listado

Configura mediante variables de entorno (ver config.py):
    EFOS_SMTP_HOST, EFOS_SMTP_PORT, EFOS_SMTP_USER, EFOS_SMTP_PASS
    EFOS_NOTIFY_FROM, EFOS_NOTIFY_TO
"""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import config
from differ import resumen_texto

logger = logging.getLogger(__name__)


def _smtp_configurado() -> bool:
    return all([
        config.SMTP_HOST,
        config.SMTP_USER,
        config.SMTP_PASSWORD,
        config.NOTIFY_FROM,
        config.NOTIFY_TO,
    ])


def enviar_reporte(diff: dict) -> bool:
    """
    Envía un correo con el resumen de cambios si hay novedades.

    Returns True si el correo se envió, False si no había config o no había cambios.
    """
    if not config.NOTIFY_ON_NEW:
        logger.info("[notifier] Notificaciones desactivadas.")
        return False

    if not _smtp_configurado():
        logger.info("[notifier] SMTP no configurado — omitiendo notificación.")
        return False

    n_nuevos  = len(diff.get("nuevos", []))
    n_cambios = len(diff.get("cambios", []))
    n_bajas   = len(diff.get("bajas", []))

    if n_nuevos + n_cambios + n_bajas == 0:
        logger.info("[notifier] Sin cambios relevantes — no se envía correo.")
        return False

    asunto = (
        f"[SAT 69-B] Cambios detectados: "
        f"+{n_nuevos} nuevos | {n_cambios} cambios | -{n_bajas} bajas"
    )
    cuerpo_texto = resumen_texto(diff)
    cuerpo_html  = _texto_a_html(cuerpo_texto)

    destinatarios = [d.strip() for d in config.NOTIFY_TO.split(",") if d.strip()]

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = asunto
        msg["From"]    = config.NOTIFY_FROM
        msg["To"]      = ", ".join(destinatarios)

        msg.attach(MIMEText(cuerpo_texto, "plain", "utf-8"))
        msg.attach(MIMEText(cuerpo_html,  "html",  "utf-8"))

        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(config.SMTP_USER, config.SMTP_PASSWORD)
            server.sendmail(config.NOTIFY_FROM, destinatarios, msg.as_string())

        logger.info(f"[notifier] Correo enviado a: {destinatarios}")
        return True

    except Exception as e:
        logger.error(f"[notifier] Error al enviar correo: {e}")
        return False


def _texto_a_html(texto: str) -> str:
    """Convierte el resumen de texto plano a HTML básico para el correo."""
    lineas = []
    for linea in texto.split("\n"):
        linea_esc = (
            linea
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        if linea.startswith("="):
            lineas.append(f"<hr>")
        elif linea.startswith("──"):
            lineas.append(f"<h3 style='color:#c0392b;font-family:monospace'>{linea_esc}</h3>")
        elif "NUEVO" in linea or "⚠" in linea:
            lineas.append(f"<p style='color:#e74c3c;font-family:monospace'>{linea_esc}</p>")
        elif "→" in linea:
            lineas.append(f"<p style='color:#e67e22;font-family:monospace'>{linea_esc}</p>")
        elif linea.strip():
            lineas.append(f"<p style='font-family:monospace'>{linea_esc}</p>")

    return f"""
    <html><body style="background:#1a1a2e;color:#e0e0e0;padding:20px">
      <h2 style="color:#00d4ff;font-family:sans-serif">
        SAT Art. 69-B CFF — Reporte de cambios
      </h2>
      {''.join(lineas)}
      <hr>
      <p style="font-size:11px;color:#888">
        Fuente: <a href="{config.SAT_PORTAL_URL}" style="color:#00d4ff">
        portal SAT</a> — descarga automatizada.
        Este reporte es de referencia operativa; verifica siempre en la fuente oficial.
      </p>
    </body></html>
    """
