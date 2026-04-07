import os
import sys
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from dotenv import load_dotenv

load_dotenv("/opt/properties-by-magni/.env")

def send_email(to_email, subject, body):
    api_key = os.getenv("BREVO_API_KEY")
    from_email = "fundvis@fundvis.is"

    if not api_key:
        print("BREVO_API_KEY not found in environment.")
        return False

    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key["api-key"] = api_key
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    # Convert plain text to simple HTML
    html_content = body.replace("\n", "<br>")

    sender = {"name": "Fundvís", "email": from_email}
    to = [{"email": to_email}]

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=to, html_content=html_content, sender=sender, subject=subject
    )

    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        print(f"Email sent successfully! Message ID: {api_response.message_id}")
        return True
    except ApiException as e:
        print(f"Failed to send email: {e}")
        return False

def process_and_send(file_path, to_email):
    try:
        with open(file_path, "r") as f:
            lines = f.readlines()
            
        subject = ""
        body = ""
        
        if lines[0].startswith("Subject: "):
            subject = lines[0].replace("Subject: ", "").strip()
            body = "".join(lines[1:]).strip()
        else:
            subject = "Fundvís Email"
            body = "".join(lines).strip()
            
        # Replace placeholders
        body = body.replace("[Date]", "April 7, 2026").replace("[Amount]", "999 ISK")
        
        print(f"Sending {file_path} to {to_email}...")
        send_email(to_email, subject, body)
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":
    to_email = "magnimar@live.com"
    process_and_send("/opt/properties-by-magni/compliance/welcome_email.txt", to_email)
    print("---")
    process_and_send("/opt/properties-by-magni/compliance/receipt_email.txt", to_email)

