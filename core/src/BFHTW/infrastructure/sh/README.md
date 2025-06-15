# FARTSICORN DEV VM – GCP Setup

This project includes automation scripts to provision, configure, and tear down a GCP-based development VM for the TIQ AI project.

---

## 🚀 Prerequisites

1. **Install the Google Cloud CLI**  
   👉 [Installation guide](https://cloud.google.com/sdk/docs/install)

2. **Authenticate with GCP**
   ```bash
   gcloud auth login
   ```

3. **Set your default GCP project**
   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```

4. **Enable the Compute Engine API (first time only)**
   ```bash
   gcloud services enable compute.googleapis.com
   ```

---

## 📂 Project Structure

```text
infrastructure/
├── sh/
│   ├── create-dev-vm.sh       # One-touch VM provisioning
│   ├── destroy-dev-vm.sh      # Optional: Destroys the VM
│   ├── setup-dev-vm.sh        # Runs on the VM to configure it
│   └── users.json             # List of users and SSH keys to provision
```

---

## 🛠 VM Provisioning

To spin up a dev VM:

```bash
cd infrastructure/sh
./create-dev-vm.sh
```

This will:
- Create the VM with your config
- Attach a static IP
- SSH into the VM and run the setup script (`setup-dev-vm.sh`)
- Configure users and dev packages

You’ll see output like:

```text
🌐 Instance created: tiqai-dev
🔐 You can connect using:
ssh yourname@34.82.101.22
```

---

## 🔧 What the Setup Script Does

Once the VM is running, the `setup-dev-vm.sh` script will:

- Apply system updates
- Install dev packages (Python, Docker, SQLite, etc.)
- Add user accounts from `users.json`
- Harden SSH access (no root login, key-only auth)
- Enable unattended upgrades and fail2ban

---

## 🧨 Tear Down the VM (Optional)

If you want to destroy the VM and associated resources:

```bash
./destroy-dev-vm.sh
```

> This script is optional. If not present, you can destroy manually:
```bash
gcloud compute instances delete tiqai-dev --zone=australia-southeast1-b
```

---

## 📝 Customizing Your Setup

- Update package installs in `setup-dev-vm.sh`
- Add or modify users in `users.json`
- Edit VM config (name, zone, machine type) directly in `create-dev-vm.sh`
