#!/bin/bash
set -euo pipefail

# --- List of users to create ---
USERS=(
  "osamuel-cnettdevops"
  "jeison-devsecops"
  "david-neteng"
)

for NEW_USER in "${USERS[@]}"; do
  echo "===== Setting up user: $NEW_USER ====="

  USER_HOME="/home/$NEW_USER"
  SSH_DIR="$USER_HOME/.ssh"
  PRIVATE_KEY="$SSH_DIR/id_rsa"
  PUBLIC_KEY="${PRIVATE_KEY}.pub"
  RENAMED_PRIVATE_KEY="$SSH_DIR/${NEW_USER}_rsa"
  AUTHORIZED_KEYS="$SSH_DIR/authorized_keys"

  # --- Create user ---
  if id "$NEW_USER" &>/dev/null; then
    echo "User '$NEW_USER' already exists. Skipping."
  else
    sudo adduser --disabled-password --gecos "" "$NEW_USER"
    echo "User '$NEW_USER' created."
  fi

  # --- Create .ssh folder ---
  sudo mkdir -p "$SSH_DIR"
  sudo chmod 700 "$SSH_DIR"
  sudo chown "$NEW_USER:$NEW_USER" "$SSH_DIR"

  # --- Generate unique SSH keys for this user ---
  if sudo test ! -f "$PRIVATE_KEY"; then
    sudo -u "$NEW_USER" ssh-keygen -t rsa -b 4096 -f "$PRIVATE_KEY" -N "" -q
    echo "SSH keypair created for $NEW_USER."
  else
    echo "SSH key already exists for $NEW_USER."
  fi

  # --- Rename the keys ---
  sudo mv "$PRIVATE_KEY" "$RENAMED_PRIVATE_KEY"
  sudo mv "$PUBLIC_KEY" "${RENAMED_PRIVATE_KEY}.pub"
  echo "Keys renamed to: ${NEW_USER}_rsa and ${NEW_USER}_rsa.pub"

  # --- Add public key to authorized_keys ---
  sudo cp "${RENAMED_PRIVATE_KEY}.pub" "$AUTHORIZED_KEYS"
  sudo chmod 600 "$AUTHORIZED_KEYS"
  sudo chown "$NEW_USER:$NEW_USER" "$AUTHORIZED_KEYS"
  echo "authorized_keys updated for $NEW_USER"

  echo "===== Finished setup for $NEW_USER ====="
  echo
done

echo "🎉 All users created successfully!"
