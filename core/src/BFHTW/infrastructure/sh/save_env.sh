#!/bin/bash

# Usage:
# source ./save_env.sh --secret_name OPENAI_API --oauth_path /path/to/service-account.json --project_id my-gcp-project

# Only set -e if not sourced
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  set -e
fi

# --- Parse args ---
while [[ "$#" -gt 0 ]]; do
  case $1 in
    --secret_name) SECRET_NAME="$2"; shift ;;
    --oauth_path) OAUTH_PATH="$2"; shift ;;
    --project_id) PROJECT_ID="$2"; shift ;;
    *) echo "[ERROR] Unknown parameter: $1"; return 1 2>/dev/null || exit 1 ;;
  esac
  shift
done

# --- Check required inputs ---
if [[ -z "${SECRET_NAME:-}" || -z "${OAUTH_PATH:-}" || -z "${PROJECT_ID:-}" ]]; then
  echo "[ERROR] Missing required arguments."
  echo "Usage: ./save_env.sh --secret_name SECRET --oauth_path /path/to/key.json --project_id PROJECT"
  return 1 2>/dev/null || exit 1
fi

# --- Resolve full path to credentials ---
if [[ ! -f "$OAUTH_PATH" ]]; then
  echo "[ERROR] Credentials file not found at path: $OAUTH_PATH"
  return 1 2>/dev/null || exit 1
fi

OAUTH_PATH="$(realpath "$OAUTH_PATH")"
export GOOGLE_APPLICATION_CREDENTIALS="$OAUTH_PATH"
echo "[INFO] Using credentials from: $GOOGLE_APPLICATION_CREDENTIALS"

# --- Confirm gcloud is available ---
if ! command -v gcloud &> /dev/null; then
  echo "[ERROR] gcloud CLI not found in PATH"
  return 1 2>/dev/null || exit 1
fi

# --- Authenticate with GCP using service account ---
if ! gcloud auth activate-service-account \
      --key-file="$OAUTH_PATH" \
      --project="$PROJECT_ID" &>/dev/null; then
  echo "[ERROR] Failed to authenticate with GCP using service account"
  return 1 2>/dev/null || exit 1
fi

# --- Get secret value ---
SECRET_VALUE=$(gcloud secrets versions access latest \
  --secret="$SECRET_NAME" \
  --project="$PROJECT_ID" 2>&1)

# --- Check fetch result ---
if [[ $? -ne 0 || -z "$SECRET_VALUE" ]]; then
  echo "[ERROR] Failed to fetch secret '$SECRET_NAME'"
  echo "[DETAILS] $SECRET_VALUE"
  return 1 2>/dev/null || exit 1
fi

# --- Export the secret ---
export ${SECRET_NAME}="${SECRET_VALUE}"
echo "[INFO] Secret loaded: ${SECRET_NAME}=${SECRET_VALUE}"

# --- Set Python Path ---
export PYTHONPATH="/home/steven/BFHTW/core/src/:$PYTHONPATH"
echo "[INFO] PYTHONPATH set to: $PYTHONPATH"
