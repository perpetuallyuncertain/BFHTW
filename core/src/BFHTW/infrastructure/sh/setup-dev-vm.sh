#!/bin/bash

#
# This script is intended to be run on the GCP VM
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

################################################################################
echo "Updating system..."
sudo apt update && sudo apt full-upgrade -y

################################################################################
echo "Enabling automatic security updates..."
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -f noninteractive --priority=low unattended-upgrades

################################################################################
echo "Installing final dev dependencies..."
sudo apt install -y \
  ca-certificates \
  curl \
  build-essential \
  fail2ban \
  git \
  git-lfs \
  gnupg2 \
  htop \
  jq \
  libffi-dev \
  libssl-dev \
  python3 \
  python3-venv \
  python3-pip \
  sqlite3 \
  tree \
  unzip \
  vim \
  docker.io \
  net-tools \
  ufw \
  tmux \
  wget

echo "Installing yq manually..."
sudo wget https://github.com/mikefarah/yq/releases/download/v4.43.1/yq_linux_amd64 -O /usr/local/bin/yq
sudo chmod +x /usr/local/bin/yq

###############################################################################
echo "Enabling and starting Docker..."
sudo systemctl enable docker
sudo systemctl start docker

################################################################################
echo "Adding user to docker group..."
sudo usermod -aG docker "$USER"
echo "You may need to log out and back in (or run 'newgrp docker') to activate Docker group permissions."

echo "Configuring git..."
git config --global core.autocrlf false
git config --global core.eol lf

################################################################################
echo "Adding users from users.json..."
if [[ ! -f ${SCRIPT_DIR}/users.json ]]; then
    echo "${SCRIPT_DIR}/users.json not found. Skipping user creation."
else
    jq -c '.[]' ${SCRIPT_DIR}/users.json | while read -r ROW; do
        USERNAME=$(echo "${ROW}" | jq -r '.username')
        echo "Creating or updating user: ${USERNAME}"

        if ! id "${USERNAME}" &>/dev/null; then
            sudo adduser --disabled-password --gecos "" "${USERNAME}"
            sudo usermod -aG sudo "${USERNAME}"
        fi

        SSH_DIR="/home/${USERNAME}/.ssh"
        AUTH_KEYS="${SSH_DIR}/authorized_keys"
        sudo mkdir -p "${SSH_DIR}"
        sudo touch "${AUTH_KEYS}"
        sudo chown -R "${USERNAME}:${USERNAME}" "${SSH_DIR}"
        sudo chmod 700 "${SSH_DIR}"
        sudo chmod 600 "${AUTH_KEYS}"

        echo "${ROW}" | jq -r '.public_keys[]' | while IFS= read -r KEY; do
            echo "Adding Key: '${KEY}'"
            if ! sudo grep -qF "${KEY}" "${AUTH_KEYS}"; then
                echo "    Adding key for ${USERNAME}"
                echo "${KEY}" | sudo tee -a "${AUTH_KEYS}" > /dev/null
            else
                echo "    Key already present for ${USERNAME}"
            fi
        done
    done
fi

################################################################################
echo "Hardening SSH configuration..."
sudo sed -i 's/^PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sudo sed -i 's/^#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo systemctl restart ssh.service

################################################################################
echo "Enabling fail2ban..."
sudo systemctl enable fail2ban --now

################################################################################
echo "Deploying environment variables"

if [[ ! -f "${SCRIPT_DIR}/save_env.sh" ]]; then
    echo "${SCRIPT_DIR}/save_env.sh not found. Skipping environment deployment."
else
    sudo "${SCRIPT_DIR}/save_env.sh"
    echo "Environment variables saved"
fi

################################################################################

echo "VM Setup Complete"

echo "Rebooting to finalize setup..."
sleep 5
sudo reboot
