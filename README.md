# Ashell-Dotfiles

**Production-grade dotfiles and DevOps automation for a-Shell on iOS.**

A comprehensive, tested, and maintainable setup for configuring a-Shell as a functional DevOps environment on iPad and iPhone, with support for Git, Node.js, Python, and essential CLI tools.

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [iOS Constraints & Workarounds](#ios-constraints--workarounds)
- [Contributing](#contributing)
- [License](#license)

---

## Features

✅ **Cross-platform package manager detection** (apk, apt, brew, yum, dnf)
✅ **Multi-shell support** (bash, zsh, fish) with auto-detection
✅ **Idempotent installation** (safe to run multiple times)
✅ **Comprehensive error handling** with recovery paths
✅ **Dry-run mode** for safe preview before execution
✅ **Configuration backups** before any modifications
✅ **Verified installations** with post-install checks
✅ **Color-coded logging** with verbose/debug modes
✅ **iOS a-Shell optimized** (respects sandbox constraints)
✅ **Production-grade shell scripting** (ShellCheck validated)

---

## Architecture

```
ashell-dotfiles/
├── install.sh              # Main bootstrap script (production-grade)
├── setup.sh                # a-Shell environment initialization
├── README.md               # This file
├── .shellcheckrc           # ShellCheck configuration
└── tests/
    ├── install.sh.test     # Test suite for install.sh
    └── setup.sh.test       # Test suite for setup.sh
```

### Design Principles

1. **Deterministic State**: Scripts idempotently reach target state regardless of re-runs
2. **Explicit Error Handling**: No silent failures; all errors surface immediately
3. **iOS Compatibility**: Respects a-Shell sandbox restrictions (no background jobs, no network daemon)
4. **Production Safety**: Backups created before modifications; recovery paths documented
5. **Maintainability**: Strict typing, clear variable names, comprehensive logging

---

## Requirements

### a-Shell (iOS)
- **a-Shell** v1.14+ from [App Store](https://apps.apple.com/us/app/a-shell/id1473805438)
- iOS 14.0 or later
- ~100MB free storage

### Linux/macOS
- **Bash** 4.0+
- **Git** 2.0+
- One of: apk (Alpine), apt (Debian/Ubuntu), brew (macOS), yum (RHEL), dnf (Fedora)

---

## Installation

### Quick Start

```bash
# Download and execute bootstrap script
curl -fsSL https://raw.githubusercontent.com/themerchantstoretms-dev/Ashell-Dotfiles/main/install.sh | bash
```

### Explicit Download & Verification

```bash
# Clone or download repository
git clone https://github.com/themerchantstoretms-dev/Ashell-Dotfiles.git
cd Ashell-Dotfiles

# View what will be installed (dry-run mode)
./install.sh --dry-run --verbose

# Execute installation
./install.sh --verbose

# Reload shell configuration
source ~/.bashrc   # for bash
source ~/.zshrc    # for zsh
source ~/.config/fish/config.fish  # for fish
```

### Installation Options

```bash
./install.sh [OPTIONS]

OPTIONS:
  --dry-run          Preview changes without modifying filesystem
  --verbose, -v      Show detailed execution logs
  --shell=SHELL      Target shell (bash, zsh, fish). Auto-detected by default.
  --help, -h         Display usage information
```

### What Gets Installed

| Tool | Purpose | Package Manager |
|------|---------|-----------------|
| **git** | Version control | apk/apt/brew/yum/dnf |
| **curl** | HTTP client | apk/apt/brew/yum/dnf |
| **python3** | Python runtime | apk/apt/brew/yum/dnf |
| **nodejs** | Node.js runtime | apk/apt/brew/yum/dnf |
| **fzf** | Fuzzy finder (interactive menus) | apk/apt/brew/yum/dnf |
| **zoxide** | Quick directory navigation | apk/apt/brew/yum/dnf |
| **peco** | Interactive filtering tool | apk/apt/brew/yum/dnf |
| **dialog** | CLI dialog menus | apk/apt/brew/yum/dnf |

### Configuration Created

| Path | Purpose | Can Modify |
|------|---------|-----------|
| `~/.ashell/menu.sh` | Interactive command palette | Yes (will not overwrite) |
| `~/.ashell/helpers.sh` | DevOps helper functions | Yes (will not overwrite) |
| `~/.bashrc` / `~/.zshrc` / `~/.config/fish/config.fish` | Shell aliases and sourcing | Yes (backup created first) |

---

## Usage

### Command Palette

After installation, the `/` command triggers the interactive menu:

```bash
/
```

Output:
```
===================================
   a-Shell DevOps Hub Menu
===================================

Choose an action:
  1) Open Repository
  2) List Issues
  3) Create Pull Request
  4) Commit Changes
  5) Exit

Enter your choice (1-5):
```

### Helper Functions

Available in all shells via `~/.ashell/helpers.sh`:

```bash
# Open a repository
ashell_open_repo <repo-url-or-path>

# List issues (placeholder for future implementation)
ashell_list_issues

# Create pull request (placeholder for future implementation)
ashell_create_pr
```

### Examples

```bash
# Navigate quickly
z my_project  # via zoxide

# Find files interactively
fzf

# Check Git status with enhanced view
git status

# Run the DevOps menu
/

# Source custom helpers
source ~/.ashell/helpers.sh
ashell_open_repo ~/my-repo
```

---

## Configuration

### Shell-Specific Configuration

**For Bash** (`~/.bashrc`):
```bash
# a-Shell DevOps Hub Configuration
alias /='bash ~/.ashell/menu.sh'
source ~/.ashell/helpers.sh
```

**For Zsh** (`~/.zshrc`):
```bash
# a-Shell DevOps Hub Configuration
alias /='bash ~/.ashell/menu.sh'
source ~/.ashell/helpers.sh
```

**For Fish** (`~/.config/fish/config.fish`):
```fish
# a-Shell DevOps Hub Configuration
alias / 'bash ~/.ashell/menu.sh'
source ~/.ashell/helpers.sh
```

### Customization

Edit `~/.ashell/menu.sh` to add custom menu options:

```bash
#!/bin/bash

echo "==================================="
echo "   a-Shell DevOps Hub Menu"
echo "==================================="
echo ""
echo "Choose an action:"
echo "  1) Open Repository"
echo "  2) List Issues"
echo "  6) Custom Action"  # Add your custom option
echo ""
read -p "Enter your choice: " choice

case $choice in
  1) echo "Opening Repository..." ;;
  2) echo "Listing Issues..." ;;
  6) your_custom_function ;;  # Call your function
  *) echo "Invalid choice." ; exit 1 ;;
esac
```

Edit `~/.ashell/helpers.sh` to add custom functions:

```bash
#!/bin/bash

# Your custom DevOps functions
my_custom_command() {
  echo "Executing custom command..."
  # Your logic here
}
```

---

## Troubleshooting

### Installation Fails on Package Installation

**Problem:** One or more packages fail to install.

**Solution:**
```bash
# Run with verbose output to see exact error
./install.sh --verbose

# Try manual installation for specific package
# Example for brew on macOS:
brew install <package-name>

# Non-critical packages (fzf, zoxide, peco, dialog) can be skipped
# The script will continue even if these fail
```

### Shell Configuration Not Applied

**Problem:** Changes to `~/.bashrc`, `~/.zshrc`, or `~/.config/fish/config.fish` not taking effect.

**Solution:**
```bash
# Reload shell configuration
source ~/.bashrc   # for bash
source ~/.zshrc    # for zsh
source ~/.config/fish/config.fish  # for fish

# Or restart the shell entirely
bash    # or zsh, or fish
```

### Menu Command (/) Not Working

**Problem:** `/` command returns "command not found"

**Solution:**
```bash
# Verify alias was created
alias | grep "^alias /="

# If missing, source the shell config manually
source ~/.bashrc   # or ~/.zshrc for zsh

# If still missing, verify menu.sh exists
ls -la ~/.ashell/menu.sh

# If missing, re-run install script
./install.sh
```

### Package Manager Not Detected

**Problem:** "No supported package manager found"

**Solution:**
```bash
# Install your system's package manager first, then re-run
# Examples:
# - Alpine: apk (should already exist)
# - Debian/Ubuntu: apt-get
# - macOS: brew (install from https://brew.sh)
# - RHEL/CentOS: yum or dnf

# After installing PM, re-run:
./install.sh --verbose
```

### Dry-Run Shows Errors

**Problem:** `--dry-run` displays error messages but makes no changes.

**Solution:**
```bash
# This is expected behavior—dry-run validates without modifying
# Review the output for issues, then run without --dry-run
./install.sh --verbose

# Check backups if needed
ls -la ~/.dotfiles_backup.*
```

### On iOS a-Shell Specifically

**Problem:** `dialog` or `peco` not available in a-Shell iOS.

**Solution:**
```bash
# a-Shell iOS has limited tool availability
# These packages may not install on iOS
# The install script will skip them with a warning (non-critical)
# Functionality will still work with standard tools (fzf, zoxide, etc.)
```

---

## iOS Constraints & Workarounds

### a-Shell iOS Sandboxing

a-Shell runs within iOS app sandbox with specific constraints:

| Constraint | Impact | Workaround |
|-----------|--------|-----------|
| No persistent background jobs | Can't run daemons (Redis, nginx, etc.) | Use cloud services or macOS/Linux for servers |
| Network restricted by iOS | Limited outbound connections | Use SSH for remote access; rely on curl/wget for APIs |
| No file watching (inotify) | Can't watch directories for changes | Manual triggers or cloud-based file sync |
| Processes terminate on app close | Long jobs interrupted | Keep app active or use remote execution |
| Limited system access | Can't modify OS-level configs | Configure within a-Shell sandbox only |

### Recommended iOS Workflows

1. **Code Review & Git Operations**
   ```bash
   git clone <repo>
   git checkout -b feature/my-feature
   git status
   git add .
   git commit -m "message"
   git push origin feature/my-feature
   ```

2. **Remote Server Management**
   ```bash
   # SSH into remote servers
   ssh user@remote-host
   
   # Copy files
   scp local-file user@remote-host:/path/
   
   # Monitor logs
   ssh user@remote-host "tail -f /var/log/app.log"
   ```

3. **Script Development & Testing**
   ```bash
   # Write and test scripts locally
   nano my-script.sh
   chmod +x my-script.sh
   ./my-script.sh
   
   # Push to git when ready
   git add my-script.sh
   git commit -m "Add my-script"
   git push
   ```

4. **Quick API Testing**
   ```bash
   curl -X GET https://api.example.com/endpoint
   curl -X POST -d '{"key":"value"}' https://api.example.com/endpoint
   
   # With jq for JSON parsing
   curl https://api.example.com/data | jq '.results[]'
   ```

---

## Contributing

We welcome contributions! Follow these guidelines:

### Before Submitting

1. **Run ShellCheck validation:**
   ```bash
   shellcheck install.sh setup.sh
   ```

2. **Run test suite:**
   ```bash
   bats tests/install.sh.test
   bats tests/setup.sh.test
   ```

3. **Test on your platform:**
   ```bash
   ./install.sh --dry-run --verbose
   ./install.sh --verbose
   source ~/.bashrc  # or ~/.zshrc
   /  # Test menu works
   ```

### Submission Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make changes and test thoroughly
4. Commit with clear messages: `git commit -m "feat: Add X functionality"`
5. Push to your fork: `git push origin feature/my-feature`
6. Open a Pull Request with description of changes

### Code Standards

- **Bash:** ShellCheck clean, `set -euo pipefail`, quoted variables
- **Functions:** Documented with purpose, arguments, return values
- **Variables:** Explicit names, no abbreviations except obvious (i, n in loops)
- **Logging:** Use `log_info()`, `log_warn()`, `log_error()` functions
- **Comments:** Explain "why," not "what" (code is self-documenting)

---

## Testing

### Manual Testing

```bash
# Dry-run mode (no changes)
./install.sh --dry-run --verbose

# Install with verbose output
./install.sh --verbose

# Test after installation
/ # Should show menu
fzf # Should work
zoxide # Should work
```

### Automated Testing (When Available)

```bash
# Run test suite
bats tests/*.test

# Run ShellCheck
shellcheck install.sh setup.sh
```

---

## Recovery & Uninstallation

### Restore Backed-Up Configuration

After installation, a timestamped backup is created:

```bash
# List available backups
ls -la ~/.dotfiles_backup.*

# Restore specific backup
cp ~/.dotfiles_backup.1234567890/.bashrc ~/.bashrc
cp ~/.dotfiles_backup.1234567890/.zshrc ~/.zshrc

# Reload shell
source ~/.bashrc
```

### Remove a-Shell Configuration (Manual Uninstall)

```bash
# Remove menu and helpers
rm -rf ~/.ashell

# Remove aliases and sourcing from shell RC files
# Edit ~/.bashrc, ~/.zshrc, or ~/.config/fish/config.fish
# Remove lines:
#   alias /='bash ~/.ashell/menu.sh'
#   source ~/.ashell/helpers.sh

# Reload shell
source ~/.bashrc
```

---

## FAQ

**Q: Can I run servers (Redis, PostgreSQL, etc.) in a-Shell?**
A: No. iOS app sandbox prevents long-lived background processes. Use cloud services (Redis Cloud, AWS RDS, etc.) or run servers on a separate Linux/macOS machine.

**Q: Can I schedule cron jobs in a-Shell?**
A: Not persistently. a-Shell runs only while the app is active. Use GitHub Actions, cloud schedulers, or a separate Linux server for scheduled tasks.

**Q: Is my data secure in a-Shell?**
A: a-Shell runs in iOS app sandbox, so your data is isolated from other apps. But the app itself is not open-source for the iOS version, so assume reasonable but not absolute security. Don't store highly sensitive credentials; use environment variables instead.

**Q: How do I access my code from other devices?**
A: Use Git (GitHub, GitLab, etc.) to sync code. Use iCloud Drive, Dropbox, or OneDrive for files. Use SSH to connect to remote servers for direct file transfer.

**Q: Can I edit files in a-Shell and sync to my Mac/PC?**
A: Yes. Use Git for code, or use cloud storage (iCloud Drive, Dropbox) for file syncing.

---

## Resources

- **a-Shell GitHub:** https://github.com/holzschu/a-shell
- **a-Shell Documentation:** https://github.com/holzschu/a-shell/wiki
- **ShellCheck:** https://www.shellcheck.net/
- **Bash Best Practices:** https://www.projectrules.ai/rules/bash
- **Git Documentation:** https://git-scm.com/doc

---

## License

This repository is provided as-is for educational and development purposes.

---

## Support

For issues, questions, or feature requests:

1. **Check Troubleshooting section** above
2. **Review existing GitHub Issues:** https://github.com/themerchantstoretms-dev/Ashell-Dotfiles/issues
3. **Open a new issue** with:
   - Your system (a-Shell iOS / Linux / macOS)
   - Output from `./install.sh --verbose`
   - Steps to reproduce
   - Expected vs. actual behavior

---

**Last Updated:** 2026-05-26
**Maintainer:** themerchantstoretms-dev
