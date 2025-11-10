
#!/bin/bash

set -euo pipefail
 
# --- Variables ---

NEW_USER="osamuel-cnettdevops"

USER_HOME="/home/$NEW_USER"

SSH_DIR="$USER_HOME/.ssh"

PRIVATE_KEY="$SSH_DIR/id_rsa"

PUBLIC_KEY="${PRIVATE_KEY}.pub"

RENAMED_PRIVATE_KEY="$SSH_DIR/${NEW_USER}_rsa"

AUTHORIZED_KEYS="$SSH_DIR/authorized_keys"
 
# --- Create the new user (non-interactive, no password) ---

if id "$NEW_USER" &>/dev/null; then

  echo "User '$NEW_USER' already exists. Skipping creation."

else

  sudo adduser --disabled-password --gecos "" "$NEW_USER"

  echo "User '$NEW_USER' created successfully."

fi
 
# --- Ensure .ssh directory exists ---

sudo mkdir -p "$SSH_DIR"

sudo chmod 700 "$SSH_DIR"

sudo chown "$NEW_USER:$NEW_USER" "$SSH_DIR"
 
# --- Generate SSH key pair if missing ---

if sudo test ! -f "$PRIVATE_KEY"; then

  sudo -u "$NEW_USER" ssh-keygen -t rsa -b 2048 -f "$PRIVATE_KEY" -N "" -q

  echo "SSH key pair generated for $NEW_USER."

else

  echo "SSH key pair already exists for $NEW_USER. Skipping key generation."

fi
 
# --- Rename key files ---

if sudo test -f "$PRIVATE_KEY" && sudo test ! -f "$RENAMED_PRIVATE_KEY"; then

  sudo mv "$PRIVATE_KEY" "$RENAMED_PRIVATE_KEY"

  sudo mv "$PUBLIC_KEY" "${RENAMED_PRIVATE_KEY}.pub"

  echo "Keys renamed to ${NEW_USER}_rsa and ${NEW_USER}_rsa.pub."

fi
 
# --- Copy public key to authorized_keys ---

sudo cp "${RENAMED_PRIVATE_KEY}.pub" "$AUTHORIZED_KEYS"

sudo chmod 600 "$AUTHORIZED_KEYS"

sudo chown "$NEW_USER:$NEW_USER" "$AUTHORIZED_KEYS"

echo "Public key added to authorized_keys for $NEW_USER."
 
# --- Final ownership fix ---

sudo chown -R "$NEW_USER:$NEW_USER" "$SSH_DIR"
 
# --- Output info ---

echo

echo "✅ Setup completed successfully!"

echo "   User: $NEW_USER"

echo "   SSH directory: $SSH_DIR"

echo "   Private key: $RENAMED_PRIVATE_KEY"

echo

 
