from fastapi import APIRouter, Header, HTTPException, status
import logging

from app.schemas import EmailSendRequest
from app.config import settings
from app.service import render_template, send_email_message

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["emails"])

def verify_api_key(x_api_key: str = Header(None, alias="X-API-Key")):
    """
    Validate the incoming request's API key header to secure the generic service.
    """
    if settings.API_KEY and x_api_key != settings.API_KEY:
        logger.warning("Unauthorized request: Missing or invalid API Key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Invalid or missing API key."
        )

@router.post("/send", status_code=status.HTTP_200_OK)
def send_email(payload: EmailSendRequest, x_api_key: str = Header(None, alias="X-API-Key")):
    # 1. Enforce API security
    verify_api_key(x_api_key)
    
    # 2. Determine final HTML body (either template or raw html_content)
    html_body = payload.html_content
    
    if payload.template_name:
        logger.info(f"Rendering HTML body using template: {payload.template_name}")
        try:
            html_body = render_template(payload.template_name, payload.template_context or {})
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Template compilation failed: {str(e)}"
            )
            
    # 3. Perform email delivery
    try:
        send_email_message(
            recipients=payload.to_email,
            subject=payload.subject,
            html_body=html_body,
            text_body=payload.text_content,
            sender_name=payload.sender_name,
            sender_email=payload.sender_email
        )
        return {
            "success": True,
            "message": "Email dispatched successfully.",
            "recipients": payload.to_email,
            "subject": payload.subject
        }
    except Exception as e:
        logger.exception("Failed to dispatch email")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Email delivery failed: {str(e)}"
        )
