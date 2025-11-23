# Enviro+

Designed for environmental monitoring, Enviro+ lets you measure air quality (pollutant gases and particulates), temperature, pressure, humidity, light, and noise level. Learn more - https://shop.pimoroni.com/products/enviro-plus

[![Build Status](https://img.shields.io/github/actions/workflow/status/pimoroni/enviroplus-python/test.yml?branch=main)](https://github.com/pimoroni/enviroplus-python/actions/workflows/test.yml)
[![Coverage Status](https://coveralls.io/repos/github/pimoroni/enviroplus-python/badge.svg?branch=main)](https://coveralls.io/github/pimoroni/enviroplus-python?branch=main)
[![PyPi Package](https://img.shields.io/pypi/v/enviroplus.svg)](https://pypi.python.org/pypi/enviroplus)
[![Python Versions](https://img.shields.io/pypi/pyversions/enviroplus.svg)](https://pypi.python.org/pypi/enviroplus)

---

## 🌍 Join the Open Sensor Network

Want to contribute to open environmental data? Check out [**opensensor.space**](https://opensensor.space/) - a cloud-native platform for streaming sensor data directly to open datasets. Part of the [walkthru.earth](https://walkthru.earth/) initiative for people-first urban intelligence.

**opensensor.space** demonstrates how IoT devices can participate in cloud-native architectures:
- **Minimum carbon footprint** - Edge processing reduces data transmission by 60-90%
- **Open data** - All sensor readings stored in Parquet format on [Source Cooperative](https://source.coop/)
- **Near real-time dashboards** - Query sensor data directly in the browser with DuckDB
- **Resilient** - Offline-first architecture with automatic sync

See live environmental data from Enviro+ sensors at [opensensor.space](https://opensensor.space/)!

---

# Installing

**Note** The code in this repository supports both the Enviro+ and Enviro Mini boards. _The Enviro Mini board does not have the Gas sensor or the breakout for the PM sensor._

![Enviro Plus pHAT](https://raw.githubusercontent.com/pimoroni/enviroplus-python/main/Enviro-Plus-pHAT.jpg)
![Enviro Mini pHAT](https://raw.githubusercontent.com/pimoroni/enviroplus-python/main/Enviro-mini-pHAT.jpg)

:warning: This library now supports Python 3.9+ only. Python 2 is EOL - https://www.python.org/doc/sunset-python-2/

## Quick Start (Debian Trixie/Bookworm)

**Good news!** On modern Raspberry Pi OS (Debian Trixie/Bookworm as of late 2024), I2C, SPI, and serial interfaces work out of the box. Just install and run:

```bash
git clone https://github.com/walkthru-earth/enviroplus-python.git
cd enviroplus-python
./install-uv.sh --with-examples
uv run python examples/weather.py
```

That's it! No manual configuration needed on recent OS versions.

## Installation Methods

### Option 1: Modern Installation with UV (Recommended)

[UV](https://docs.astral.sh/uv/) is an extremely fast Python package manager (10-100x faster than pip) written in Rust:

```bash
git clone https://github.com/walkthru-earth/enviroplus-python.git
cd enviroplus-python
./install-uv.sh --with-examples
```

**Run examples without activating environment:**

```bash
uv run python examples/weather.py
uv run python examples/all-in-one.py
```

**Or activate the environment:**

```bash
source .venv/bin/activate
python examples/weather.py
```

**Installation options:**
- `--with-examples` - Install dependencies for example scripts
- `--with-dev` - Install development tools (ruff, pdoc, etc.)
- `--unstable` - Install from source instead of PyPI
- `--skip-hardware` - Skip hardware configuration (useful for testing)

See [UV_MIGRATION.md](UV_MIGRATION.md) for complete UV usage guide.

### Option 2: Traditional Installation with pip

```bash
git clone https://github.com/walkthru-earth/enviroplus-python.git
cd enviroplus-python
./install.sh
```

**Note:** Libraries will be installed in the "pimoroni" virtual environment:

```bash
source ~/.virtualenvs/pimoroni/bin/activate
python examples/weather.py
```

**Note:** Raspbian/Raspberry Pi OS Lite users may first need to install git: `sudo apt install git`

## Manual Installation from PyPI

For custom setups or containerized environments:

```bash
# Using UV (recommended)
uv venv
uv pip install enviroplus

# Or traditional pip
python3 -m venv .venv
source .venv/bin/activate
pip install enviroplus
```

### Hardware Configuration (Older OS Versions Only)

**Debian Trixie/Bookworm (2024+):** Hardware interfaces work by default - no configuration needed!

**Older versions (Bullseye and earlier):** You may need to manually enable interfaces:

**Enable I2C and SPI:**
```bash
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_spi 0
```

**For PMS5003 Particulate Sensor (Bookworm):**
```bash
sudo raspi-config nonint do_serial_hw 0
sudo raspi-config nonint do_serial_cons 1
echo "dtoverlay=pi3-miniuart-bt" | sudo tee -a /boot/firmware/config.txt
```

**For PMS5003 Particulate Sensor (Bullseye):**
```bash
sudo raspi-config nonint set_config_var enable_uart 1 /boot/config.txt
sudo raspi-config nonint do_serial 1
echo "dtoverlay=pi3-miniuart-bt" | sudo tee -a /boot/config.txt
```

After configuration changes, reboot your Pi.

## Community Projects & Integrations

* **opensensor.space** - https://opensensor.space/ - Cloud-native open sensor network streaming environmental data to open datasets in Parquet format. Part of the [walkthru.earth](https://walkthru.earth/) initiative
* Enviro Plus Dashboard - https://gitlab.com/dedSyn4ps3/enviroplus-dashboard - React-based web dashboard for viewing sensor data
* Enviro+ Example Projects - https://gitlab.com/dedSyn4ps3/enviroplus-python-projects - Includes original examples plus code to stream to Adafruit IO
* enviro monitor - https://github.com/roscoe81/enviro-monitor - Environmental monitoring solution
* mqtt-all - https://github.com/robmarkcole/rpi-enviro-mqtt - MQTT integration (now upstream: [examples/mqtt-all.py](examples/mqtt-all.py))
* enviroplus_exporter - https://github.com/tijmenvandenbrink/enviroplus_exporter - Prometheus exporter with Luftdaten and InfluxDB Cloud support
* homekit-enviroplus - https://github.com/sighmon/homekit-enviroplus - Apple HomeKit accessory for Enviro+
* go-enviroplus - https://github.com/rubiojr/go-enviroplus - Go modules to read Enviro+ sensors
* homebridge-enviroplus - https://github.com/mhawkshaw/homebridge-enviroplus - Homebridge plugin for HomeKit integration
* Enviro Plus Web - https://gitlab.com/idotj/enviroplusweb - Flask application serving web page with current readings and graphs

## Help & Support

* GPIO Pinout - https://pinout.xyz/pinout/enviro_plus
* Support forums - https://forums.pimoroni.com/c/support
* Discord - https://discord.gg/hr93ByC
