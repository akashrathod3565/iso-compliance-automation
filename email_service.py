import smtplib
from email.mime.text import MIMEText


def send_email(to_email, supplier_name, status, days_left):

    sender = "your_email@gmail.com"
    password = "your_app_password"

    subject = "ISO 9001 Compliance Alert"

    if status == "Red":
        body = f"""
        Dear {supplier_name},

        Your ISO 9001 certificate has EXPIRED.
        Please submit a renewed certificate immediately.

        Regards,
        Compliance Team
        """

    elif status == "Amber":
        body = f"""
        Dear {supplier_name},

        Your ISO 9001 certificate will expire in {days_left} days.
        Please renew and upload updated certificate.

        Regards,
        Compliance Team
        """

    else:
        return  # No email for Green

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.send_message(msg)
