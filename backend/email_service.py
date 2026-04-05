import os
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from dotenv import load_dotenv
from premailer import transform

load_dotenv("/opt/properties-by-magni/.env")


def get_email_template(content, title="Propio"):
    html = f"""
    <!DOCTYPE html>
    <html lang="is">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
    </head>
    <body>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #334155;
                background-color: #f8fafc;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 20px auto;
                background-color: #ffffff;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            }}
            .header {{
                background-color: #1e293b;
                padding: 30px;
                text-align: center;
                color: #ffffff;
            }}
            .header img {{
                max-width: 150px;
                height: auto;
                margin-bottom: 10px;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
                font-weight: 600;
                letter-spacing: -0.025em;
            }}
            .content {{
                padding: 40px 30px;
            }}
            .footer {{
                background-color: #f1f5f9;
                padding: 20px;
                text-align: center;
                font-size: 12px;
                color: #64748b;
            }}
            .button {{
                display: inline-block;
                padding: 12px 24px;
                background-color: #2563eb;
                color: #ffffff !important;
                text-decoration: none;
                border-radius: 6px;
                font-weight: 600;
                margin-top: 20px;
            }}
            .button:hover {{
                background-color: #1d4ed8;
            }}
            .link-alt {{
                margin-top: 20px;
                font-size: 13px;
                color: #94a3b8;
                word-break: break-all;
            }}
            @media only screen and (max-width: 600px) {{
                .container {{
                    margin: 0 !important;
                    width: 100% !important;
                    max-width: 100% !important;
                    border-radius: 0 !important;
                }}
                .content {{
                    padding: 30px 20px !important;
                }}
                .header {{
                    padding: 25px 20px !important;
                }}
                .header h1 {{
                    font-size: 20px !important;
                }}
                }}
            </style>
            <div class="container">
            <div class="header">
                <h1>Propio</h1>
            </div>
            <div class="content">
                {content}
            </div>
            <div class="footer">
                &copy; {2026} Propio. Allt rétt áskilinn.<br>
                Ef þú telur þig hafa fengið þennan póst fyrir mistök, vinsamlegast hunsaðu hann.
            </div>
        </div>
    </body>
    </html>
    """
    return transform(html)


def send_verification_email(to_email, verification_token):
    api_key = os.getenv("BREVO_API_KEY")
    from_email = "propertiesbymagni@propertiesbymagni.com"
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

    subject = "Verify your Propio account"
    content = f"""
        <h2 style="color: #1e293b; margin-top: 0;">Welcome to Propio!</h2>
        <p>Takk fyrir að skrá þig! Til að virkja aðganginn þinn og byrja að vaka yfir fasteignamarkaðnum, vinsamlegast smelltu á hnappinn hér að neðan:</p>
        <a href="{verification_link}" class="button">Virkja aðgang</a>
        <p style="margin-top: 30px;">Ef hnappurinn virkar ekki geturðu líka afritað og límt þennan hlekk í vafrann þinn:</p>
        <div class="link-alt">{verification_link}</div>
    """
    html_content = get_email_template(content, "Virkja aðgang - Propio")

    sender = {"name": "Propio", "email": from_email}
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
    from_email = "propertiesbymagni@propertiesbymagni.com"
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

    subject = "Endurstilla lykilorð fyrir Propio"
    content = f"""
        <h2 style="color: #1e293b; margin-top: 0;">Beiðni um endurstillingu lykilorðs</h2>
        <p>Þú baðst um að endurstilla lykilorðið þitt. Vinsamlegast smelltu á hnappinn hér að neðan til að velja nýtt lykilorð:</p>
        <a href="{reset_link}" class="button">Endurstilla lykilorð</a>
        <p style="margin-top: 30px;">Þessi hlekkur rennur út eftir 1 klukkustund.</p>
        <p>Ef þú baðst ekki um þetta getur þú hunsað þennan tölvupóst.</p>
        <div class="link-alt">{reset_link}</div>
    """
    html_content = get_email_template(content, "Endurstilla lykilorð - Propio")

    sender = {"name": "Propio", "email": from_email}
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
