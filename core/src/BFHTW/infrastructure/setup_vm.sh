#!/bin/bash

set -e  # Exit on any error
set -u  # Treat unset variables as errors

echo "Updating package list..."
sudo apt update -y

echo "Upgrading installed packages..."
sudo apt upgrade -y

echo "Installing essential packages..."
sudo apt install -y \
    curl \
    wget \
    unzip \
    git \
    jq \
    ca-certificates \
    gnupg \
    lsb-release \
    software-properties-common

echo "Ensuring Docker is available in WSL..."
if ! command -v docker &> /dev/null; then
    echo "Docker not found. Please install Docker Desktop and enable WSL integration."
    exit 1
fi

echo "Checking Docker service..."
if ! docker info &> /dev/null; then
    echo "Docker is installed but not running or not connected to WSL."
    echo "Please ensure Docker Desktop is open and WSL integration is enabled for your distro."
    exit 1
fi

echo "Docker is running!"

echo "🧹 Cleaning up package cache..."
sudo apt autoremove -y
sudo apt clean

echo "Environment setup complete!"
