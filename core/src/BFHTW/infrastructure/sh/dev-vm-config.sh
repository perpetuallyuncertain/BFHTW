#!/usr/bin/env bash

# GCP VM Config

export PROJECT_ID="fartsicorn"
export ZONE="australia-southeast1-b"
export VM_NAME="fartsicorn-dev"
export MACHINE_TYPE="n2-standard-4"                
export IMAGE_FAMILY="ubuntu-2204-lts"
export IMAGE_PROJECT="ubuntu-os-cloud"
export DISK_SIZE="128GB"
export STARTUP_SCRIPT_PATH="./setup-dev-vm.sh"
export SSH_KEY_FILE="./ssh-keys.txt"
export TAGS="fartsicorn-dev"