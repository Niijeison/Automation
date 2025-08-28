#!/usr/bin/env python3
import re
import smtplib, ssl

# 🔹 Path to auth log
LOG_FILE = "/var/log/auth.log"

# 🔹 Email Settings
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
SENDER_EMAIL = "skoybrown@gmail..com"   # replace with your Gmail
APP_PASSWORD = "erzs rftp gxfg lkjd"      # replace with your Gmail App Password
RECEIVER_EMAIL = "skoybrown@gmail.com" # can be same as sender

# 🔹 Threshold
THRESHOLD = 5  

def check_failed_logins():
    failed_attempts = []

    with open(LOG_FILE, "r") as f:
        for line in f:
            if "Failed password" in line:
                failed_attempts.append(line.strip())

    return failed_attempts


def send_email_alert(attempts):
    message = f"""\
Subject: 🚨 SSH Brute Force Alert on Server

Warning: {len(attempts)} failed SSH login attempts detected!

Here are the last few:
{chr(10).join(attempts[-5:])}
"""

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, message)
        print("📧 Email alert sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")


if __name__ == "__main__":
    attempts = check_failed_logins()
    if attempts:
        print(f"🚨 {len(attempts)} failed SSH login attempts detected.")
        if len(attempts) >= THRESHOLD:
            send_email_alert(attempts)
    else:
        print("✅ No failed SSH logins found.")
