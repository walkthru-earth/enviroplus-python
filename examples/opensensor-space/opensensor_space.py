#!/usr/bin/env python3

"""
OpenSensor Space - Modern sensor data collection with DuckDB
Collects environmental sensor data and stores it efficiently in partitioned Parquet files
using DuckDB for optimal memory usage and storage efficiency.
"""

import time
import datetime
import duckdb
import os
import sys
from pathlib import Path

# Load configuration from config.env
try:
    from dotenv import load_dotenv
    script_dir = Path(__file__).parent
    config_file = script_dir / "config.env"

    if config_file.exists():
        load_dotenv(config_file)
        print(f"Loaded configuration from {config_file}")
    else:
        print(f"Warning: Configuration file not found: {config_file}")
        print("Using default values. Run install.sh to create configuration.")
except ImportError:
    print("Warning: python-dotenv not installed. Using default values.")
    script_dir = Path(__file__).parent

# Import sensor libraries
from enviroplus import gas
from bme280 import BME280

# Optional: Light sensor (LTR559) and particulate sensor (PMS5003)
try:
    from ltr559 import LTR559
    ltr559_sensor = LTR559()
except ImportError:
    ltr559_sensor = None

# Handle PMS5003 sensor - gracefully handle if it's broken
try:
    from pms5003 import PMS5003, ReadTimeoutError
    pms5003 = PMS5003()
    print("PMS5003 sensor initialized successfully")
except Exception as e:
    print(f"Warning: PMS5003 sensor initialization failed: {e}")
    print("Continuing without particulate matter sensor")
    pms5003 = None

# --- Configuration from environment variables ---
SENSOR_CONFIG = {
    'bme280': True,   # temperature, pressure, humidity
    'gas': True,      # oxidised, reducing, nh3
    'ltr559': True,   # lux, proximity
    'pms5003': True   # pm1, pm2.5, pm10 (set to True if sensor is connected)
}

# Read from config.env or use defaults
READ_INTERVAL = int(os.getenv('READ_INTERVAL', '5'))        # seconds between sensor reads
BATCH_DURATION = int(os.getenv('BATCH_DURATION', '900'))    # seconds for each batch - 15 minutes
STATION_ID = os.getenv('STATION_ID', '00000000-0000-0000-0000-000000000000')  # UUID format

# Temperature compensation settings
TEMP_COMPENSATION_ENABLED = os.getenv('TEMP_COMPENSATION_ENABLED', 'true').lower() == 'true'
TEMP_COMPENSATION_FACTOR = float(os.getenv('TEMP_COMPENSATION_FACTOR', '2.25'))
cpu_temps = []  # List to store CPU temperature history for smoothing

# Output directory (relative to script location or absolute)
OUTPUT_DIR = os.getenv('OUTPUT_DIR', str(script_dir.parent.parent / 'output'))

# --- Sensor Initialization ---
if SENSOR_CONFIG.get('bme280'):
    from smbus2 import SMBus
    bus = SMBus(1)
    bme280 = BME280(i2c_dev=bus)

if SENSOR_CONFIG.get('gas'):
    gas.enable_adc()       # Enable ADC for gas sensor
    gas.set_adc_gain(4.096)  # Set ADC gain as appropriate

# --- Helper Functions ---
def get_cpu_temperature():
    """
    Get the CPU temperature for compensating BME280 temperature readings.
    """
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp = f.read()
            temp = int(temp) / 1000.0
        return temp
    except (IOError, ValueError):
        # Return a safe default if we can't read the CPU temperature
        return 40.0

def compensate_temperature(raw_temp):
    """
    Compensate temperature reading from BME280 using CPU temperature.
    Method adapted from Initial State's Enviro pHAT review.
    """
    global cpu_temps

    if not TEMP_COMPENSATION_ENABLED:
        return raw_temp

    # Get current CPU temperature
    cpu_temp = get_cpu_temperature()

    # Initialize the list if it's empty
    if len(cpu_temps) == 0:
        cpu_temps = [cpu_temp] * 5
    else:
        # Smooth out with some averaging to decrease jitter
        cpu_temps = cpu_temps[1:] + [cpu_temp]

    # Calculate the average CPU temperature
    avg_cpu_temp = sum(cpu_temps) / float(len(cpu_temps))

    # Apply compensation formula
    comp_temp = raw_temp - ((avg_cpu_temp - raw_temp) / TEMP_COMPENSATION_FACTOR)

    return comp_temp

