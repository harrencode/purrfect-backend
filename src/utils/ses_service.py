# src/utils/ses_service.py
import os
import boto3

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
SES_FROM_EMAIL = os.getenv("SES_FROM_EMAIL")

if not SES_FROM_EMAIL:
    raise ValueError("SES_FROM_EMAIL environment variable is not set.")

if not AWS_REGION:
    raise ValueError("AWS_REGION environment variable is not set.")

ses = boto3.client("ses", region_name=AWS_REGION)

if not ses:
    raise ValueError("Failed to create SES client. Check AWS credentials and configuration.")

def send_verification_code(to_email: str, code: str) -> None:
    subject = "Your verification code"
    body_text = f"Your verification code is: {code}\nThis code expires soon."
    body_html = f"""
    <html><body>
      <p>Your verification code is:</p>
      <h2>{code}</h2>
      <p>This code expires soon.</p>
    </body></html>
    """

    ses.send_email(
        Source=SES_FROM_EMAIL,
        Destination={"ToAddresses": [to_email]},
        Message={
            "Subject": {"Data": subject, "Charset": "UTF-8"},
            "Body": {
                "Text": {"Data": body_text, "Charset": "UTF-8"},
                "Html": {"Data": body_html, "Charset": "UTF-8"},
            },
        },
    )
