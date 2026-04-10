"""
MySQL Multiple Users & Database Manager
========================================
This script connects to a MySQL Server and performs the following for multiple users:
  1. Creates new MySQL users with generated credentials.
  2. If a user already exists, creates a dedicated database for that user
     and grants full privileges on it.

Usage:
    python manage_users.py <username1> <username2> ... [--host HOST] [--port PORT]

Environment variables (or .env file):
    MYSQL_HOST           - MySQL server host       (default: localhost)
    MYSQL_PORT           - MySQL server port        (default: 3306)
    MYSQL_ADMIN_USER     - Admin/root username      (default: root)
    MYSQL_ADMIN_PASSWORD - Admin/root password      (required)
"""

import argparse
import os
import secrets
import string
import sys

import mysql.connector
from mysql.connector import Error


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def generate_password(length: int = 20) -> str:
    """Generate a secure random password."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    password = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.digits),
        secrets.choice("!@#$%^&*()-_=+"),
    ]
    password += [secrets.choice(alphabet) for _ in range(length - len(password))]
    password_list = list(password)
    secrets.SystemRandom().shuffle(password_list)
    return "".join(password_list)


def get_admin_connection(host: str, port: int, user: str, password: str):
    """Return a connection to the MySQL server using admin credentials."""
    try:
        conn = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
        )
        if conn.is_connected():
            print(f"✅  Connected to MySQL server at {host}:{port}")
            return conn
    except Error as e:
        print(f"❌  Failed to connect to MySQL: {e}")
        sys.exit(1)


def user_exists(cursor, username: str) -> bool:
    """Check whether a MySQL user account already exists."""
    cursor.execute(
        "SELECT COUNT(*) FROM mysql.user WHERE User = %s",
        (username,),
    )
    (count,) = cursor.fetchone()
    return count > 0


def create_user(cursor, username: str, password: str, host: str = "%") -> None:
    """Create a new MySQL user with the given password."""
    cursor.execute(
        f"CREATE USER %s@%s IDENTIFIED BY %s",
        (username, host, password),
    )
    print(f"✅  User '{username}'@'{host}' created successfully.")


def create_database_for_user(cursor, username: str, db_name: str, host: str = "%") -> None:
    """Create a database and grant the user full privileges on it."""
    safe_db = db_name.replace("`", "``")
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{safe_db}`")
    cursor.execute(
        f"GRANT ALL PRIVILEGES ON `{safe_db}`.* TO %s@%s",
        (username, host),
    )
    cursor.execute("FLUSH PRIVILEGES")
    print(f"✅  Database '{db_name}' created and privileges granted to '{username}'@'{host}'.")


# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create multiple MySQL users and/or their dedicated databases."
    )
    parser.add_argument(
        "usernames",
        nargs="+",
        help="One or more MySQL usernames to create or manage.",
    )
    parser.add_argument(
        "--host",
        default=os.getenv("MYSQL_HOST", "localhost"),
        help="MySQL server host (default: $MYSQL_HOST or localhost).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("MYSQL_PORT", "3306")),
        help="MySQL server port (default: $MYSQL_PORT or 3306).",
    )
    parser.add_argument(
        "--admin-user",
        default=os.getenv("MYSQL_ADMIN_USER", "root"),
        help="Admin user for the MySQL server (default: $MYSQL_ADMIN_USER or root).",
    )
    parser.add_argument(
        "--admin-password",
        default=os.getenv("MYSQL_ADMIN_PASSWORD"),
        help="Admin password (default: $MYSQL_ADMIN_PASSWORD).",
    )
    parser.add_argument(
        "--user-host",
        default="%",
        help="Host part of the new user accounts (default: '%%' = any host).",
    )

    args = parser.parse_args()

    if not args.admin_password:
        print("❌  Admin password is required. Set MYSQL_ADMIN_PASSWORD or use --admin-password.")
        sys.exit(1)

    # ---- Connect as admin ----
    conn = get_admin_connection(args.host, args.port, args.admin_user, args.admin_password)
    cursor = conn.cursor()

    try:
        credentials = []
        for username in args.usernames:
            print(f"\n--- Processing user: {username} ---")
            db_name = f"{username}_db"
            
            if user_exists(cursor, username):
                # ---- User already exists → create a database for them ----
                print(f"ℹ️   User '{username}' already exists.")
                create_database_for_user(cursor, username, db_name, args.user_host)
            else:
                # ---- Create user with fresh credentials ----
                password = generate_password()
                create_user(cursor, username, password, args.user_host)

                # ---- Create a dedicated database and grant access ----
                create_database_for_user(cursor, username, db_name, args.user_host)

                # Keep track of credentials to print at the end
                credentials.append({
                    "username": username,
                    "password": password,
                    "host": args.user_host,
                    "database": db_name
                })

        conn.commit()
        
        # ---- Print credentials for all new users ----
        if credentials:
            print("\n" + "=" * 50)
            print("   NEW USER CREDENTIALS")
            print("=" * 50)
            for cred in credentials:
                print(f"   Username : {cred['username']}")
                print(f"   Password : {cred['password']}")
                print(f"   Host     : {cred['host']}")
                print(f"   Database : {cred['database']}")
                print("-" * 50)
            print("⚠️   Save these credentials securely — the passwords")
            print("    will NOT be shown again.")
            print("=" * 50 + "\n")

        print("🎉  Done!")

    except Error as e:
        conn.rollback()
        print(f"❌  MySQL error: {e}")
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()
        print("🔌  Connection closed.")


if __name__ == "__main__":
    main()
