#!/usr/bin/env python3
"""
Enviro+ Hardware Setup Tool

This tool helps configure your Raspberry Pi for use with Enviro+ boards.
It checks system requirements and optionally installs/configures everything needed.

Usage:
    enviroplus-setup --check          # Check system status
    enviroplus-setup --install        # Install and configure (requires sudo)
    enviroplus-setup --help           # Show help
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output"""

    GREEN = "\033[0;32m"
    CYAN = "\033[0;36m"
    RED = "\033[0;31m"
    YELLOW = "\033[0;33m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def success(msg):
    """Print success message in green"""
    print(f"{Colors.GREEN}✓ {msg}{Colors.RESET}")


def info(msg):
    """Print info message in cyan"""
    print(f"{Colors.CYAN}{msg}{Colors.RESET}")


def warning(msg):
    """Print warning message in yellow"""
    print(f"{Colors.YELLOW}⚠ WARNING: {msg}{Colors.RESET}")


def error(msg):
    """Print error message in red"""
    print(f"{Colors.RED}✗ ERROR: {msg}{Colors.RESET}")


def run_command(cmd, check=False, capture=True):
    """
    Run a shell command and return result

    Args:
        cmd: Command to run (string or list)
        check: Raise exception on error
        capture: Capture output (otherwise print to console)

    Returns:
        subprocess.CompletedProcess object
    """
    try:
        if capture:
            result = subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True, text=True, check=check)
        else:
            result = subprocess.run(cmd, shell=isinstance(cmd, str), check=check)
        return result
    except subprocess.CalledProcessError as e:
        if check:
            raise
        return e


def is_root():
    """Check if running as root"""
    return os.geteuid() == 0


def is_raspberry_pi():
    """Check if running on Raspberry Pi"""
    try:
        with open("/proc/cpuinfo", "r") as f:
            cpuinfo = f.read()
            return "Raspberry Pi" in cpuinfo or "BCM" in cpuinfo
    except FileNotFoundError:
        return False


def get_os_info():
    """Get OS and distribution information"""
    info = {
        "system": platform.system(),
        "machine": platform.machine(),
        "python_version": platform.python_version(),
    }

    # Try to get distribution info
    try:
        with open("/etc/os-release", "r") as f:
            for line in f:
                if line.startswith("PRETTY_NAME="):
                    info["distro"] = line.split("=")[1].strip().strip('"')
                    break
    except FileNotFoundError:
        info["distro"] = "Unknown"

    return info


def check_apt_package(package):
    """
    Check if an apt package is installed

    Args:
        package: Package name to check

    Returns:
        bool: True if installed, False otherwise
    """
    result = run_command(f"dpkg -l {package}", capture=True)
    return result.returncode == 0 and f"ii  {package}" in result.stdout


def check_i2c_enabled():
    """Check if I2C is enabled"""
    # Check if i2c-dev module is loaded
    result = run_command("lsmod | grep i2c_dev", capture=True)
    if result.returncode != 0:
        return False

    # Check if /dev/i2c-1 exists
    return Path("/dev/i2c-1").exists()


def check_spi_enabled():
    """Check if SPI is enabled"""
    # Check if spi module is loaded
    result = run_command("lsmod | grep spi_", capture=True)
    if result.returncode != 0:
        return False

    # Check if /dev/spidev0.0 exists
    return Path("/dev/spidev0.0").exists()


def check_serial_enabled():
    """Check if serial/UART is enabled"""
    # Check if serial devices exist
    serial_devices = ["/dev/serial0", "/dev/ttyAMA0", "/dev/ttyS0"]
    return any(Path(dev).exists() for dev in serial_devices)


