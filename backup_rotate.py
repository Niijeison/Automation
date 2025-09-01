#!/usr/bin/env python3
import os
import tarfile
import datetime
import glob
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 📂 Paths
SOURCE_DIR = "/home/jeison/Buerkie/nii"
BACKUP_DIR = "/home/jeison/backups"
MAX_BACKUPS = 7  # keep last 7 backups

# 📧 Email config
EMAIL_FROM = "skoybrown@gmail.com"
EMAIL_TO = "skoybrown@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
EMAIL_USER = "skoybrown@gmail.com"
EMAIL_PASS = "yybo pbsq gfdc bnnp"  # <-- paste Google App Password here

def send_email(subject, body):
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_FROM
        msg["To"] = EMAIL_TO
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())

        print("📧 Email sent successfully.")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

def main():
    os.makedirs(BACKUP_DIR, exist_ok=True)

    # 📅 Create backup filename
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_filename = f"backup_{timestamp}.tar.gz"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)

    try:
        # 🎁 Create backup
        with tarfile.open(backup_path, "w:gz") as tar:
            tar.add(SOURCE_DIR, arcname=os.path.basename(SOURCE_DIR))

        body = f"✅ Backup successful!\n\nFile: {backup_path}"
        print(body)
        send_email("Backup Report: SUCCESS", body)

        # 🔄 Rotation
        backups = sorted(glob.glob(os.path.join(BACKUP_DIR, "backup_*.tar.gz")))
        if len(backups) > MAX_BACKUPS:
            old_backups = backups[:-MAX_BACKUPS]
            for old in old_backups:
                os.remove(old)
                print(f"🗑️ Deleted old backup: {old}")

    except Exception as e:
        body = f"❌ Backup FAILED!\n\nError: {e}"
        print(body)
        send_email("Backup Report: FAILURE", body)

if __name__ == "__main__":
    main()
