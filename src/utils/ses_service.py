# src/utils/ses_service.py
import os
from html import escape
import boto3
from botocore.exceptions import ClientError

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
SES_FROM_EMAIL = os.getenv("SES_FROM_EMAIL")

if not SES_FROM_EMAIL:
    raise ValueError("SES_FROM_EMAIL environment variable is not set.")

if not AWS_REGION:
    raise ValueError("AWS_REGION environment variable is not set.")

ses = boto3.client("ses", region_name=AWS_REGION)

if not ses:
    raise ValueError("Failed to create SES client. Check AWS credentials and configuration.")


def is_unverified_email_rejection(error: Exception) -> bool:
    if not isinstance(error, ClientError):
        return False

    error_details = error.response.get("Error", {})
    return (
        error_details.get("Code") == "MessageRejected"
        and "Email address is not verified" in error_details.get("Message", "")
    )


def _verification_message(code: str, requested_email: str | None = None) -> dict:
    subject = "Your verification code"
    requested_for = f"\nRequested for: {requested_email}" if requested_email else ""
    escaped_email = escape(requested_email) if requested_email else ""
    requested_for_html = (
        f"<p><strong>Requested for:</strong> {escaped_email}</p>"
        if requested_email
        else ""
    )
    body_text = f"Your verification code is: {code}{requested_for}\nThis code expires soon."
    body_html = f"""
    <html><body>
      <p>Your verification code is:</p>
      <h2>{code}</h2>
      {requested_for_html}
      <p>This code expires soon.</p>
    </body></html>
    """
    return {
        "Subject": {"Data": subject, "Charset": "UTF-8"},
        "Body": {
            "Text": {"Data": body_text, "Charset": "UTF-8"},
            "Html": {"Data": body_html, "Charset": "UTF-8"},
        },
    }


def send_verification_code(to_email: str, code: str) -> dict:
    message = _verification_message(code)
    try:
        ses.send_email(
            Source=SES_FROM_EMAIL,
            Destination={"ToAddresses": [to_email]},
            Message=message,
        )
        return {"requires_admin_code": False, "sent_to": to_email}
    except Exception as error:
        if not is_unverified_email_rejection(error):
            raise

    admin_message = _verification_message(code, requested_email=to_email)
    ses.send_email(
        Source=SES_FROM_EMAIL,
        Destination={"ToAddresses": [SES_FROM_EMAIL]},
        Message=admin_message,
    )
    return {
        "requires_admin_code": True,
        "sent_to": SES_FROM_EMAIL,
        "admin_email": SES_FROM_EMAIL,
    }
