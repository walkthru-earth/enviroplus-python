#!/bin/bash
#
# Lightweight sync script for Raspberry Pi to object storage
# Uses rclone for efficient, multi-cloud compatible sync with logging
#
# This script syncs the local output directory to object storage
# It includes error handling, logging, and notification support

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Load configuration from config.env
CONFIG_FILE="$SCRIPT_DIR/config.env"
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
else
    echo "ERROR: Configuration file not found: $CONFIG_FILE"
    echo "Please run install-opensensor-space.sh first to create configuration."
    exit 1
fi

# Check if sync is enabled
if [ "${SYNC_ENABLED:-false}" != "true" ]; then
    echo "Sync is disabled in configuration. Exiting."
    exit 0
fi

# Configuration from environment or defaults
OUTPUT_DIR="${OUTPUT_DIR:-$PROJECT_DIR/output}"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="${LOG_DIR}/sync.log"
ERROR_LOG="${LOG_DIR}/sync_error.log"

# Check required storage configuration
if [ -z "$STORAGE_BUCKET" ]; then
    echo "ERROR: STORAGE_BUCKET not set in config.env"
    exit 1
fi

if [ -z "$STORAGE_PREFIX" ]; then
    echo "ERROR: STORAGE_PREFIX not set in config.env"
    exit 1
fi

# Set rclone environment variables for S3 authentication
# This modern approach avoids needing a config file
export RCLONE_S3_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}"
export RCLONE_S3_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}"
export RCLONE_S3_REGION="${STORAGE_REGION:-us-west-2}"
export RCLONE_S3_ENDPOINT="${STORAGE_ENDPOINT}"
export RCLONE_S3_PROVIDER="Other"

# Build remote path using on-the-fly backend syntax
# Format: :s3:bucket/prefix (no config file needed!)
REMOTE_PATH=":s3:${STORAGE_BUCKET}/${STORAGE_PREFIX}"

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to log errors
log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" | tee -a "$ERROR_LOG" >&2
}

# Check if rclone is installed
if ! command -v rclone &> /dev/null; then
    log_error "rclone is not installed. Please install it first:"
    log_error "  curl https://rclone.org/install.sh | sudo bash"
    exit 1
fi

# Check if output directory exists
if [ ! -d "$OUTPUT_DIR" ]; then
    log_error "Output directory does not exist: $OUTPUT_DIR"
    exit 1
fi

# Count files to sync
FILE_COUNT=$(find "$OUTPUT_DIR" -type f -name "*.parquet" | wc -l)

if [ "$FILE_COUNT" -eq 0 ]; then
    log_message "No parquet files to sync. Exiting."
    exit 0
fi

log_message "Starting sync operation. Files to process: $FILE_COUNT"

# Perform the sync with rclone
# Options explained:
#   --update: Skip files that are newer on the destination
#   --verbose: Provide detailed output
#   --transfers 4: Use 4 parallel transfers (good for Raspberry Pi)
#   --checkers 8: Use 8 parallel file checkers
#   --contimeout 60s: Connection timeout
#   --timeout 300s: IO idle timeout
#   --retries 3: Retry failed operations 3 times
#   --low-level-retries 10: Low level retries
#   --stats 30s: Print stats every 30 seconds
#   --stats-one-line: Keep stats on one line

rclone sync "$OUTPUT_DIR" "$REMOTE_PATH" \
    --update \
    --verbose \
    --transfers 4 \
    --checkers 8 \
    --contimeout 60s \
    --timeout 300s \
    --retries 3 \
    --low-level-retries 10 \
    --stats 30s \
    --stats-one-line \
    --log-file="$LOG_FILE" \
    --log-level INFO

# Capture exit code
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    log_message "Sync completed successfully. $FILE_COUNT files processed."

    # Optional: Send success notification (uncomment to enable)
    # notify-send "Sensor Data Sync" "Successfully synced $FILE_COUNT files to storage"

else
    log_error "Sync failed with exit code $EXIT_CODE"

    # Optional: Send error notification (uncomment to enable)
    # notify-send -u critical "Sensor Data Sync" "Sync failed with exit code $EXIT_CODE"

fi

# Optional: Rotate log files if they get too large (>10MB)
if [ -f "$LOG_FILE" ] && [ $(stat -f%z "$LOG_FILE" 2>/dev/null || stat -c%s "$LOG_FILE" 2>/dev/null) -gt 10485760 ]; then
    mv "$LOG_FILE" "${LOG_FILE}.$(date +%Y%m%d_%H%M%S)"
    log_message "Rotated log file (exceeded 10MB)"
fi

exit $EXIT_CODE
