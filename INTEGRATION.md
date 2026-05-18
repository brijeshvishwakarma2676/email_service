# Lumina Generic Email Service — Integration Protocol

Welcome to the **Lumina Generic Email Service** integration guide. This microservice provides an extremely fast, secure, and reliable pipeline to deliver HTML templates and raw text emails using standard SMTP infrastructure.

---

## 🔒 Authentication & Protocol Specifications

All outbound requests to this service must be authenticated and conform to the following specifications:

*   **Base URL**: `http://localhost:8005/api/v1`
*   **Authentication Header**: `X-API-Key`
    > [!IMPORTANT]
    > The request will fail with a `401 Unauthorized` error if the `X-API-Key` header is missing or does not match the key configured in the `.env` file of the email service.

---

## 📡 Endpoint: Send Email

*   **HTTP Method**: `POST`
*   **Path**: `/send`
*   **Content-Type**: `application/json`

### 📋 Request Schema Parameters

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| **`to_email`** | `str` or `List[str]` | **Yes** | Single email string, a comma-separated string, or a JSON array of recipient email addresses. |
| **`subject`** | `str` | **Yes** | The subject line of the email. |
| **`html_content`** | `str` | *No* | Raw HTML markup for the body. (Bypassed if `template_name` is provided). |
| **`text_content`** | `str` | *No* | Plain text fallback content for email clients that do not render HTML. |
| **`template_name`** | `str` | *No* | Name of a template file inside the `/templates` folder (e.g. `"index.html"`). |
| **`template_context`** | `dict` | *No* | Key-value pairs for dynamic variable interpolation inside the selected Jinja2 template. |
| **`sender_email`** | `str` | *No* | Override the default `From` address. Must be supported/allowed by your SMTP server config. |
| **`sender_name`** | `str` | *No* | A friendly display name for the sender (e.g. `"Lumina Support"`). |

---

## 💻 Integration Examples

Here is how you can connect your existing portals and platforms to this email service:

### 1. Bash / cURL
```bash
curl -X POST "http://localhost:8005/api/v1/send" \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your-configured-api-key" \
     -d '{
       "to_email": "merchant@example.com",
       "subject": "System Verification Required",
       "template_name": "index.html",
       "template_context": {
         "title": "System Alert",
         "heading": "Verify Outbound Protocol",
         "body": "Your loyalty portal analytics system has been updated. Please click the button below to verify the synchronization."
       },
       "sender_name": "Lumina Protocol Support"
     }'
```

### 2. Python (Requests Library)
```python
import requests

def dispatch_email(recipient: str, heading: str, body: str):
    url = "http://localhost:8005/api/v1/send"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": "your-configured-api-key"
    }
    payload = {
        "to_email": recipient,
        "subject": f"Lumina Update: {heading}",
        "template_name": "index.html",
        "template_context": {
            "title": "Account Notification",
            "heading": heading,
            "body": body
        },
        "sender_name": "Lumina Automated Relay"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Network error during email dispatch: {e}")
        return None
```

### 3. JavaScript (Modern Fetch API / Node.js)
```javascript
async function sendNotification(recipient, title, message) {
  const url = "http://localhost:8005/api/v1/send";
  
  const payload = {
    to_email: recipient,
    subject: title,
    template_name: "index.html",
    template_context: {
      title: "System Update",
      heading: title,
      body: message
    },
    sender_name: "Lumina Control Center"
  };

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "your-configured-api-key"
      },
      body: JSON.stringify(payload)
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "Dispatch operation failed.");
    }
    console.log("Email dispatched successfully:", data);
  } catch (error) {
    console.error("Integration Error:", error.message);
  }
}
```

---

## 🎨 Customizing Templates

To register a new HTML layout:
1.  Navigate to the `/templates` folder.
2.  Create your custom HTML file (e.g. `welcome.html`).
3.  Inject placeholders using double curly-braces (e.g. `{{ username }}`).
4.  Call the endpoint with `"template_name": "welcome.html"`, and pass `"username": "Brijesh"` inside the `"template_context"` payload parameters.

---

## ⚠️ Error Resolution & Diagnostics

The service returns precise HTTP status codes:

*   `401 Unauthorized`: The `X-API-Key` is missing or incorrect.
*   `422 Unprocessable Entity`: The request payload lacks required fields (like `to_email`), or the Jinja2 compiler failed to render the selected template due to syntax errors.
*   `500 Internal Server Error`: The SMTP server could not be reached, authentication failed, or connection timed out. Check terminal output logs for a complete error stack trace.
