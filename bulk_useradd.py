#!/usr/bin/env python3
import csv
import subprocess
import re
import logging

CSV_FILE = "/home/jeison/Buerkie/nii/users.csv"

# Configure logging
logging.basicConfig(filename='user_creation.log', level=logging.INFO, format='%(asctime)s - %(message)s')

def is_valid_input(value):
    """Check if input contains only valid characters."""
    return bool(re.match(r'^[a-zA-Z0-9_-]+$', value))

def user_exists(username):
    """Check if a user already exists."""
    result = subprocess.run(["getent", "passwd", username], capture_output=True, text=True)
    return result.returncode == 0

def create_user(username, password, group):
    """Create a user and add to group."""
    try:
        if not all(is_valid_input(x) for x in [username, group]):
            logging.error(f"Invalid username or group: {username}, {group}")
            print(f"[!] Invalid username or group for {username}")
            return

        if user_exists(username):
            logging.info(f"User '{username}' already exists, skipping")
            print(f"[!] User '{username}' already exists, skipping")
            return

        # Create group if it doesn't exist
        subprocess.run(["sudo", "groupadd", "-f", group], check=True)

        # Create user and add to group
        subprocess.run(["sudo", "useradd", "-m", "-s", "/bin/bash", "-g", group, username], check=True)

        # Set password
        subprocess.run(["sudo", "chpasswd"], input=f"{username}:{password}".encode(), check=True)

        logging.info(f"User '{username}' created and added to group '{group}'")
        print(f"[+] User '{username}' created and added to group '{group}'")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to create {username}: {e}")
        print(f"[!] Failed to create {username}: {e}")

def main():
    try:
        with open(CSV_FILE, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            if not all(header in reader.fieldnames for header in ['username', 'password', 'group']):
                raise ValueError("CSV file must contain 'username', 'password', and 'group' columns")
            for row in reader:
                create_user(row['username'], row['password'], row['group'])
    except FileNotFoundError:
        logging.error(f"CSV file not found: {CSV_FILE}")
        print(f"[!] CSV file not found: {CSV_FILE}")
    except PermissionError:
        logging.error("Permission denied: Ensure script is run with sufficient privileges")
        print("[!] Permission denied: Ensure script is run with sufficient privileges")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print(f"[!] Unexpected error: {e}")

if __name__ == "__main__":
    main()
