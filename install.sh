#!/bin/bash
##############################################################################
# a-Shell DevOps Hub Installation Script
# Supports: Alpine (apk), macOS (brew), Debian/Ubuntu (apt), RHEL (yum/dnf)
# Usage: ./install.sh [--dry-run] [--verbose] [--shell=bash|zsh|fish]
##############################################################################

set -euo pipefail

# ============================================================================
# Configuration & Globals
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ASHELL_HOME="${HOME}/.ashell"
DRY_RUN=false
VERBOSE=false
TARGET_SHELL="${SHELL##*/}"
BACKUP_DIR="${HOME}/.dotfiles_backup.$(date +%s)"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ============================================================================
# Logging Functions
# ============================================================================

log_info() {
  echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
  echo -e "${GREEN}[✓]${NC} $*"
}

log_warn() {
  echo -e "${YELLOW}[WARN]${NC} $*" >&2
}

log_error() {
  echo -e "${RED}[ERROR]${NC} $*" >&2
}

debug() {
  if [[ "$VERBOSE" == true ]]; then
    echo -e "${BLUE}[DEBUG]${NC} $*" >&2
  fi
}

# ============================================================================
# Help & Usage
# ============================================================================

usage() {
  cat <<EOF
USAGE: $(basename "$0") [OPTIONS]

OPTIONS:
  --dry-run         Show what would be installed without making changes
  --verbose, -v     Enable verbose output
  --shell=SHELL     Target shell (bash, zsh, fish). Default: $TARGET_SHELL
  --help, -h        Show this help message

EXAMPLE:
  $(basename "$0") --dry-run --verbose
  $(basename "$0") --shell=zsh

EOF
}

# ============================================================================
# Argument Parsing
# ============================================================================

parse_args() {
  while [[ $# -gt 0 ]]; do
    case $1 in
      --dry-run)
        DRY_RUN=true
        shift
        ;;
      --verbose|-v)
        VERBOSE=true
        shift
        ;;
      --shell=*)
        TARGET_SHELL="${1#*=}"
        shift
        ;;
      --help|-h)
        usage
        exit 0
        ;;
      *)
        log_error "Unknown option: $1"
        usage
        exit 1
        ;;
    esac
  done
}

# ============================================================================
# Pre-flight Checks
# ============================================================================

check_prerequisites() {
  log_info "Performing pre-flight checks..."
  
  if [[ $EUID -eq 0 ]]; then
    log_warn "Running as root. Some operations may not work as expected."
  fi
  
  if ! command -v bash &>/dev/null; then
    log_error "bash is not installed. This script requires bash."
    exit 1
  fi
  
  log_success "Pre-flight checks passed"
}

# ============================================================================
# Package Manager Detection & Installation
# ============================================================================

detect_package_manager() {
  debug "Detecting package manager..."
  
  if command -v apk &>/dev/null; then
    PM="apk"
    PM_INSTALL=("apk" "add")
    PM_UPDATE=("apk" "update")
  elif command -v apt-get &>/dev/null; then
    PM="apt"
    PM_INSTALL=("sudo" "apt-get" "install" "-y")
    PM_UPDATE=("sudo" "apt-get" "update")
  elif command -v brew &>/dev/null; then
    PM="brew"
    PM_INSTALL=("brew" "install")
    PM_UPDATE=("brew" "update")
  elif command -v yum &>/dev/null; then
    PM="yum"
    PM_INSTALL=("sudo" "yum" "install" "-y")
    PM_UPDATE=("sudo" "yum" "update")
  elif command -v dnf &>/dev/null; then
    PM="dnf"
    PM_INSTALL=("sudo" "dnf" "install" "-y")
    PM_UPDATE=("sudo" "dnf" "update")
  else
    log_error "No supported package manager found (apk, apt, brew, yum, dnf)"
    exit 1
  fi
  
  log_success "Detected package manager: $PM"
}

run_cmd() {
  if [[ "$DRY_RUN" == true ]]; then
    log_info "[DRY-RUN] Would execute: $*"
  else
    debug "Executing: $*"
    "$@" || return $?
  fi
}

