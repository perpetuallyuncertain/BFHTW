#!/usr/bin/env bash

# destroy-dev-vm.sh - Tear down the GCP dev VM and associated resources

set -eu

# Set the root dir relative to the directory of this script
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." >/dev/null 2>&1 && pwd)"
export ROOT_DIR

INFRA_DIR="${ROOT_DIR}/infrastructure"
export INFRA_DIR

INFRA_SCRIPT_DIR="${INFRA_DIR}/sh"
export INFRA_SCRIPT_DIR

# Load common config for the VM
# shellcheck disable=SC1091
source "${INFRA_SCRIPT_DIR}/dev-vm-config.sh"

echo "Deleting VM ${VM_NAME} in zone ${ZONE}..."

gcloud compute instances delete "${VM_NAME}" \
  --zone="${ZONE}" \
  --quiet

echo "Deleting NIC ${NIC_NAME}..."
gcloud compute networks subnets delete "${SUBNET_NAME}" \
  --region="${REGION}" \
  --quiet || true

gcloud compute networks delete "${VNET_NAME}" \
  --quiet || true

gcloud compute addresses delete "${STATIC_IP_NAME}" \
  --region="${REGION}" \
  --quiet || true

gcloud compute disks delete "${OS_DISK_NAME}" \
  --zone="${ZONE}" \
  --quiet || true

echo "Deleting firewall rules and cleanup (if any)..."
gcloud compute firewall-rules delete "${NSG_NAME}" \
  --quiet || true

echo "VM and associated resources are being removed."
