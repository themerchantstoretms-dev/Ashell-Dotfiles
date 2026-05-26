#!/bin/bash
# a-Shell DevOps Setup Script

echo "🚀 Initializing a-Shell DevOps Environment..."

# 1. Create necessary directories
mkdir -p ~/Documents/projects
mkdir -p ~/Documents/scripts
mkdir -p ~/.ssh

# 2. Write the .profile configuration
cat << 'EOF' > ~/Documents/.profile
# --- Colors ---
BLUE="\[\033[1;34m\]"
WHITE="\[\033[1;37m\]"
GREEN="\[\033[0;32m\]"
RESET="\[\033[0m\]"

# --- Prompt ---
export PS1="${BLUE}☁  gcp ${WHITE}a-shell:${GREEN}\w${WHITE} \$ ${RESET}"

# --- DevOps Aliases ---
alias git="lg2"
alias py="python"
alias ll="ls -la"
alias cls="clear"
alias update-env="curl -sL https://gist.githubusercontent.com/YOUR_GITHUB/YOUR_GIST_ID/raw/setup.sh | bash"

clear
echo -e "${BLUE}☁ Google Cloud Shell (a-Shell DevOps)${RESET}"
echo "Ready."
EOF

echo "✅ .profile configured."
echo "🔄 Please run: source ~/Documents/.profile"