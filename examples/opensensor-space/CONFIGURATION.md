# Configuration Reference

Quick reference for all configuration variables in `config.env`.

## Station Configuration

```bash
# Unique identifier for this sensor station (UUID v4 format)
# Generate with: python3 -c "import uuid; print(uuid.uuid4())"
STATION_ID=00000000-0000-0000-0000-000000000000
```

## Sensor Settings

```bash
# Seconds between sensor readings (5 = efficient, 1 = more granular)
READ_INTERVAL=5

# Seconds per data batch before writing to parquet (900 = 15 minutes)
BATCH_DURATION=900

# Temperature compensation (adjusts for Raspberry Pi CPU heat)
TEMP_COMPENSATION_ENABLED=true
TEMP_COMPENSATION_FACTOR=2.25
```

## Cloud Storage Configuration

### Storage Provider

```bash
# Provider type (s3, backblaze, gcs, wasabi, etc.)
STORAGE_PROVIDER=s3

# S3 endpoint URL (leave empty for AWS S3)
STORAGE_ENDPOINT=https://data.source.coop

# Storage region
STORAGE_REGION=us-west-2
```

### Bucket and Prefix

**Important:** These variables define where your data is uploaded.

#### Source Cooperative Example

```bash
STORAGE_BUCKET=us-west-2.opendata.source.coop
STORAGE_PREFIX=youssef-harby/weather-station-realtime-parquet/parquet
```

Uploads to: `s3://us-west-2.opendata.source.coop/youssef-harby/weather-station-realtime-parquet/parquet/`

#### AWS S3 Example

```bash
STORAGE_BUCKET=my-sensor-bucket
STORAGE_PREFIX=production/station-01/data
```

Uploads to: `s3://my-sensor-bucket/production/station-01/data/`

#### Backblaze B2 Example

```bash
STORAGE_BUCKET=my-backblaze-bucket
STORAGE_PREFIX=sensors/enviroplus/station-01
```

#### Google Cloud Storage Example

```bash
STORAGE_BUCKET=my-gcs-bucket
STORAGE_PREFIX=iot/sensors/weather
```

### Storage Credentials

```bash
# AWS-style credentials (works with S3-compatible services)
AWS_ACCESS_KEY_ID=your-access-key-here
AWS_SECRET_ACCESS_KEY=your-secret-key-here
```

**Note:** For Source Cooperative, Backblaze B2, Wasabi, and other S3-compatible services, use their provided access key and secret key in these fields.

## Sync Configuration

```bash
# Enable/disable automatic cloud sync
SYNC_ENABLED=true

# How often to sync (in minutes)
SYNC_INTERVAL_MINUTES=15
```

## Advanced Configuration

### Custom Output Directory

```bash
# Override default output directory (optional)
# Default: <project-root>/output
OUTPUT_DIR=/custom/path/to/output
```

### Rclone Remote Name

```bash
# Name of rclone remote configuration (optional)
# Default: s3remote
RCLONE_REMOTE=my-custom-remote
```

## Complete Example Configurations

### Minimal (No Sync)

```bash
STATION_ID=a1b2c3d4-e5f6-4789-a0b1-c2d3e4f5a6b7
READ_INTERVAL=5
BATCH_DURATION=900
TEMP_COMPENSATION_ENABLED=true
TEMP_COMPENSATION_FACTOR=2.25
SYNC_ENABLED=false
```

### Source Cooperative (Open Data)

```bash
STATION_ID=a1b2c3d4-e5f6-4789-a0b1-c2d3e4f5a6b7
READ_INTERVAL=5
BATCH_DURATION=900
TEMP_COMPENSATION_ENABLED=true
TEMP_COMPENSATION_FACTOR=2.25

STORAGE_PROVIDER=s3
STORAGE_ENDPOINT=https://data.source.coop
STORAGE_REGION=us-west-2
STORAGE_BUCKET=us-west-2.opendata.source.coop
STORAGE_PREFIX=username/weather-stations/sensor-data

AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

SYNC_ENABLED=true
SYNC_INTERVAL_MINUTES=15
```

### Backblaze B2 (Cost-Effective)

```bash
STATION_ID=a1b2c3d4-e5f6-4789-a0b1-c2d3e4f5a6b7
READ_INTERVAL=5
BATCH_DURATION=900
TEMP_COMPENSATION_ENABLED=true
TEMP_COMPENSATION_FACTOR=2.25

STORAGE_PROVIDER=s3
STORAGE_ENDPOINT=https://s3.us-west-000.backblazeb2.com
STORAGE_REGION=us-west-000
STORAGE_BUCKET=my-b2-bucket
STORAGE_PREFIX=environmental-sensors/station-01

AWS_ACCESS_KEY_ID=<b2-key-id>
AWS_SECRET_ACCESS_KEY=<b2-application-key>

SYNC_ENABLED=true
SYNC_INTERVAL_MINUTES=15
```

### AWS S3 (Production)

```bash
STATION_ID=a1b2c3d4-e5f6-4789-a0b1-c2d3e4f5a6b7
READ_INTERVAL=5
BATCH_DURATION=900
TEMP_COMPENSATION_ENABLED=true
TEMP_COMPENSATION_FACTOR=2.25

STORAGE_PROVIDER=s3
STORAGE_ENDPOINT=
STORAGE_REGION=us-east-1
STORAGE_BUCKET=prod-sensor-data
STORAGE_PREFIX=stations/enviroplus/01

AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

SYNC_ENABLED=true
SYNC_INTERVAL_MINUTES=15
```

## Validation

After editing `config.env`, test your configuration:

```bash
# Test data collection (will run for one batch cycle)
uv run python opensensor_space.py

# Test sync configuration
./sync_to_storage.sh

# Test rclone connection
source config.env
rclone lsd ${RCLONE_REMOTE:-s3remote}:${STORAGE_BUCKET}
```

## Migration from Old Configuration

If migrating from the old `opensensor-space-edge` repository:

| Old | New |
|-----|-----|
| `STATION_ID="01"` | `STATION_ID=<uuid>` (use UUID format) |
| Hardcoded bucket path | `STORAGE_BUCKET` + `STORAGE_PREFIX` |
| `READ_INTERVAL=1` | `READ_INTERVAL=5` (recommended) |
| `BATCH_DURATION=300` | `BATCH_DURATION=900` (15 min) |
| Latitude/Longitude in data | Removed (use UUID instead) |

## Troubleshooting

### Sync fails with "bucket not found"

Check that `STORAGE_BUCKET` and `STORAGE_PREFIX` are correctly set:

```bash
source config.env
echo "Bucket: $STORAGE_BUCKET"
echo "Prefix: $STORAGE_PREFIX"
echo "Full path: ${RCLONE_REMOTE:-s3remote}:${STORAGE_BUCKET}/${STORAGE_PREFIX}"
```

### Invalid credentials

Verify credentials are set:

```bash
source config.env
echo "Access Key: ${AWS_ACCESS_KEY_ID:0:8}..." # Shows first 8 chars
```

### Data not syncing

Check sync is enabled:

```bash
source config.env
echo "Sync enabled: $SYNC_ENABLED"
```

If `SYNC_ENABLED=false`, set it to `true` and restart the sync timer:

```bash
sudo systemctl restart opensensor-sync.timer
```