def check_config_overlay(overlay):
    """
    Check if a device tree overlay is configured in config.txt

    Args:
        overlay: Overlay name (e.g., "dtoverlay=pi3-miniuart-bt")

    Returns:
        bool: True if overlay is present and enabled
    """
    config_paths = ["/boot/firmware/config.txt", "/boot/config.txt"]

    for config_path in config_paths:
        if not Path(config_path).exists():
            continue

        try:
            with open(config_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line == overlay:
                        return True
        except PermissionError:
            warning(f"Cannot read {config_path} (permission denied)")
            return None

    return False


class SystemChecker:
    """Check system requirements for Enviro+"""

    REQUIRED_APT_PACKAGES = ["python3-cffi", "libportaudio2"]

    REQUIRED_OVERLAYS = ["dtoverlay=pi3-miniuart-bt", "dtoverlay=adau7002-simple"]

    def __init__(self):
        self.results = {}

    def check_all(self):
        """Run all system checks"""
        print(f"\n{Colors.BOLD}{'=' * 60}{Colors.RESET}")
        print(f"{Colors.BOLD}  Enviro+ System Requirements Check{Colors.RESET}")
        print(f"{Colors.BOLD}{'=' * 60}{Colors.RESET}\n")

        # System info
        info_data = get_os_info()
        info(f"System: {info_data['system']} {info_data['machine']}")
        info(f"Distribution: {info_data['distro']}")
        info(f"Python: {info_data['python_version']}")

        if not is_raspberry_pi():
            warning("Not running on Raspberry Pi - hardware features may not work")
        else:
            success("Running on Raspberry Pi")

        print(f"\n{Colors.BOLD}System Packages:{Colors.RESET}")

        # Check apt packages
        all_packages_ok = True
        for package in self.REQUIRED_APT_PACKAGES:
            installed = check_apt_package(package)
            self.results[f"apt_{package}"] = installed

            if installed:
                success(f"{package}: Installed")
            else:
                error(f"{package}: Not installed")
                all_packages_ok = False

        print(f"\n{Colors.BOLD}Hardware Interfaces:{Colors.RESET}")

        # Check hardware interfaces
        i2c_ok = check_i2c_enabled()
        spi_ok = check_spi_enabled()
        serial_ok = check_serial_enabled()

        self.results["i2c"] = i2c_ok
        self.results["spi"] = spi_ok
        self.results["serial"] = serial_ok

        if i2c_ok:
            success("I2C: Enabled")
        else:
            error("I2C: Not enabled")

        if spi_ok:
            success("SPI: Enabled")
        else:
            error("SPI: Not enabled")

        if serial_ok:
            success("Serial/UART: Enabled")
        else:
            error("Serial/UART: Not enabled")

        print(f"\n{Colors.BOLD}Device Tree Overlays:{Colors.RESET}")

        # Check overlays
        overlays_ok = True
        for overlay in self.REQUIRED_OVERLAYS:
            status = check_config_overlay(overlay)
            self.results[f"overlay_{overlay}"] = status

            if status is True:
                success(f"{overlay}: Configured")
            elif status is None:
                warning(f"{overlay}: Cannot verify (permission denied)")
            else:
                error(f"{overlay}: Not configured")
                overlays_ok = False

        # Summary
        print(f"\n{Colors.BOLD}{'=' * 60}{Colors.RESET}")

        all_ok = all_packages_ok and i2c_ok and spi_ok and overlays_ok

        if all_ok:
            success("All requirements met! Your system is ready for Enviro+")
        else:
            warning("Some requirements are missing. Run with --install to configure.")
            print("\nTo install and configure everything:")
            print("  sudo enviroplus-setup --install")

        print(f"{Colors.BOLD}{'=' * 60}{Colors.RESET}\n")

        return all_ok

    def get_summary(self):
        """Get a summary of check results"""
        return self.results


class SystemInstaller:
    """Install and configure system requirements"""

    def __init__(self):
        self.checker = SystemChecker()
        self.config_backup_done = False

    def install_all(self, skip_hardware=False):
        """Install and configure everything"""

        if not is_root():
            error("Installation requires root privileges")
            print("Please run with sudo: sudo enviroplus-setup --install")
            return False

        if not is_raspberry_pi():
            warning("Not running on Raspberry Pi - skipping hardware configuration")
            skip_hardware = True

        print(f"\n{Colors.BOLD}{'=' * 60}{Colors.RESET}")
        print(f"{Colors.BOLD}  Enviro+ System Setup{Colors.RESET}")
        print(f"{Colors.BOLD}{'=' * 60}{Colors.RESET}\n")

        # Update apt cache
        info("Updating package lists...")
        result = run_command("apt update", capture=False)
        if result.returncode != 0:
            error("Failed to update package lists")
            return False
        success("Package lists updated")
        print()

        # Install apt packages
        info("Checking and installing system packages...")
        packages_to_install = []

        for package in SystemChecker.REQUIRED_APT_PACKAGES:
            if not check_apt_package(package):
                packages_to_install.append(package)
                info(f"  → {package} will be installed")
            else:
                success(f"  → {package} already installed")

        if packages_to_install:
            cmd = f"apt install -y {' '.join(packages_to_install)}"
            info(f"Installing: {' '.join(packages_to_install)}")
            result = run_command(cmd, capture=False)
            if result.returncode != 0:
                error("Failed to install packages")
                return False
            success(f"Installed {len(packages_to_install)} package(s)")
        else:
            success("All required packages already installed")

        print()

        if not skip_hardware:
            # Configure hardware interfaces
            info("Configuring hardware interfaces...")

            if not check_i2c_enabled():
                info("  → Enabling I2C...")
                run_command("raspi-config nonint do_i2c 0", capture=False)
                success("    I2C enabled")
            else:
                success("  → I2C already enabled")

            if not check_spi_enabled():
                info("  → Enabling SPI...")
                run_command("raspi-config nonint do_spi 0", capture=False)
                success("    SPI enabled")
            else:
                success("  → SPI already enabled")

            if not check_serial_enabled():
                info("  → Configuring serial for PMS5003...")
                run_command("raspi-config nonint do_serial_cons 1", capture=False)
                run_command("raspi-config nonint do_serial_hw 0", capture=False)
                success("    Serial configured")
            else:
                success("  → Serial already enabled")

            print()

            # Configure device tree overlays
            info("Configuring device tree overlays...")
            self._configure_overlays()

        print(f"\n{Colors.BOLD}{'=' * 60}{Colors.RESET}")
        success("Installation complete!")
        print(f"{Colors.BOLD}{'=' * 60}{Colors.RESET}\n")

        if not skip_hardware:
            warning("REBOOT REQUIRED for hardware changes to take effect")
            print("Run: sudo reboot")
            print()

        return True

    def _configure_overlays(self):
        """Configure device tree overlays in config.txt"""
        config_paths = ["/boot/firmware/config.txt", "/boot/config.txt"]
        config_path = None

        for path in config_paths:
            if Path(path).exists():
                config_path = path
                break

        if not config_path:
            warning("Could not find config.txt - skipping overlay configuration")
            return

        info(f"Using {config_path}")

        # Backup config file
        if not self.config_backup_done:
            timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            backup_path = f"{config_path}.backup-enviroplus-{timestamp}"
            info(f"Backing up to {backup_path}")
            shutil.copy2(config_path, backup_path)
            self.config_backup_done = True

        # Read current config
        with open(config_path, "r") as f:
            config_lines = f.readlines()

        modified = False

        for overlay in SystemChecker.REQUIRED_OVERLAYS:
            # Check if overlay is already present
            overlay_present = any(line.strip() == overlay for line in config_lines)

            if not overlay_present:
                # Check if it's commented out
                commented_line = f"#{overlay}"
                for i, line in enumerate(config_lines):
                    if line.strip() == commented_line:
                        config_lines[i] = f"{overlay}\n"
                        info(f"  → Enabled {overlay} (was commented)")
                        modified = True
                        break
                else:
                    # Add new line
                    config_lines.append(f"{overlay}\n")
                    info(f"  → Added {overlay}")
                    modified = True
            else:
                success(f"  → {overlay} already configured")

        if modified:
            # Write updated config
            with open(config_path, "w") as f:
                f.writelines(config_lines)
            success("Device tree overlays configured")
        else:
            success("All overlays already configured")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Enviro+ Hardware Setup Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  enviroplus-setup --check              Check system requirements
  sudo enviroplus-setup --install       Install and configure everything
  sudo enviroplus-setup --install --skip-hardware  Install packages only

Notes:
  - System package installation requires sudo/root
  - Hardware configuration requires Raspberry Pi and sudo/root
  - A reboot is required after hardware configuration
        """,
    )

    parser.add_argument("--check", action="store_true", help="Check system requirements (default action)")

    parser.add_argument("--install", action="store_true", help="Install and configure everything (requires sudo)")

    parser.add_argument("--skip-hardware", action="store_true", help="Skip hardware configuration (with --install)")

    args = parser.parse_args()

    # Default to check if no action specified
    if not args.install:
        args.check = True

    try:
        if args.install:
            installer = SystemInstaller()
            success_result = installer.install_all(skip_hardware=args.skip_hardware)
            sys.exit(0 if success_result else 1)

        elif args.check:
            checker = SystemChecker()
            all_ok = checker.check_all()
            sys.exit(0 if all_ok else 1)

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        error(f"Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
