import smtplib
import logging
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import List, Dict, Any, Optional

from app.config import settings

logger = logging.getLogger(__name__)

# Setup template directory
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates")
os.makedirs(TEMPLATES_DIR, exist_ok=True)

# Setup Jinja2 environment
template_env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(["html", "xml"])
)

def render_template(template_name: str, context: Dict[str, Any]) -> str:
    """Render a template with a given context dictionary."""
    try:
        template = template_env.get_template(template_name)
        return template.render(**(context or {}))
    except Exception as e:
        logger.error(f"Error rendering template {template_name}: {str(e)}")
        raise RuntimeError(f"Template rendering failed: {str(e)}")

def send_email_message(
    recipients: List[str],
    subject: str,
    html_body: Optional[str] = None,
    text_body: Optional[str] = None,
    sender_name: Optional[str] = None,
    sender_email: Optional[str] = None
):
    """
    Constructs and sends a MIME email message via SMTP.
    """
    smtp_from_email = sender_email or settings.DEFAULT_FROM_EMAIL
    
    # Format 'From' field: e.g. "PointNest Protocol <no-reply@pointnest.com>"
    if sender_name:
        from_display = f"{sender_name} <{smtp_from_email}>"
    else:
        from_display = smtp_from_email

    # Create message container
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_display
    msg["To"] = ", ".join(recipients)

    # Attach plain text part if provided
    if text_body:
        msg.attach(MIMEText(text_body, "plain", "utf-8"))

    # Attach HTML part if provided
    if html_body:
        msg.attach(MIMEText(html_body, "html", "utf-8"))
    elif not text_body:
        # Fallback to an empty text message if nothing is supplied
        msg.attach(MIMEText("", "plain", "utf-8"))

    # Establish SMTP connection
    try:
        logger.info(f"Connecting to SMTP server {settings.SMTP_HOST}:{settings.SMTP_PORT}...")
        
        # Check SSL configuration
        if settings.SMTP_USE_SSL:
            server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10)
        else:
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10)
            
            # Start TLS if enabled
            if settings.SMTP_USE_TLS:
                server.ehlo()
                server.starttls()
                server.ehlo()

        # Login to SMTP server
        if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
            logger.info("Logging into SMTP server...")
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)

        # Send email
        logger.info(f"Sending email to: {recipients}...")
        server.sendmail(smtp_from_email, recipients, msg.as_string())
        server.quit()
        logger.info("Email sent successfully!")
        
    except smtplib.SMTPResponseException as e:
        logger.error(f"SMTP Error during email delivery: Code {e.smtp_code} - {e.smtp_error.decode('utf-8', errors='ignore')}")
        raise RuntimeError(f"SMTP Error: {e.smtp_code} - {e.smtp_error.decode('utf-8', errors='ignore')}")
    except Exception as e:
        logger.error(f"Unexpected connection error while sending email: {str(e)}")
        raise RuntimeError(f"Email delivery failed: {str(e)}")
