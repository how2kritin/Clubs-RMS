import os
from typing import Dict, List

from mailersend import emails

api_key = os.getenv("MAILERSEND_API_KEY", "OOF")
domain = os.getenv("MAILERSEND_DOMAIN", "clubsplusplus.com")


def send_email(recipients: List[Dict[str, str]], subject: str, content: str) -> None:
    mailer = emails.NewEmail(api_key)

    mail_body = {}

    mail_from = {
        "name": "Clubs Plus Plus",
        "email": f"cpp@{domain}",
    }

    reply_to = [
        {
            "name": "reply",
            "email": f"reply@{domain}",
        }
    ]

    mailer.set_mail_from(mail_from, mail_body)
    mailer.set_mail_to(recipients, mail_body)
    mailer.set_subject(subject, mail_body)
    mailer.set_html_content(content, mail_body)
    mailer.set_reply_to(reply_to, mail_body)

    mailer.send(mail_body)


if __name__ == "__main__":
    print(api_key)
    print(domain)

    recipients = [
        {"name": "Varun Edachali", "email": "varun.edachali@students.iiit.ac.in"}
    ]
    subject = "Test Email"
    content = "<h1>Hello, this is a test email!</h1>"

    send_email(recipients, subject, content)