# --- Sensor Reading Function ---
def read_sensors():
    """
    Reads data from the enabled sensors and returns a dict with a timestamp.
    """
    data = {}
    # Current UTC time
    current_time = datetime.datetime.now(datetime.timezone.utc)

    # Store timestamp as ISO format string for DuckDB
    data['timestamp'] = current_time.isoformat()

    if SENSOR_CONFIG.get('bme280'):
        raw_temp = bme280.get_temperature()
        data['temperature'] = compensate_temperature(raw_temp)
        data['raw_temperature'] = raw_temp  # Store the raw value as well
        data['pressure'] = bme280.get_pressure()
        data['humidity'] = bme280.get_humidity()

    if SENSOR_CONFIG.get('gas'):
        gas_data = gas.read_all()
        # Convert raw sensor values (e.g. in ohms) to kilo-ohms
        data['oxidised'] = gas_data.oxidising / 1000.0
        data['reducing'] = gas_data.reducing / 1000.0
        data['nh3'] = gas_data.nh3 / 1000.0

    if SENSOR_CONFIG.get('ltr559') and ltr559_sensor:
        data['lux'] = ltr559_sensor.get_lux()
        data['proximity'] = ltr559_sensor.get_proximity()

    if SENSOR_CONFIG.get('pms5003') and pms5003:
        try:
            pm_readings = pms5003.read()
            # Standard PM measurements
            data['pm1'] = float(pm_readings.pm_ug_per_m3(1.0))
            data['pm2_5'] = float(pm_readings.pm_ug_per_m3(2.5))
            data['pm10'] = float(pm_readings.pm_ug_per_m3(10.0))
            # Particle counts - using the correct attribute names
            data['particles_03um'] = float(pm_readings.pm_per_1l_air(0.3))
            data['particles_05um'] = float(pm_readings.pm_per_1l_air(0.5))
            data['particles_10um'] = float(pm_readings.pm_per_1l_air(1.0))
            data['particles_25um'] = float(pm_readings.pm_per_1l_air(2.5))
            data['particles_50um'] = float(pm_readings.pm_per_1l_air(5.0))
            data['particles_100um'] = float(pm_readings.pm_per_1l_air(10.0))
        except (ReadTimeoutError, ValueError) as e:
            print(f"Warning: PMS5003 read error: {e}")
            # Set all PM-related fields to None in case of timeout or value error
            for field in ['pm1', 'pm2_5', 'pm10',
                         'particles_03um', 'particles_05um', 'particles_10um',
                         'particles_25um', 'particles_50um', 'particles_100um']:
                data[field] = None

    return data