install_package() {
  local package=$1
  
  if command -v "$package" &>/dev/null; then
    log_warn "Package '$package' already installed, skipping"
    return 0
  fi
  
  log_info "Installing $package..."
  run_cmd "${PM_INSTALL[@]}" "$package" || {
    log_error "Failed to install $package"
    return 1
  }
  
  if command -v "$package" &>/dev/null; then
    log_success "Successfully installed $package"
  else
    log_error "Verification failed: $package not found after installation"
    return 1
  fi
}

# ============================================================================
# Main Installation Logic
# ============================================================================

backup_configs() {
  log_info "Creating backup of existing configurations..."
  mkdir -p "$BACKUP_DIR"
  
  for config in .zshrc .bashrc .fish/config.fish; do
    if [[ -f "${HOME}/${config}" ]]; then
      run_cmd cp "${HOME}/${config}" "${BACKUP_DIR}/${config##*/}"
      log_success "Backed up ${config} → ${BACKUP_DIR}/${config##*/}"
    fi
  done
}

install_base_tools() {
  log_info "Installing base tools..."
  
  local tools=(git curl python3 nodejs)
  
  for tool in "${tools[@]}"; do
    install_package "$tool" || log_warn "Non-critical: Failed to install $tool"
  done
}

install_dev_tools() {
  log_info "Installing development tools..."
  
  local tools=(fzf zoxide peco dialog)
  local failed=()
  
  for tool in "${tools[@]}"; do
    if ! install_package "$tool"; then
      failed+=("$tool")
    fi
  done
  
  if [[ ${#failed[@]} -gt 0 ]]; then
    log_warn "Failed to install: ${failed[*]} (non-critical, continuing)"
  fi
}

setup_ashell_environment() {
  log_info "Setting up a-Shell environment..."
  
  if [[ "$DRY_RUN" == true ]]; then
    log_info "[DRY-RUN] Would create directory: $ASHELL_HOME"
  else
    mkdir -p "$ASHELL_HOME"
    log_success "Created $ASHELL_HOME"
  fi
  
  create_menu_script
  create_helpers_file
}

create_menu_script() {
  local menu_file="${ASHELL_HOME}/menu.sh"
  
  log_info "Creating menu script..."
  
  if [[ "$DRY_RUN" == true ]]; then
    log_info "[DRY-RUN] Would create: $menu_file"
    return
  fi
  
  cat <<'MENU_EOF' > "$menu_file"
#!/bin/bash

echo "==================================="
echo "   a-Shell DevOps Hub Menu"
echo "==================================="
echo ""
echo "Choose an action:"
echo "  1) Open Repository"
echo "  2) List Issues"
echo "  3) Create Pull Request"
echo "  4) Commit Changes"
echo "  5) Exit"
echo ""
read -p "Enter your choice (1-5): " choice

case $choice in
  1) echo "Opening Repository..." ;;
  2) echo "Listing Issues..." ;;
  3) echo "Creating Pull Request..." ;;
  4) echo "Committing Changes..." ;;
  5) echo "Exiting..." ; exit 0 ;;
  *) echo "Invalid choice. Please try again." ; exit 1 ;;
esac
MENU_EOF

  chmod +x "$menu_file"
  log_success "Created $menu_file"
}

create_helpers_file() {
  local helpers_file="${ASHELL_HOME}/helpers.sh"
  
  log_info "Creating helper functions file..."
  
  if [[ "$DRY_RUN" == true ]]; then
    log_info "[DRY-RUN] Would create: $helpers_file"
    return
  fi
  
  cat <<'HELPERS_EOF' > "$helpers_file"
#!/bin/bash

# Helper functions for a-Shell DevOps workflows

ashell_open_repo() {
  if [[ -z "$1" ]]; then
    echo "Usage: ashell_open_repo <repo-url-or-path>"
    return 1
  fi
  echo "Opening repository: $1"
}

ashell_list_issues() {
  echo "Listing issues... (Not yet implemented)"
}

ashell_create_pr() {
  echo "Creating PR... (Not yet implemented)"
}
HELPERS_EOF

  chmod +x "$helpers_file"
  log_success "Created $helpers_file"
}

configure_shell_rc() {
  log_info "Configuring shell configuration..."
  
  case "$TARGET_SHELL" in
    zsh)
      configure_rc_file "${HOME}/.zshrc"
      ;;
    bash)
      configure_rc_file "${HOME}/.bashrc"
      ;;
    fish)
      configure_fish_config
      ;;
    *)
      log_warn "Unsupported shell: $TARGET_SHELL. Skipping configuration."
      return 1
      ;;
  esac
}

