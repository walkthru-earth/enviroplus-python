#!/bin/bash
#
# OpenSensor Space Installer
# Interactive installation and configuration script
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONFIG_FILE="$SCRIPT_DIR/config.env"
VENV_PATH="$PROJECT_ROOT/.venv"

# Print functions
print_header() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}  ${GREEN}OpenSensor Space - Smart Installer${NC}                    ${BLUE}║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo
}

print_step() {
    echo -e "${GREEN}▶${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

# Ask yes/no question
ask_yes_no() {
    local prompt="$1"
    local default="${2:-n}"
    local response

    if [ "$default" = "y" ]; then
        prompt="$prompt [Y/n]: "
    else
        prompt="$prompt [y/N]: "
    fi

    read -p "$prompt" response
    response=${response:-$default}

    case "$response" in
        [yY]|[yY][eE][sS]) return 0 ;;
        *) return 1 ;;
    esac
}

# Ask for input with default value
ask_input() {
    local prompt="$1"
    local default="$2"
    local response

    if [ -n "$default" ]; then
        read -p "$prompt [$default]: " response
        echo "${response:-$default}"
    else
        read -p "$prompt: " response
        echo "$response"
    fi
}

# Generate UUID
generate_uuid() {
    python3 -c "import uuid; print(str(uuid.uuid4()))"
}

# Check if command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Main installation
main() {
    print_header

    print_step "Checking system requirements..."

    # Check for Python
    if ! command_exists python3; then
        print_error "Python 3 is not installed. Please install Python 3.9+ first."
        exit 1
    fi

    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    print_success "Python $PYTHON_VERSION found"

    # Check for UV
    if ! command_exists uv; then
        print_warning "UV package manager not found."
        if ask_yes_no "Would you like to install UV now?" "y"; then
            print_step "Installing UV..."
            curl -LsSf https://astral.sh/uv/install.sh | sh
            export PATH="$HOME/.local/bin:$PATH"
            print_success "UV installed successfully"
        else
            print_error "UV is required. Please install it manually: https://docs.astral.sh/uv/"
            exit 1
        fi
    else
        print_success "UV package manager found"
    fi

    echo
    print_step "Setting up Python environment..."

    # Navigate to project root
    cd "$PROJECT_ROOT"

    # Check if virtual environment exists
    if [ ! -d "$VENV_PATH" ]; then
        print_info "Creating virtual environment..."
        uv venv
    fi

    # Install opensensor-space dependencies
    print_info "Installing dependencies (this may take a few minutes)..."
    uv pip install -e ".[opensensor-space]"
    print_success "Dependencies installed"

    echo
    print_step "Configuring OpenSensor Space..."

    # Check if config already exists
    if [ -f "$CONFIG_FILE" ]; then
        print_warning "Configuration file already exists."
        if ! ask_yes_no "Would you like to reconfigure?" "n"; then
            print_info "Keeping existing configuration."
        else
            rm "$CONFIG_FILE"
        fi
    fi

    if [ ! -f "$CONFIG_FILE" ]; then
        print_info "Creating configuration file..."

        # Station ID
        echo
        print_info "Station ID must be a UUID (universally unique identifier)"
        if ask_yes_no "Generate a new UUID automatically?" "y"; then
            STATION_ID=$(generate_uuid)
            print_success "Generated UUID: $STATION_ID"
        else
            STATION_ID=$(ask_input "Enter your station UUID")
        fi

        # Sensor configuration
        echo
        READ_INTERVAL=$(ask_input "Sensor reading interval in seconds" "5")
        BATCH_DURATION=$(ask_input "Batch duration in seconds (900 = 15 minutes)" "900")

        # Cloud sync configuration
        echo
        print_info "Cloud Storage Sync Configuration (optional)"
        if ask_yes_no "Enable automatic cloud storage sync?" "y"; then
            SYNC_ENABLED="true"

            echo
            print_info "Storage Provider Options:"
            echo "  1) Source Cooperative (S3-compatible)"
            echo "  2) AWS S3"
            echo "  3) Backblaze B2"
            echo "  4) Other S3-compatible"

            STORAGE_CHOICE=$(ask_input "Select storage provider [1-4]" "1")

            case $STORAGE_CHOICE in
                1)
                    STORAGE_PROVIDER="s3"
                    STORAGE_ENDPOINT="https://data.source.coop"
                    STORAGE_REGION="us-west-2"
                    print_info "Using Source Cooperative"
                    echo
                    print_info "For Source Cooperative:"
                    print_info "  Bucket format: us-west-2.opendata.source.coop"
                    print_info "  Prefix example: username/project-name/data"
                    ;;
                2)
                    STORAGE_PROVIDER="s3"
                    STORAGE_ENDPOINT=""
                    STORAGE_REGION=$(ask_input "AWS region" "us-west-2")
                    ;;
                3)
                    STORAGE_PROVIDER="s3"
                    STORAGE_ENDPOINT="https://s3.us-west-000.backblazeb2.com"
                    STORAGE_REGION="us-west-000"
                    ;;
                4)
                    STORAGE_PROVIDER="s3"
                    STORAGE_ENDPOINT=$(ask_input "S3 endpoint URL")
                    STORAGE_REGION=$(ask_input "Region" "us-west-2")
                    ;;
            esac

            echo
            STORAGE_BUCKET=$(ask_input "Bucket name" "us-west-2.opendata.source.coop")
            STORAGE_PREFIX=$(ask_input "Prefix/path within bucket" "username/project-name/sensor-data")

            echo
            print_info "Storage Credentials"
            AWS_ACCESS_KEY_ID=$(ask_input "Access Key ID")
            AWS_SECRET_ACCESS_KEY=$(ask_input "Secret Access Key")

            SYNC_INTERVAL=$(ask_input "Sync interval in minutes" "15")
        else
            SYNC_ENABLED="false"
        fi

        # Write configuration file
        cat > "$CONFIG_FILE" << EOF
