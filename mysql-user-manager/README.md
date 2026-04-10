# MySQL User & Database Manager

A Python CLI tool that manages MySQL users and their databases.

## What it does

| Scenario | Action |
|---|---|
| User **does not exist** | Creates the user with a secure random password, creates a database `<username>_db`, and grants full privileges. Prints credentials once. |
| User **already exists** | Skips user creation, creates the database (if it doesn't exist), and grants privileges. |

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy and edit the environment file
cp .env.example .env
# → fill in your MySQL admin password
```

## Usage

```bash
# Basic — uses env vars / defaults for connection
python manage_user.py myappuser

# Explicit connection details
python manage_user.py myappuser \
  --host 127.0.0.1 \
  --port 3306 \
  --admin-user root \
  --admin-password 'S3cur3P@ss'

# Custom database name
python manage_user.py myappuser --db-name my_custom_db

# Restrict user to localhost only
python manage_user.py myappuser --user-host localhost

# Manage multiple users at once
python manage_users.py user1 user2 user3
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `MYSQL_HOST` | `localhost` | MySQL server hostname |
| `MYSQL_PORT` | `3306` | MySQL server port |
| `MYSQL_ADMIN_USER` | `root` | Admin account used to create users |
| `MYSQL_ADMIN_PASSWORD` | *(required)* | Password for the admin account |
