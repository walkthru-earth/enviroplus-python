#!/bin/bash
# Modern installation script using UV package manager
# For traditional pip installation, use ./install.sh instead

set -e  # Exit on error

LIBRARY_NAME=$(grep -m 1 name pyproject.toml | awk -F" = " '{print substr($2,2,length($2)-2)}')
CONFIG_FILE=config.txt
CONFIG_DIR="/boot/firmware"
DATESTAMP=$(date "+%Y-%m-%d-%H-%M-%S")
CONFIG_BACKUP=false
APT_HAS_UPDATED=false
USAGE="./install-uv.sh [OPTIONS]

OPTIONS:
    --unstable          Install from source instead of PyPI
    --with-examples     Install example dependencies
    --with-dev          Install development dependencies
    --skip-hardware     Skip hardware configuration (I2C, SPI, serial)
    --help              Show this help message
"

# Options
INSTALL_UNSTABLE=false
INSTALL_EXAMPLES=false
INSTALL_DEV=false
SKIP_HARDWARE=false

# Colors and formatting
success() { echo -e "\033[0;32m$1\033[0m"; }
inform() { echo -e "\033[0;36m$1\033[0m"; }
warning() { echo -e "\033[0;31m⚠ WARNING:\033[0m $1"; }
fatal() { echo -e "\033[0;31m⚠ FATAL:\033[0m $1"; exit 1; }

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --unstable) INSTALL_UNSTABLE=true; shift ;;
        --with-examples) INSTALL_EXAMPLES=true; shift ;;
        --with-dev) INSTALL_DEV=true; shift ;;
        --skip-hardware) SKIP_HARDWARE=true; shift ;;
        -h|--help) echo "$USAGE"; exit 0 ;;
        *) echo "Unknown option: $1"; echo "$USAGE"; exit 1 ;;
    esac
done

# Check not running as root
if [ "$(id -u)" -eq 0 ]; then
    fatal "Script should not be run as root. Try './install-uv.sh'"
fi

printf "\n"
inform "═══════════════════════════════════════════════════════════"
inform "  Installing $LIBRARY_NAME with UV (Modern Python Manager)"
inform "═══════════════════════════════════════════════════════════"
printf "\n"

# Install UV if not present
if ! command -v uv &> /dev/null; then
    inform "UV not found. Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Source UV into current shell
    export PATH="$HOME/.local/bin:$PATH"

    if ! command -v uv &> /dev/null; then
        fatal "UV installation failed. Please install manually: https://docs.astral.sh/uv/"
    fi

    success "✓ UV installed successfully"
else
    UV_VERSION=$(uv --version)
    inform "✓ UV already installed ($UV_VERSION)"
fi

printf "\n"

# Install system dependencies (required for hardware and some Python packages)
inform "Installing system dependencies..."

if [ ! $APT_HAS_UPDATED ]; then
    sudo apt update
    APT_HAS_UPDATED=true
fi

# Install system packages needed for compilation and hardware access
sudo apt install -y python3-dev python3-pip python3-cffi libportaudio2

success "✓ System dependencies installed"
printf "\n"

# Find config file location
find_config() {
    if [ ! -f "$CONFIG_DIR/$CONFIG_FILE" ]; then
        CONFIG_DIR="/boot"
        if [ ! -f "$CONFIG_DIR/$CONFIG_FILE" ]; then
            warning "Could not find $CONFIG_FILE - skipping boot config"
            return 1
        fi
    fi
    inform "Using $CONFIG_FILE in $CONFIG_DIR"
    return 0
}

# Backup config file
do_config_backup() {
    if [ ! $CONFIG_BACKUP == true ]; then
        CONFIG_BACKUP=true
        FILENAME="config.preinstall-$LIBRARY_NAME-$DATESTAMP.txt"
        inform "Backing up $CONFIG_DIR/$CONFIG_FILE to $CONFIG_DIR/$FILENAME"
        sudo cp "$CONFIG_DIR/$CONFIG_FILE" "$CONFIG_DIR/$FILENAME"
    fi
}

