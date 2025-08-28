#!/usr/bin/env python3

import shutil
import os
import psutil
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# -------- Settings --------
THRESHOLD = 5  # %
EMAIL_FROM = "skoybrown@gmail.com"
EMAIL_TO = "skoybrown@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = "skoybrown@gmail.com"
EMAIL_PASS = "yybo pbsq gfdc bnnp"  # use App Password, not your main Gmail password

# -------- System Checks --------
total, used, free = shutil.disk_usage("/")
disk_percent = used / total * 100
cpu_usage = psutil.cpu_percent(interval=1)
memory_usage = psutil.virtual_memory().percent

with open("/proc/uptime", "r") as f:
    uptime_seconds = float(f.readline().split()[0])
    uptime_hours = uptime_seconds / 3600

users = os.popen("who").read().strip()

# -------- Report --------
report = f"""
Linux Health Monitor Report
===========================
Disk Usage   : {disk_percent:.2f}%
CPU Usage    : {cpu_usage}%
Memory Usage : {memory_usage}%
Uptime       : {uptime_hours:.2f} hours
Users Logged : {users if users else 'No active users'}
"""

print(report)

# -------- Email Alert --------
def send_alert(subject, message):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg["Subject"] = subject
    msg.attach(MIMEText(message, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
            print(f"✅ Alert email sent to {EMAIL_TO}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# Trigger alert if threshold crossed
if cpu_usage > THRESHOLD or memory_usage > THRESHOLD or disk_percent > THRESHOLD:
    send_alert("⚠️ Linux Health Alert", report)
