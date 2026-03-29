import os
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from dotenv import load_dotenv

load_dotenv("/opt/properties-by-magni/.env")


def send_verification_email(to_email, verification_token):
    api_key = os.getenv("BREVO_API_KEY")
    from_email = os.getenv("FROM_EMAIL", "magnimarboss@gmail.com")
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")

    if not api_key:
        print("BREVO_API_KEY not found in environment. Email not sent.")
        return False

    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key["api-key"] = api_key

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    verification_link = f"{frontend_url}/verify-email?token={verification_token}"

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
        to=to, html_content=html_content, sender=sender, subject=subject
    )

    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        print(
            f"Email sent successfully to {to_email}. Message ID: {api_response.message_id}"
        )
        return True
    except ApiException as e:
        print(f"Exception when calling TransactionalEmailsApi->send_transac_email: {e}")
        return False


def send_password_reset_email(to_email, reset_token):
    api_key = os.getenv("BREVO_API_KEY")
    from_email = os.getenv("FROM_EMAIL", "magnimarboss@gmail.com")
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")

    if not api_key:
        print("BREVO_API_KEY not found in environment. Email not sent.")
        return False

    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key["api-key"] = api_key

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    reset_link = f"{frontend_url}/reset-password?token={reset_token}"

    subject = "Endurstilla lykilorð fyrir Properties by Magni"
    html_content = f"""
    <html>
        <body>
            <h1>Beiðni um endurstillingu lykilorðs</h1>
            <p>Þú baðst um að endurstilla lykilorðið þitt. Vinsamlegast smelltu á hlekkinn hér að neðan til að velja nýtt lykilorð:</p>
            <p><a href="{reset_link}">{reset_link}</a></p>
            <p>Þessi hlekkur rennur út eftir 1 klukkustund.</p>
            <p>Ef þú baðst ekki um þetta getur þú hundsað þennan tölvupóst.</p>
        </body>
    </html>
    """

    sender = {"name": "Properties by Magni", "email": from_email}
    to = [{"email": to_email}]

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=to, html_content=html_content, sender=sender, subject=subject
    )

    try:
        api_instance.send_transac_email(send_smtp_email)
        print(f"Password reset email sent to {to_email}.")
        return True
    except ApiException as e:
        print(f"Exception when calling TransactionalEmailsApi->send_transac_email: {e}")
        return False