configure_rc_file() {
  local rc_file=$1
  local alias_cmd="alias /='bash ${ASHELL_HOME}/menu.sh'"
  local source_cmd="source ${ASHELL_HOME}/helpers.sh"
  
  log_info "Configuring $rc_file..."
  
  if [[ "$DRY_RUN" == true ]]; then
    log_info "[DRY-RUN] Would add to $rc_file:"
    log_info "  $alias_cmd"
    log_info "  $source_cmd"
    return
  fi
  
  if [[ -f "$rc_file" ]]; then
    run_cmd cp "$rc_file" "${rc_file}.backup"
  fi
  
  if grep -q "alias /=" "$rc_file" 2>/dev/null; then
    log_warn "Alias already exists in $rc_file, skipping"
  else
    {
      echo ""
      echo "# a-Shell DevOps Hub Configuration"
      echo "$alias_cmd"
      echo "$source_cmd"
    } >> "$rc_file"
    log_success "Added configuration to $rc_file"
  fi
}

configure_fish_config() {
  local fish_config="${HOME}/.config/fish/config.fish"
  
  log_info "Configuring fish shell..."
  
  if [[ "$DRY_RUN" == true ]]; then
    log_info "[DRY-RUN] Would configure: $fish_config"
    return
  fi
  
  mkdir -p "${HOME}/.config/fish"
  
  if [[ -f "$fish_config" ]]; then
    run_cmd cp "$fish_config" "${fish_config}.backup"
  fi
  
  if grep -q "alias /" "$fish_config" 2>/dev/null; then
    log_warn "Alias already exists in $fish_config, skipping"
  else
    {
      echo ""
      echo "# a-Shell DevOps Hub Configuration"
      echo "alias / 'bash ${ASHELL_HOME}/menu.sh'"
      echo "source ${ASHELL_HOME}/helpers.sh"
    } >> "$fish_config"
    log_success "Added configuration to $fish_config"
  fi
}

# ============================================================================
# Cleanup & Final Steps
# ============================================================================

cleanup() {
  local exit_code=$?
  
  if [[ $exit_code -ne 0 ]]; then
    log_error "Installation failed with exit code $exit_code"
    log_info "Backups saved to: $BACKUP_DIR"
  fi
  
  exit $exit_code
}

verify_installation() {
  log_info "Verifying installation..."
  
  local checks=(
    "git:Git"
    "fzf:Fuzzy Finder"
    "zoxide:Zoxide"
  )
  
  local failed=()
  
  for check in "${checks[@]}"; do
    local cmd="${check%:*}"
    local name="${check#*:}"
    
    if command -v "$cmd" &>/dev/null; then
      log_success "$name installed"
    else
      failed+=("$name")
    fi
  done
  
  if [[ ${#failed[@]} -gt 0 ]]; then
    log_warn "Missing: ${failed[*]}"
  fi
}

print_summary() {
  cat <<EOF

${GREEN}════════════════════════════════════════════════${NC}
${GREEN}Installation Complete!${NC}
${GREEN}════════════════════════════════════════════════${NC}

📁 a-Shell directory: $ASHELL_HOME
🎯 Menu trigger:     /
🐚 Shell configured: $TARGET_SHELL

${YELLOW}Next Steps:${NC}
1. Reload your shell configuration:
   - For zsh: source ~/.zshrc
   - For bash: source ~/.bashrc
   - For fish: source ~/.config/fish/config.fish

2. Test the command palette:
   /

3. If you need to revert, backups are at:
   $BACKUP_DIR

${BLUE}Need help?${NC}
- View menu: /
- Check helpers: cat ${ASHELL_HOME}/helpers.sh

EOF
}

# ============================================================================
# Main Execution
# ============================================================================

main() {
  trap cleanup EXIT
  
  log_info "a-Shell DevOps Hub Installation Script"
  
  if [[ "$DRY_RUN" == true ]]; then
    log_warn "Running in DRY-RUN mode - no changes will be made"
  fi
  
  parse_args "$@"
  check_prerequisites
  detect_package_manager
  
  backup_configs
  install_base_tools
  install_dev_tools
  setup_ashell_environment
  configure_shell_rc
  verify_installation
  print_summary
}

main "$@"
