#!/usr/bin/env python3
"""
a-Shell/iSH DevOps Bootstrap Script

Production-grade Python bootstrap for iOS terminal environments.
Supports cross-platform setup with robust error handling, logging, and recovery.

Usage:
    python3 bootstrap.py [--target=ashell|ish] [--verbose] [--dry-run]

Targets:
    ashell  - a-Shell native iOS app (lightweight, limited tools)
    ish     - iSH Alpine Linux emulation (full package manager, slower)
"""

import sys
import os
import subprocess
import logging
import platform
import json
from typing import Optional, List, Dict, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum


# ============================================================================
# Configuration & Constants
# ============================================================================

class Target(Enum):
    """Supported iOS terminal environments."""
    ASHELL = "ashell"
    ISH = "ish"


class Platform(Enum):
    """Operating system classification."""
    LINUX = "linux"
    MACOS = "darwin"
    WINDOWS = "windows"
    UNKNOWN = "unknown"


@dataclass
class BootstrapConfig:
    """Bootstrap configuration and runtime state."""
    target: Target
    verbose: bool
    dry_run: bool
    home_dir: Path
    config_dir: Path
    backup_dir: Path
    log_file: Path
    platform: Platform


# ============================================================================
# Logging System
# ============================================================================

class ColorFormatter(logging.Formatter):
    """Colored log formatter for terminal output."""
    
    COLORS = {
        'DEBUG': '\033[0;34m',      # Blue
        'INFO': '\033[0;32m',       # Green
        'WARNING': '\033[1;33m',    # Yellow
        'ERROR': '\033[0;31m',      # Red
        'CRITICAL': '\033[1;31m',   # Bold Red
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with color codes."""
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}[{levelname}]{self.RESET}"
        return super().format(record)


def setup_logging(config: BootstrapConfig) -> logging.Logger:
    """Configure logging with file and console handlers."""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG if config.verbose else logging.INFO)
    
    # File handler
    file_handler = logging.FileHandler(config.log_file)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG if config.verbose else logging.INFO)
    console_formatter = ColorFormatter(
        '%(levelname)s %(message)s' if config.verbose else '%(levelname)s %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


logger: Optional[logging.Logger] = None


def log_info(msg: str) -> None:
    """Log info message."""
    if logger:
        logger.info(msg)


def log_warn(msg: str) -> None:
    """Log warning message."""
    if logger:
        logger.warning(msg)


def log_error(msg: str) -> None:
    """Log error message."""
    if logger:
        logger.error(msg)


def log_debug(msg: str) -> None:
    """Log debug message."""
    if logger:
        logger.debug(msg)


# ============================================================================
# Platform Detection
# ============================================================================

def detect_platform() -> Platform:
    """Detect current operating system."""
    system = platform.system().lower()
    if system == "linux":
        return Platform.LINUX
    elif system == "darwin":
        return Platform.MACOS
    elif system == "windows":
        return Platform.WINDOWS
    return Platform.UNKNOWN


def detect_ios_terminal() -> Optional[Target]:
    """
    Detect which iOS terminal environment we're running in.
    
    Returns:
        Target if detected, None otherwise
    """
    # Check for a-Shell markers
    if Path("~/Documents").expanduser().exists() or os.getenv("ASHELL"):
        return Target.ASHELL
    
    # Check for iSH markers
    if Path("/usr/bin/apk").exists() or os.getenv("ISH"):
        return Target.ISH
    
    return None


# ============================================================================
# Command Execution
# ============================================================================

class CommandExecutor:
    """Handles command execution with error handling and logging."""
    
    def __init__(self, config: BootstrapConfig):
        self.config = config
    
    def run(
        self,
        cmd: List[str],
        check: bool = True,
        capture_output: bool = False,
        shell: bool = False,
    ) -> Tuple[int, str, str]:
        """
        Execute command with error handling.
        
        Args:
            cmd: Command and arguments
            check: Raise exception on non-zero exit
            capture_output: Capture stdout/stderr
            shell: Run command through shell
        
        Returns:
            Tuple of (returncode, stdout, stderr)
        """
        cmd_str = " ".join(cmd) if isinstance(cmd, list) else cmd
        
        if self.config.dry_run:
            log_info(f"[DRY-RUN] Would execute: {cmd_str}")
            return (0, "", "")
        
        log_debug(f"Executing: {cmd_str}")
        
        try:
            result = subprocess.run(
                cmd if isinstance(cmd, list) else cmd_str,
                shell=shell,
                check=check,
                capture_output=capture_output,
                text=True,
            )
            log_debug(f"Command succeeded with exit code {result.returncode}")
            return (result.returncode, result.stdout or "", result.stderr or "")
        except subprocess.CalledProcessError as e:
            log_error(f"Command failed with exit code {e.returncode}")
            log_debug(f"stderr: {e.stderr}")
            raise
    
    def check_command_exists(self, cmd: str) -> bool:
        """Check if command exists in PATH."""
        try:
            self.run(["which", cmd], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False


# ============================================================================
# Package Manager Detection
# ============================================================================

class PackageManager:
    """Handles package manager detection and installation."""
    
    def __init__(self, executor: CommandExecutor, config: BootstrapConfig):
        self.executor = executor
        self.config = config
        self.pm_type: Optional[str] = None
        self.pm_install_cmd: Optional[List[str]] = None
        self.pm_update_cmd: Optional[List[str]] = None
    
    def detect(self) -> bool:
        """
        Detect available package manager.
        
        Returns:
            True if package manager found, False otherwise
        """
        # Check for a-Shell specific package managers
        if self.config.target == Target.ASHELL:
            if self.executor.check_command_exists("pip3"):
                self.pm_type = "pip3"
                self.pm_install_cmd = ["pip3", "install"]
                log_info("Detected pip3 package manager (a-Shell)")
                return True
        
        # Check for iSH/Alpine
        if self.config.target == Target.ISH or self.executor.check_command_exists("apk"):
            self.pm_type = "apk"
            self.pm_install_cmd = ["apk", "add"]
            self.pm_update_cmd = ["apk", "update"]
            log_info("Detected apk package manager (Alpine/iSH)")
            return True
        
        # Check for standard package managers
        managers = [
            ("apt", ["apt-get", "install", "-y"], ["apt-get", "update"]),
            ("brew", ["brew", "install"], ["brew", "update"]),
            ("yum", ["sudo", "yum", "install", "-y"], ["sudo", "yum", "update"]),
            ("dnf", ["sudo", "dnf", "install", "-y"], ["sudo", "dnf", "update"]),
        ]
        
        for pm_name, install_cmd, update_cmd in managers:
            if self.executor.check_command_exists(pm_name):
                self.pm_type = pm_name
                self.pm_install_cmd = install_cmd
                self.pm_update_cmd = update_cmd
                log_info(f"Detected {pm_name} package manager")
                return True
        
        log_error("No supported package manager found")
        return False
    
    def install_package(self, package: str) -> bool:
        """Install a single package."""
        if not self.pm_install_cmd:
            log_error("No package manager configured")
            return False
        
        # Check if already installed
        if self.executor.check_command_exists(package):
            log_warn(f"Package '{package}' already installed, skipping")
            return True
        
        log_info(f"Installing {package}...")
        cmd = self.pm_install_cmd + [package]
        
        try:
            self.executor.run(cmd)
            if self.executor.check_command_exists(package):
                log_info(f"✓ Successfully installed {package}")
                return True
            else:
                log_error(f"✗ Verification failed: {package} not found after installation")
                return False
        except subprocess.CalledProcessError:
            log_error(f"✗ Failed to install {package}")
            return False


# ============================================================================
# File Operations
# ============================================================================

class FileManager:
    """Handles file operations with backup support."""
    
    def __init__(self, config: BootstrapConfig):
        self.config = config
    
    def backup_file(self, src: Path) -> Optional[Path]:
        """Create timestamped backup of file."""
        if not src.exists():
            return None
        
        self.config.backup_dir.mkdir(parents=True, exist_ok=True)
        backup_path = self.config.backup_dir / src.name
        
        if self.config.dry_run:
            log_info(f"[DRY-RUN] Would backup: {src} → {backup_path}")
            return backup_path
        
        try:
            backup_path.write_text(src.read_text())
            log_info(f"Backed up: {src} → {backup_path}")
            return backup_path
        except Exception as e:
            log_error(f"Failed to backup {src}: {e}")
            return None
    
    def create_file(self, path: Path, content: str, make_executable: bool = False) -> bool:
        """Create or update file with content."""
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if self.config.dry_run:
            log_info(f"[DRY-RUN] Would create: {path}")
            return True
        
        try:
            path.write_text(content)
            if make_executable:
                path.chmod(0o755)
                log_info(f"Created executable: {path}")
            else:
                log_info(f"Created: {path}")
            return True
        except Exception as e:
            log_error(f"Failed to create {path}: {e}")
            return False
    
    def append_to_file(self, path: Path, content: str, check_exists: bool = True) -> bool:
        """Append content to file if not already present."""
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if path.exists() and check_exists:
            existing = path.read_text()
            if content.strip() in existing:
                log_warn(f"Content already exists in {path}, skipping")
                return True
        
        if self.config.dry_run:
            log_info(f"[DRY-RUN] Would append to: {path}")
            return True
        
        try:
            with open(path, "a") as f:
                f.write(content)
            log_info(f"Appended to: {path}")
            return True
        except Exception as e:
            log_error(f"Failed to append to {path}: {e}")
            return False


# ============================================================================
# Bootstrap Steps
# ============================================================================

class BootstrapSteps:
    """Orchestrates bootstrap installation steps."""
    
    def __init__(
        self,
        config: BootstrapConfig,
        executor: CommandExecutor,
        pm: PackageManager,
        fm: FileManager,
    ):
        self.config = config
        self.executor = executor
        self.pm = pm
        self.fm = fm
    
    def validate_environment(self) -> bool:
        """Validate prerequisites and environment."""
        log_info("Validating environment...")
        
        # Check Python version
        if sys.version_info < (3, 7):
            log_error("Python 3.7+ required")
            return False
        
        log_info(f"✓ Python {sys.version.split()[0]} detected")
        
        # Check home directory
        if not self.config.home_dir.exists():
            log_error(f"Home directory not found: {self.config.home_dir}")
            return False
        
        log_info(f"✓ Home directory: {self.config.home_dir}")
        
        return True
    
    def setup_directories(self) -> bool:
        """Create required directories."""
        log_info("Setting up directories...")
        
        dirs = [
            self.config.config_dir,
            self.config.backup_dir,
            self.config.config_dir / "scripts",
        ]
        
        for dir_path in dirs:
            if self.config.dry_run:
                log_info(f"[DRY-RUN] Would create: {dir_path}")
            else:
                dir_path.mkdir(parents=True, exist_ok=True)
                log_info(f"Created: {dir_path}")
        
        return True
    
    def install_base_tools(self) -> bool:
        """Install essential base tools."""
        log_info("Installing base tools...")
        
        base_tools = {
            Target.ASHELL: ["python3", "curl"],
            Target.ISH: ["bash", "git", "curl", "python3", "nodejs"],
        }
        
        tools = base_tools.get(self.config.target, [])
        failed = []
        
        for tool in tools:
            if not self.pm.install_package(tool):
                failed.append(tool)
        
        if failed:
            log_warn(f"Failed to install: {', '.join(failed)}")
        
        return len(failed) == 0
    
    def install_dev_tools(self) -> bool:
        """Install optional development tools."""
        log_info("Installing development tools...")
        
        dev_tools = {
            Target.ASHELL: [],  # Limited availability in a-Shell
            Target.ISH: ["fzf", "zoxide", "vim", "nano"],
        }
        
        tools = dev_tools.get(self.config.target, [])
        failed = []
        
        for tool in tools:
            if not self.pm.install_package(tool):
                failed.append(tool)
        
        if failed:
            log_warn(f"Non-critical failures: {', '.join(failed)}")
        
        return True  # Non-critical
    
    def setup_shell_config(self) -> bool:
        """Configure shell environment."""
        log_info("Configuring shell environment...")
        
        shell_rc_files = {
            "bash": self.config.home_dir / ".bashrc",
            "zsh": self.config.home_dir / ".zshrc",
        }
        
        shell_config = f"""\
# a-Shell DevOps Hub Configuration
alias /='bash {self.config.config_dir}/menu.sh'
source {self.config.config_dir}/helpers.sh
"""
        
        for shell_name, rc_file in shell_rc_files.items():
            if rc_file.exists():
                self.fm.backup_file(rc_file)
                if self.fm.append_to_file(rc_file, shell_config):
                    log_info(f"Configured {shell_name}")
        
        return True
    
    def create_helper_scripts(self) -> bool:
        """Create menu and helper scripts."""
        log_info("Creating helper scripts...")
        
        # Create menu.sh
        menu_script = f"""#!/bin/bash

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
"""
        
        # Create helpers.sh
        helpers_script = f"""#!/bin/bash

# DevOps Helper Functions

ashell_open_repo() {{
  if [[ -z "$1" ]]; then
    echo "Usage: ashell_open_repo <repo-url-or-path>"
    return 1
  fi
  echo "Opening repository: $1"
}}

ashell_list_issues() {{
  echo "Listing issues... (Not yet implemented)"
}}

ashell_create_pr() {{
  echo "Creating PR... (Not yet implemented)"
}}
"""
        
        self.fm.create_file(self.config.config_dir / "menu.sh", menu_script, make_executable=True)
        self.fm.create_file(self.config.config_dir / "helpers.sh", helpers_script, make_executable=True)
        
        return True
    
    def verify_installation(self) -> bool:
        """Verify critical tools are installed."""
        log_info("Verifying installation...")
        
        critical_tools = ["git", "curl"]
        failed = []
        
        for tool in critical_tools:
            if not self.executor.check_command_exists(tool):
                failed.append(tool)
                log_error(f"✗ {tool} not found")
            else:
                log_info(f"✓ {tool} installed")
        
        return len(failed) == 0


# ============================================================================
# Main Bootstrap Orchestration
# ============================================================================

def parse_arguments() -> Tuple[Target, bool, bool]:
    """Parse command-line arguments."""
    target = Target.ASHELL  # Default
    verbose = False
    dry_run = False
    
    for arg in sys.argv[1:]:
        if arg.startswith("--target="):
            target_str = arg.split("=")[1]
            try:
                target = Target(target_str)
            except ValueError:
                print(f"Invalid target: {target_str}")
                print(f"Valid options: {', '.join([t.value for t in Target])}")
                sys.exit(1)
        elif arg == "--verbose" or arg == "-v":
            verbose = True
        elif arg == "--dry-run":
            dry_run = True
        elif arg == "--help" or arg == "-h":
            print(__doc__)
            sys.exit(0)
    
    return target, verbose, dry_run


def create_config(target: Target, verbose: bool, dry_run: bool) -> BootstrapConfig:
    """Create bootstrap configuration."""
    home = Path.home()
    now = int(__import__('time').time())
    
    return BootstrapConfig(
        target=target,
        verbose=verbose,
        dry_run=dry_run,
        home_dir=home,
        config_dir=home / ".ashell",
        backup_dir=home / f".dotfiles_backup.{now}",
        log_file=home / f".ashell_bootstrap.log",
        platform=detect_platform(),
    )


def main() -> int:
    """Main bootstrap entry point."""
    global logger
    
    # Parse arguments
    target, verbose, dry_run = parse_arguments()
    
    # Create configuration
    config = create_config(target, verbose, dry_run)
    
    # Setup logging
    logger = setup_logging(config)
    
    log_info(f"a-Shell/iSH Bootstrap v1.0")
    log_info(f"Target: {config.target.value}")
    log_info(f"Platform: {config.platform.value}")
    log_info(f"Home: {config.home_dir}")
    
    if config.dry_run:
        log_warn("Running in DRY-RUN mode - no changes will be made")
    
    # Initialize components
    executor = CommandExecutor(config)
    pm = PackageManager(executor, config)
    fm = FileManager(config)
    steps = BootstrapSteps(config, executor, pm, fm)
    
    try:
        # Execute bootstrap steps
        if not steps.validate_environment():
            log_error("Environment validation failed")
            return 1
        
        if not pm.detect():
            log_error("Package manager detection failed")
            return 1
        
        if not steps.setup_directories():
            log_error("Directory setup failed")
            return 1
        
        if not steps.install_base_tools():
            log_warn("Some base tools failed to install (non-fatal)")
        
        if not steps.install_dev_tools():
            log_warn("Some dev tools failed to install (non-fatal)")
        
        if not steps.setup_shell_config():
            log_error("Shell configuration failed")
            return 1
        
        if not steps.create_helper_scripts():
            log_error("Helper script creation failed")
            return 1
        
        if not steps.verify_installation():
            log_warn("Installation verification failed (some tools missing)")
        
        # Summary
        log_info("")
        log_info("════════════════════════════════════════════")
        log_info("✓ Bootstrap Complete!")
        log_info("════════════════════════════════════════════")
        log_info("")
        log_info(f"Config directory: {config.config_dir}")
        log_info(f"Menu command: /")
        log_info(f"Backups: {config.backup_dir}")
        log_info("")
        
        if not config.dry_run:
            log_info("Next steps:")
            log_info("1. Reload shell: source ~/.bashrc (or ~/.zshrc)")
            log_info("2. Test menu: /")
            log_info("3. View helpers: source ~/.ashell/helpers.sh")
        
        return 0
    
    except Exception as e:
        log_error(f"Bootstrap failed: {e}")
        log_debug(f"Exception: {type(e).__name__}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