# OpenSensor Space Configuration
# Generated on $(date)

# Station Configuration
STATION_ID=$STATION_ID

# Sensor Reading Configuration
READ_INTERVAL=$READ_INTERVAL
BATCH_DURATION=$BATCH_DURATION

# Temperature Compensation
TEMP_COMPENSATION_ENABLED=true
TEMP_COMPENSATION_FACTOR=2.25

# Object Storage Configuration
STORAGE_PROVIDER=${STORAGE_PROVIDER:-s3}
STORAGE_ENDPOINT=${STORAGE_ENDPOINT:-}
STORAGE_REGION=${STORAGE_REGION:-us-west-2}
STORAGE_BUCKET=${STORAGE_BUCKET:-}
STORAGE_PREFIX=${STORAGE_PREFIX:-}

# Storage Credentials
AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID:-}
AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY:-}

# Sync Configuration
SYNC_ENABLED=$SYNC_ENABLED
SYNC_INTERVAL_MINUTES=${SYNC_INTERVAL:-15}

# Logging
LOG_LEVEL=INFO
EOF

        print_success "Configuration file created: $CONFIG_FILE"
    fi

    # Update sync script with config values
    if [ "$SYNC_ENABLED" = "true" ]; then
        echo
        print_step "Configuring rclone for cloud sync..."

        if ! command_exists rclone; then
            print_warning "rclone not found."
            if ask_yes_no "Install rclone now?" "y"; then
                curl https://rclone.org/install.sh | sudo bash
                print_success "rclone installed"
            fi
        fi

        if command_exists rclone; then
            print_info "rclone configuration saved. You can run 'rclone config' to modify."
        fi
    fi

    # Systemd service setup
    echo
    print_step "Setting up system services..."

    if ask_yes_no "Install systemd services for automatic startup?" "y"; then
        print_info "Installing systemd services..."

        # Update paths in service files
        sed "s|/home/pi/enviroplus-python|$PROJECT_ROOT|g" "$SCRIPT_DIR/systemd/opensensor_space_systemd.service" | sudo tee /etc/systemd/system/opensensor-space.service > /dev/null

        if [ "$SYNC_ENABLED" = "true" ]; then
            sed "s|/home/pi/enviroplus-python|$PROJECT_ROOT|g" "$SCRIPT_DIR/systemd/sync_timer.service" | sudo tee /etc/systemd/system/opensensor-sync.service > /dev/null
            sed "s|OnUnitActiveSec=.*|OnUnitActiveSec=${SYNC_INTERVAL}min|g" "$SCRIPT_DIR/systemd/sync_timer.timer" | sudo tee /etc/systemd/system/opensensor-sync.timer > /dev/null
        fi

        sudo systemctl daemon-reload

        if ask_yes_no "Enable opensensor-space service to start on boot?" "y"; then
            sudo systemctl enable opensensor-space.service
            print_success "Service enabled"
        fi

        if [ "$SYNC_ENABLED" = "true" ] && ask_yes_no "Enable automatic sync timer?" "y"; then
            sudo systemctl enable opensensor-sync.timer
            print_success "Sync timer enabled"
        fi
    fi

    # Create log directory
    mkdir -p "$PROJECT_ROOT/logs"

    echo
    print_header
    print_success "Installation completed successfully!"
    echo
    print_info "Configuration file: $CONFIG_FILE"
    print_info "Data output directory: $PROJECT_ROOT/output"
    print_info "Logs directory: $PROJECT_ROOT/logs"
    echo
    print_step "Next steps:"
    echo "  1. Review configuration: nano $CONFIG_FILE"
    echo "  2. Test data collection: uv run python $SCRIPT_DIR/opensensor_space.py"
    if [ "$SYNC_ENABLED" = "true" ]; then
        echo "  3. Test cloud sync: $SCRIPT_DIR/sync_to_storage.sh"
    fi
    echo "  4. Start service: sudo systemctl start opensensor-space.service"
    echo "  5. Monitor logs: tail -f $PROJECT_ROOT/logs/opensensor_space.log"
    echo
    print_info "For more information, see: $SCRIPT_DIR/README.md"
    echo
}

# Run main installation
main
