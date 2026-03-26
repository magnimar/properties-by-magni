import os
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from dotenv import load_dotenv

load_dotenv()

def send_verification_email(to_email, verification_token):
    api_key = os.getenv("BREVO_API_KEY")
    from_email = os.getenv("FROM_EMAIL", "magnimarboss@gmail.com")
    
    if not api_key:
        print("BREVO_API_KEY not found in environment. Email not sent.")
        return False

    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = api_key
    
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    
    verification_link = f"http://localhost:5173/verify-email?token={verification_token}"
    
    subject = "Verify your Properties by Magni account"
    html_content = f"""
    <html>
        <body>
            <h1>Welcome to Properties by Magni!</h1>
            <p>Please click the link below to verify your email address and activate your account:</p>
            <p><a href="{verification_link}">{verification_link}</a></p>
            <p>If you did not create an account, you can safely ignore this email.</p>
        </body>
    </html>
    """
    
    sender = {"name": "Properties by Magni", "email": from_email}
    to = [{"email": to_email}]
    
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=to,
        html_content=html_content,
        sender=sender,
        subject=subject
    )

    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        print(f"Email sent successfully to {to_email}. Message ID: {api_response.message_id}")
        return True
    except ApiException as e:
        print(f"Exception when calling TransactionalEmailsApi->send_transac_email: {e}")
        return False
