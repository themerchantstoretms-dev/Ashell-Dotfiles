#!/bin/bash

# This is the master installation script for setting up a-Shell as a DevOps hub
# Incorporates interactive tools and GitHub-like functionality

echo "Starting setup for a-Shell..."

# Update and install base tools
echo "Installing base tools (Node.js, Python, Git, etc.)..."
if command -v apk > /dev/null; then
  apk update && apk add git curl nodejs npm python3 py3-pip
else
  echo "a-Shell environment detected. Installing additional tools..."
fi

# Install fzf for fuzzy finding
echo "Installing fzf for interactive menus..."
brew install fzf || pip install fzf

# Install zoxide for quick navigation
echo "Installing zoxide for efficient directory navigation..."
brew install zoxide || pip install zoxide

# Install peco as alternative to fzf
echo "Installing peco (interactive filtering)..."
brew install peco || pip install peco

# Install useful CLI libraries
echo "Installing dialog for interactive CLI menus..."
brew install dialog || pip install dialog

# Create initial interactive GitHub menu
echo "Creating GitHub-like palette for navigational ease..."
mkdir -p ~/.ashell
cat <<EOF >~/.ashell/menu.sh
#!/bin/bash

echo "Choose an action:"
echo "1. Open Repository\n2. List Issues\n3. Create Pull Request\n4. Commit Changes"
read -p "Enter your choice: " choice

case $choice in
  1) echo "Opening Repository" ;;
  2) echo "Listing Issues" ;;
  3) echo "Creating Pull Request" ;;
  4) echo "Committing Changes" ;;
  *) echo "Invalid Choice" ;;
esac
EOF
chmod +x ~/.ashell/menu.sh

# Enable command palette trigger 'fuzzy menus'
echo "Configuring command palette trigger (/)..."
echo 'alias /="bash ~/.ashell/menu.sh"' >> ~/.zshrc
source ~/.zshrc

echo "Setup complete! Relaunch a-Shell to apply changes. Use '/' for command palette."