# --- Main Loop ---
def main():
    print("Starting sensor data collection using DuckDB. Press Ctrl+C to stop.")
    print(f"Configuration: READ_INTERVAL={READ_INTERVAL}s, BATCH_DURATION={BATCH_DURATION}s (15 minutes)")

    batch_data = []       # List to accumulate sensor readings for the current batch

    # Calculate time to the next 15-minute boundary
    now = datetime.datetime.now(datetime.timezone.utc)
    # Calculate seconds to next 15-minute boundary
    minutes_to_add = 15 - (now.minute % 15)
    if minutes_to_add == 15 and now.second == 0:  # If we're exactly at a 15-minute boundary
        seconds_to_next_15min = 0
    else:
        seconds_to_next_15min = (minutes_to_add * 60) - now.second

    # Adjust batch duration to align with 15-minute boundary for the first batch
    first_batch_duration = seconds_to_next_15min if seconds_to_next_15min > 0 else BATCH_DURATION

    print(f"First batch will run for {first_batch_duration} seconds to align with 15-minute boundary")
    batch_start = time.time()
    next_batch_end = batch_start + first_batch_duration

    try:
        while True:
            sensor_data = read_sensors()
            batch_data.append(sensor_data)

            current_time = time.time()
            time_to_next_batch = max(0, next_batch_end - current_time)

            # Check if it's time to write out the batch
            if current_time >= next_batch_end:
                # Get the batch end time for the filename (this is when the data collection period ended)
                batch_end_dt = datetime.datetime.fromtimestamp(next_batch_end, datetime.timezone.utc)
                # Round to the nearest 15-minute boundary for the timestamp
                rounded_minute = 15 * (batch_end_dt.minute // 15)
                rounded_dt = batch_end_dt.replace(minute=rounded_minute, second=0, microsecond=0)

                # Extract date components for partitioning
                year = rounded_dt.strftime('%Y')
                month = rounded_dt.strftime('%m')
                day = rounded_dt.strftime('%d')
                hour = rounded_dt.strftime('%H')
                minute = rounded_dt.strftime('%M')

                # Create a DuckDB in-memory database for this batch
                con = duckdb.connect(database=':memory:')

                # Create partitioned output directory structure
                output_base = Path(OUTPUT_DIR)
                output_base.mkdir(parents=True, exist_ok=True)

                # Use DuckDB's COPY with PARTITION_BY for efficient partitioned writes
                # DuckDB can directly query Python variables (lists of dicts)
                partition_query = f"""
                    COPY (
                        SELECT
                            timestamp::TIMESTAMP AS timestamp,
                            temperature,
                            raw_temperature,
                            pressure,
                            humidity,
                            oxidised,
                            reducing,
                            nh3,
                            lux,
                            proximity,
                            pm1,
                            pm2_5,
                            pm10,
                            particles_03um,
                            particles_05um,
                            particles_10um,
                            particles_25um,
                            particles_50um,
                            particles_100um,
                            '{STATION_ID}' AS station,
                            year(timestamp::TIMESTAMP) AS year,
                            month(timestamp::TIMESTAMP) AS month,
                            day(timestamp::TIMESTAMP) AS day,
                            hour(timestamp::TIMESTAMP) AS hour,
                            (minute(timestamp::TIMESTAMP) / 15) * 15 AS minute_bucket
                        FROM batch_data
                    ) TO '{str(output_base)}' (
                        FORMAT PARQUET,
                        PARTITION_BY (station, year, month, day, hour, minute_bucket),
                        OVERWRITE_OR_IGNORE,
                        FILENAME_PATTERN 'data_{{i}}',
                        COMPRESSION 'snappy'
                    )
                """

                con.execute(partition_query)

                records_written = len(batch_data)
                partition_path = f"station={STATION_ID}/year={year}/month={month}/day={day}/hour={hour}/minute_bucket={minute}"
                print(f"Wrote {records_written} records to {output_base}/{partition_path}/")

                # Close the connection
                con.close()

                # Reset the batch data for the next cycle
                batch_data = []

                # Set the next batch end time to align with 15-minute boundaries
                next_batch_end = next_batch_end + BATCH_DURATION
                # Ensure we're aligned to 15-minute boundaries
                current_dt = datetime.datetime.fromtimestamp(next_batch_end, datetime.timezone.utc)
                # Calculate seconds to the next 15-minute boundary
                minutes_to_add = 15 - (current_dt.minute % 15)
                if minutes_to_add == 15 and current_dt.second == 0:  # If we're exactly at a 15-minute boundary
                    pass  # No adjustment needed
                else:
                    # Adjust to the next 15-minute boundary
                    seconds_to_add = (minutes_to_add * 60) - current_dt.second
                    next_batch_end += seconds_to_add

            # Sleep until next reading or end of batch, whichever comes first
            sleep_time = min(READ_INTERVAL, time_to_next_batch)
            if sleep_time > 0:
                time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\nStopping sensor data collection.")
        if batch_data:
            print(f"Warning: {len(batch_data)} records in current batch were not written to disk.")

if __name__ == '__main__':
    main()
