#!/usr/bin/env python3
import subprocess
import datetime
import sys
import os
import smtplib
from email.mime.text import MIMEText

# Service to monitor (can be passed as argument)
SERVICE = sys.argv[1] if len(sys.argv) > 1 else "nginx"

# Log file
LOG_FILE = "/var/log/service_checker.log"

# Email settings (replace with your details)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
EMAIL_USER = "skoybrown@gmail.com"   # your Gmail
EMAIL_PASS = "yybo pbsq gfdc bnnp"          # Google App Password
EMAIL_TO   = "skoybrown@gmail.com"   # recipient (can be same as sender)


def log_message(message, level="INFO"):
    """Write a timestamped message to the log file."""
    try:
        with open(LOG_FILE, "a") as log:
            log.write(f"{datetime.datetime.now()} [{level}] {message}\n")
    except PermissionError:
        print(f"Error: Cannot write to {LOG_FILE}. Check permissions.")
        sys.exit(1)


def send_email(subject, body):
    """Send an email alert."""
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_USER
        msg["To"] = EMAIL_TO

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, [EMAIL_TO], msg.as_string())

        log_message(f"Email sent: {subject}", "INFO")
    except Exception as e:
        log_message(f"Failed to send email: {e}", "ERROR")


def is_service_active(service):
    """Check if the service is active."""
    try:
        result = subprocess.run(
            ["systemctl", "is-active", service],
            capture_output=True, text=True
        )
        return result.stdout.strip() == "active"
    except Exception as e:
        log_message(f"Error checking service {service}: {e}", "ERROR")
        return False


def restart_service(service):
    """Attempt to restart the service."""
    try:
        subprocess.run(["sudo", "systemctl", "restart", service], check=True)
        log_message(f"Service {service} restarted successfully.", "INFO")
        send_email(
            f"✅ {service} restarted",
            f"The service '{service}' was down but has been restarted successfully."
        )
        return True
    except Exception as e:
        log_message(f"Failed to restart {service}: {e}", "ERROR")
        send_email(
            f"❌ Failed to restart {service}",
            f"Attempt to restart '{service}' failed. Error: {e}"
        )
        return False


if __name__ == "__main__":
    # Check if log file is writable
    if not os.access(os.path.dirname(LOG_FILE) or ".", os.W_OK):
        print(f"Error: No write permission for {LOG_FILE}.")
        sys.exit(1)

    if is_service_active(SERVICE):
        log_message(f"Service {SERVICE} is running.", "INFO")
    else:
        log_message(f"Service {SERVICE} is down. Restarting...", "WARNING")
        if restart_service(SERVICE):
            if is_service_active(SERVICE):
                log_message(f"Service {SERVICE} restarted successfully.", "INFO")
            else:
                log_message(f"Service {SERVICE} failed to restart.", "ERROR")
