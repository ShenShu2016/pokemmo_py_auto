import os
import smtplib
from email.mime.text import MIMEText

from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()


def send_email():
    subject = "闪光闪光闪光闪光闪光闪光闪光闪光闪光t"
    body = "快点看看有闪光精灵"
    sender = os.getenv("SENDER")
    recipients = os.getenv("RECIPIENTS").split(",")
    password = os.getenv("PASSWORD")
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, recipients, msg.as_string())
    print("Message sent!")
