import smtplib
from email.mime.text import MIMEText
import datetime

import dotenv
import os

dotenv.load_dotenv()

def send_verify_email(email, jwt):
    from_email = os.getenv("EMAIL")
    from_password = os.getenv("EMAIL_PWD")
    to_email = email

    message = f"Please click the link to verify your account. http://localhost:3000/verify/{jwt}"
    msg = MIMEText(message, 'html')
    msg['Subject'] = "Account Verification"
    msg['To'] = to_email
    msg['From'] = from_email

    gmail=smtplib.SMTP('smtp.gmail.com', 587)
    gmail.ehlo()
    gmail.starttls()
    gmail.login(from_email, from_password)
    gmail.send_message(msg)
    return

def send_alert_email(email, data):
    from_email = os.getenv("EMAIL")
    from_password = os.getenv("EMAIL_PWD")
    to_email = email
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if data['operator'] == ">=":
        operator = "greater"
    else:
        operator = "less"

    if data['alert_type'] == "average":
        message = f"Your alert for {data['full_name']} ({data['ticker'].upper()}) has triggered at {current_time} EST. \
The {data['MA_period']} day average is now {operator} than ${data['trigger_price']}. \
The {data['MA_period']} day average is currently at ${data['current_value']} and the current stock price is at ${data['current_price']}."
    else:
        message = f"Your alert for {data['full_name']} ({data['ticker'].upper()}) has triggered at {current_time} EST. \
The current stock price is now {operator} than ${data['trigger_price']}. The current stock price is at ${data['current_price']}."

    msg = MIMEText(message, 'html')
    msg['Subject'] = "Stock Alert Triggered!"
    msg['To'] = to_email
    msg['From'] = from_email

    gmail=smtplib.SMTP('smtp.gmail.com', 587)
    gmail.ehlo()
    gmail.starttls()
    gmail.login(from_email, from_password)
    gmail.send_message(msg)
    return