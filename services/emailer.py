import os
import smtplib
import logging
from email.message import EmailMessage
from typing import Optional, Dict, Any

import requests

log = logging.getLogger(__name__)


def _from_email() -> str:
    sender = (os.getenv("SUPPORT_EMAIL") or "").strip()
    if sender:
        return sender
    log.warning("SUPPORT_EMAIL is not set; using a placeholder sender address")
    return "support@localhost"


def _base_url_fallback() -> Optional[str]:
    # Useful for background jobs; in request handlers prefer request.url_root.
    return os.getenv("BASE_URL")


def can_send_email() -> bool:
    if os.getenv("RESEND_API_KEY"):
        return True
    return bool(os.getenv("SMTP_HOST") and os.getenv("SMTP_USER") and (os.getenv("SMTP_PASS") or os.getenv("SMTP_PASSWORD")))


def send_email(to_email: str, subject: str, text: str, html: Optional[str] = None) -> Dict[str, Any]:
    """Send transactional email via Resend (preferred) or SMTP.

    Returns a dict with keys: ok (bool), provider (str), detail (str|dict).
    Never raises unless requests/smtplib unexpectedly explode beyond our catches.
    """
    to_email = (to_email or "").strip()
    if not to_email:
        return {"ok": False, "provider": "none", "detail": "missing_to_email"}

    resend_key = os.getenv("RESEND_API_KEY")
    if resend_key:
        try:
            r = requests.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {resend_key}", "Content-Type": "application/json"},
                json={
                    "from": _from_email(),
                    "to": [to_email],
                    "subject": subject,
                    "text": text,
                    **({"html": html} if html else {}),
                },
                timeout=10,
            )
            if r.ok:
                return {"ok": True, "provider": "resend", "detail": r.json() if r.content else {"status": r.status_code}}
            return {"ok": False, "provider": "resend", "detail": {"status": r.status_code, "body": (r.text[:500] if r.text else "")}}
        except Exception as e:
            return {"ok": False, "provider": "resend", "detail": str(e)}

    # SMTP fallback
    smtp_host = os.getenv("SMTP_HOST")
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS") or os.getenv("SMTP_PASSWORD")
    smtp_port = int(os.getenv("SMTP_PORT") or "587")
    smtp_tls = (os.getenv("SMTP_TLS", "true").lower() != "false")

    if not (smtp_host and smtp_user and smtp_pass):
        log.error(
            "Email sending is disabled: missing RESEND_API_KEY or incomplete SMTP config (need SMTP_HOST, SMTP_USER, SMTP_PASS)."
        )
        return {"ok": False, "provider": "smtp", "detail": "smtp_not_configured"}

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = _from_email()
    msg["To"] = to_email
    msg.set_content(text)
    if html:
        msg.add_alternative(html, subtype="html")

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            if smtp_tls:
                server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        return {"ok": True, "provider": "smtp", "detail": "sent"}
    except Exception as e:
        return {"ok": False, "provider": "smtp", "detail": str(e)}

