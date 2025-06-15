# `save_env.sh`

A simple Bash utility to fetch a secret from **Google Secret Manager** using a service account and load it into an **environment variable**.

---

## 📌 Purpose

This script securely retrieves a named secret from Google Cloud and stores it in your local environment for use in CLI tools, development environments, or temporary sessions.

---

## 🚀 Usage

```bash
./save_env.sh --secret_name SECRET_NAME --oauth_path /path/to/service-account.json --project_id GCP_PROJECT_ID

Arguments
Argument	Description
--secret_name	The name of the secret stored in Google Secret Manager
--oauth_path	Path to your service account JSON credentials file
--project_id	Your Google Cloud Project ID

✅ Example
bash
Copy
Edit
./save_env.sh \
  --secret_name OPENAI_API_KEY \
  --oauth_path ~/.gcp/my-service-account.json \
  --project_id my-ai-project
After running, the secret will be available in your shell session as:

bash
Copy
Edit
echo $OPENAI_API_KEY
🔁 Persist in Current Shell
If you want the environment variable to persist in your current terminal session, run:

bash
Copy
Edit
source ./save_env.sh --secret_name ... --oauth_path ... --project_id ...
⚠️ Requirements
gcloud CLI installed and in your PATH

The specified service account must have the role:

roles/secretmanager.secretAccessor

Bash shell (#!/bin/bash)

Secret must already exist in Google Secret Manager

🛠️ Troubleshooting
Verify the secret exists in Secret Manager.

Confirm the service account has access.

Check your project ID and file paths are correct.

Use gcloud auth list to check active credentials if debugging locally.

vbnet
Copy
Edit
