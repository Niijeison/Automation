#!/bin/bash

USER="jeinsonnoc"
SUDOERS_FILE="/etc/sudoers.d/$USER"

# Ensure script is run as root
if [[ $EUID -ne 0 ]]; then
    echo "Run as root"
    exit 1
fi

echo "$USER ALL=(ALL) NOPASSWD:ALL" > $SUDOERS_FILE
chmod 440 $SUDOERS_FILE

echo "Passwordless sudo enabled for $USER"