# Configure hardware interfaces (I2C, SPI, Serial)
if [ "$SKIP_HARDWARE" = false ]; then
    inform "Configuring hardware interfaces (I2C, SPI, Serial)..."

    printf "  → Enabling SPI...\n"
    sudo raspi-config nonint do_spi 0

    printf "  → Enabling I2C...\n"
    sudo raspi-config nonint do_i2c 0

    printf "  → Configuring serial for PMS5003...\n"
    sudo raspi-config nonint do_serial_cons 1
    sudo raspi-config nonint do_serial_hw 0

    success "✓ Hardware interfaces configured"
    printf "\n"

    # Update boot config
    if find_config; then
        do_config_backup

        inform "Adding device tree overlays to $CONFIG_DIR/$CONFIG_FILE..."

        # Add overlays if not present
        for overlay in "dtoverlay=pi3-miniuart-bt" "dtoverlay=adau7002-simple"; do
            sudo sed -i "s/^#$overlay/$overlay/" $CONFIG_DIR/$CONFIG_FILE
            if ! grep -q "^$overlay" $CONFIG_DIR/$CONFIG_FILE; then
                echo "$overlay" | sudo tee -a $CONFIG_DIR/$CONFIG_FILE > /dev/null
            fi
        done

        success "✓ Boot configuration updated"
        printf "\n"
    fi
else
    warning "Skipping hardware configuration (--skip-hardware flag)"
    printf "\n"
fi

# Create virtual environment
inform "Creating isolated virtual environment..."

if [ -d ".venv" ]; then
    warning "Virtual environment already exists at .venv"
    read -p "Remove and recreate? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf .venv
    else
        inform "Using existing virtual environment"
    fi
fi

if [ ! -d ".venv" ]; then
    uv venv
    success "✓ Virtual environment created at .venv"
else
    inform "✓ Using existing virtual environment"
fi

printf "\n"

# Install the package
inform "Installing $LIBRARY_NAME..."

if [ "$INSTALL_UNSTABLE" = true ]; then
    warning "Installing from source (unstable)"
    uv pip install -e .
else
    inform "Installing from PyPI (stable)"
    uv pip install enviroplus
fi

success "✓ $LIBRARY_NAME installed"
printf "\n"

# Install optional dependencies
EXTRAS=""

if [ "$INSTALL_EXAMPLES" = true ]; then
    inform "Installing example dependencies..."
    uv pip install -e ".[examples]"
    success "✓ Example dependencies installed"
    printf "\n"
fi

if [ "$INSTALL_DEV" = true ]; then
    inform "Installing development dependencies..."
    uv sync --group dev
    success "✓ Development dependencies installed"
    printf "\n"
fi

# Create lockfile for reproducibility
inform "Creating lockfile for reproducible installs..."
uv pip freeze > uv-requirements.lock
success "✓ Lockfile created: uv-requirements.lock"
printf "\n"

# Installation complete
success "═══════════════════════════════════════════════════════════"
success "  Installation Complete!"
success "═══════════════════════════════════════════════════════════"
printf "\n"

inform "Next steps:"
echo "  1. Activate the environment:"
echo "     $ source .venv/bin/activate"
echo ""
echo "  2. Or run commands directly with UV:"
echo "     $ uv run python examples/weather.py"
echo ""
echo "  3. Install optional dependencies:"
echo "     $ uv pip install -e .[examples]    # For examples"
echo "     $ uv sync --group dev              # For development"
echo ""

if [ "$SKIP_HARDWARE" = false ]; then
    warning "IMPORTANT: Reboot required for hardware changes to take effect"
    echo "           Run: sudo reboot"
    printf "\n"
fi

inform "Documentation: https://github.com/pimoroni/enviroplus-python"
printf "\n"
