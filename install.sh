#!/bin/bash

# This is the master installation script for setting up a-Shell as a DevOps hub

# Update and install base tools (Node, Python, Git, etc.)
echo "Updating package manager and installing base tools..."
if command -v apk > /dev/null; then
  apk update && apk add git curl nodejs npm python3 py3-pip
else
  echo "a-Shell environment detected. Ensure you have HomeBrew/Core config manually installed."
fi

# Install Configuration Files
echo "Installing configuration files..."
mkdir -p ~/.ssh
mkdir -p ~/.ashell

# Clone necessary scripts (if not already done)
git config --add alias.ci commit
git config --add alias.co checkout

echo "Setup completed! Use this as a starting point for more CI/CD tooling."