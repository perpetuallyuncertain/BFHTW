#!/usr/bin/env bash

# create-dev-vm.sh - Spin up a dev VM on GCP

set -eu

# Load shared configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/dev-vm-config.sh"

echo "Creating VM instance..."

gcloud compute instances create "${VM_NAME}" \
  --project="${PROJECT_ID}" \
  --zone="${ZONE}" \
  --machine-type="${MACHINE_TYPE}" \
  --image-family="${IMAGE_FAMILY}" \
  --image-project="${IMAGE_PROJECT}" \
  --boot-disk-size="${DISK_SIZE}" \
  --boot-disk-type="pd-ssd" \
  --tags="${TAGS}" \
  --metadata=startup-script="$(< ${STARTUP_SCRIPT_PATH})" \
  --metadata-from-file ssh-keys="${SSH_KEY_FILE}"

echo "Fetching external IP address..."

IP_ADDRESS=$(gcloud compute instances describe "${VM_NAME}" \
  --zone="${ZONE}" \
  --format='get(networkInterfaces[0].accessConfigs[0].natIP)')

echo "Instance created: ${VM_NAME}"
echo "You can connect using:"
echo "ssh ${USER}@${IP_ADDRESS}"
