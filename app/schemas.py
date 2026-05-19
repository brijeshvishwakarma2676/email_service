from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import List, Dict, Any, Optional

class EmailSendRequest(BaseModel):
    to_email: str | List[str] = Field(
        ..., 
        description="Single email string or a list of recipient email addresses."
    )
    subject: str = Field(..., min_length=1, description="Subject line of the email.")
    
    # Body options (one of these should be present, or we default to a blank body)
    html_content: Optional[str] = Field(
        None, 
        description="Raw HTML string content to send as the email body."
    )
    text_content: Optional[str] = Field(
        None, 
        description="Plain text content to send as the email body."
    )
    
    # Templating option (e.g., rendering index.html with context)
    template_name: Optional[str] = Field(
        None, 
        description="Name of the template file (e.g., 'index.html')."
    )
    template_context: Optional[Dict[str, Any]] = Field(
        None, 
        description="Key-value pairs to render inside the HTML template."
    )

    # Sender override options
    sender_email: Optional[EmailStr] = Field(
        None, 
        description="Optional custom sender email address. Defaults to configured SMTP email."
    )
    sender_name: Optional[str] = Field(
        None, 
        description="Optional friendly name of the sender (e.g. 'PointNest Protocol')."
    )

    @field_validator("to_email")
    @classmethod
    def validate_recipients(cls, v):
        if isinstance(v, str):
            # Check if it's a comma-separated list or a single email
            emails = [e.strip() for e in v.split(",") if e.strip()]
            if not emails:
                raise ValueError("At least one recipient email address is required.")
            return emails
        if isinstance(v, list):
            if not v:
                raise ValueError("At least one recipient email address is required.")
            return [e.strip() for e in v if e.strip()]
        return v
