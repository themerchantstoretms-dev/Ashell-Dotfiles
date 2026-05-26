#!/bin/bash
# Post-create hook for GitHub Codespaces
# Runs after container creation and basic provisioning

set -euo pipefail

echo "🔧 Running post-create setup..."

# Install additional tools
echo "📦 Installing development tools..."
apt-get update
apt-get install -y \
    shellcheck \
    python3-pip \
    bats \
    jq

# Install Python dev dependencies
echo "🐍 Installing Python dependencies..."
pip3 install --user \
    black \
    flake8 \
    pytest

# Setup shell environment
echo "🐚 Configuring shell..."
{
    echo ""
    echo "# Ashell-Dotfiles Development Environment"
    echo "export ASHELL_DEV=true"
    echo "alias shellcheck='shellcheck -x'"
} >> ~/.bashrc

echo "✅ Post-create setup complete!"
