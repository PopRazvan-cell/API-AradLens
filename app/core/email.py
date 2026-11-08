import logging
import smtplib
from email.message import EmailMessage

from app.core.config import settings

logger = logging.getLogger(__name__)


def send_email(to: str, subject: str, body: str) -> bool:
    """Trimite un email text. Returneaza False daca SMTP nu e configurat."""
    if not settings.smtp_host or not settings.smtp_user or not to:
        logger.warning(
            "SMTP neconfigurat (SMTP_USER/SMTP_PASSWORD lipsa); email netrimis catre %s",
            to,
        )
        return False

    message = EmailMessage()
    message["From"] = settings.smtp_from or settings.smtp_user
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)

    try:
        if settings.smtp_use_ssl:
            server: smtplib.SMTP = smtplib.SMTP_SSL(
                settings.smtp_host, settings.smtp_port, timeout=20
            )
        else:
            server = smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20)

        with server:
            if settings.smtp_use_tls and not settings.smtp_use_ssl:
                server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(message)
        return True
    except Exception:
        logger.exception("Eroare la trimiterea emailului catre %s", to)
        return False


def send_password_reset_email(to: str, reset_link: str) -> bool:
    subject = "Resetare parola - AradLens Admin"
    body = (
        "Ai cerut resetarea parolei pentru contul de admin AradLens.\n\n"
        f"Deschide linkul de mai jos (valabil "
        f"{settings.password_reset_expire_minutes} minute):\n\n"
        f"{reset_link}\n\n"
        "Daca nu ai cerut tu acest lucru, ignora acest email."
    )
    return send_email(to, subject, body)
