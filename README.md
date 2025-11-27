# Enviro+ Community Edition

![Enviro Plus pHAT](Enviro-Plus-pHAT.jpg)
![Enviro Mini pHAT](Enviro-mini-pHAT.jpg)

**Environmental monitoring for Raspberry Pi** - Measure air quality (gases and particulates), temperature, pressure, humidity, light, and noise.

[![Build Status](https://img.shields.io/github/actions/workflow/status/walkthru-earth/enviroplus-community/test.yml?branch=main)](https://github.com/walkthru-earth/enviroplus-community/actions/workflows/test.yml)
[![PyPI](https://img.shields.io/pypi/v/enviroplus-community.svg)](https://pypi.org/project/enviroplus-community/)
[![Python Versions](https://img.shields.io/pypi/pyversions/enviroplus-community.svg)](https://pypi.org/project/enviroplus-community/)

---

## 🌍 Join the Open Sensor Network

**[opensensor.space](https://opensensor.space/)** is a cloud-native platform for streaming environmental sensor data to open datasets.

Part of the [walkthru.earth](https://walkthru.earth/) initiative for people-first urban intelligence:
- 🌱 **Minimum carbon footprint** - Edge processing reduces transmission by 60-90%
- 📊 **Open data** - All readings stored in Parquet format on [Source Cooperative](https://source.coop/)
- ⚡ **Near real-time** - Query sensor data in the browser with DuckDB
- 🔄 **Resilient** - Offline-first with automatic sync

[**See live data from Enviro+ sensors →**](https://opensensor.space/)

---

## 🚀 Quick Start

### Installation

```bash
# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create isolated environment and install package
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install enviroplus-community

# Check system requirements
enviroplus-setup --check

# Install system dependencies and configure hardware
sudo enviroplus-setup --install

# Reboot (required for hardware changes)
sudo reboot
```

### Run Examples

```bash
# List all available examples
enviroplus-examples

# Get details about a specific example
enviroplus-examples --info weather.py

# Copy examples to your project
enviroplus-examples --copy ~/my-sensors/

# Run an example
uv run python -m enviroplus.examples.weather

# Or run directly (if venv is activated)
python -m enviroplus.examples.weather
```

### Quick Test

```python
import time
from pimoroni_bme280 import BME280

try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus

bme280 = BME280(i2c_dev=SMBus(1))

while True:
    temperature = bme280.get_temperature()
    pressure = bme280.get_pressure()
    humidity = bme280.get_humidity()

    print(f"Temperature: {temperature:.1f}°C")
    print(f"Pressure: {pressure:.1f}hPa")
    print(f"Humidity: {humidity:.1f}%")
    print("---")

    time.sleep(2)
```

---

## 📦 What's Included

### Hardware Support
- **BME280** - Temperature, pressure, humidity
- **LTR559** - Light and proximity
- **MICS6814** - Gas sensor (oxidising, reducing, NH3)
- **PMS5003** - Particulate matter (PM1, PM2.5, PM10)
- **ADAU7002** - MEMS microphone for noise measurement
- **ST7735** - 0.96" color LCD display (160x80)

### Python Package
- Core sensor libraries
- 17 example scripts
- Hardware setup tool (`enviroplus-setup`)
- Examples helper (`enviroplus-examples`)
- Full documentation

### Example Scripts

**Basic Sensors:**
- `weather.py` - Temperature, pressure, humidity
- `light.py` - Light sensor readings
- `gas.py` - Gas sensor readings
- `particulates.py` - Particulate matter readings
- `compensated-temperature.py` - CPU-compensated temperature

**Advanced:**
- `all-in-one.py` - Full dashboard with all sensors
- `mqtt-all.py` - Publish to MQTT broker
- `sensorcommunity.py` - Upload to Sensor.Community network
- `noise-profile.py` - Noise measurement with frequency analysis

[**See all examples →**](https://github.com/walkthru-earth/enviroplus-community/tree/main/enviroplus/examples)

---

## 🛠️ Hardware Setup

The `enviroplus-setup` tool automatically configures your Raspberry Pi:

```bash
# Check what's needed
enviroplus-setup --check

# Install and configure everything
sudo enviroplus-setup --install
```

**What it does:**
- ✅ Installs system packages (`python3-cffi`, `libportaudio2`)
- ✅ Enables I2C interface (for sensors)
- ✅ Enables SPI interface (for LCD display)
- ✅ Configures serial/UART (for PMS5003 sensor)
- ✅ Adds device tree overlays to `/boot/firmware/config.txt`
- ✅ Creates backup before changes

**Note:** A reboot is required after hardware configuration.

---

## 📖 Documentation

- **Installation Guide:** See above
- **Example Scripts:** [enviroplus/examples/](enviroplus/examples/)
- **API Reference:** Use `enviroplus-examples --info <script>` for details
- **Hardware Setup:** Run `enviroplus-setup --help`
- **Publishing Guide:** [PYPI_PUBLISHING.md](PYPI_PUBLISHING.md)
- **Development:** [DEVELOPMENT.md](DEVELOPMENT.md)

---

## 🤝 Community Projects & Integrations

Amazing projects built by the community using Enviro+:

### Cloud & IoT Platforms
- **[opensensor.space](https://opensensor.space/)** - Cloud-native open sensor network with edge processing and open data (walkthru.earth)
- **[enviroplus_exporter](https://github.com/tijmenvandenbrink/enviroplus_exporter)** - Prometheus exporter with Luftdaten and InfluxDB Cloud support
- **[mqtt-all](https://github.com/robmarkcole/rpi-enviro-mqtt)** - MQTT integration (now upstream in [examples/mqtt-all.py](enviroplus/examples/mqtt-all.py))
- **[sensorcommunity](https://sensor.community/)** - Upload data to Sensor.Community (Luftdaten) network

### Web Dashboards
- **[Enviro Plus Dashboard](https://gitlab.com/dedSyn4ps3/enviroplus-dashboard)** - React-based web dashboard for viewing sensor data
- **[Enviro Plus Web](https://gitlab.com/idotj/enviroplusweb)** - Flask application serving web pages with current readings and graphs
- **[enviro monitor](https://github.com/roscoe81/enviro-monitor)** - Comprehensive environmental monitoring solution

### Home Automation
- **[homekit-enviroplus](https://github.com/sighmon/homekit-enviroplus)** - Apple HomeKit accessory for Enviro+
- **[homebridge-enviroplus](https://github.com/mhawkshaw/homebridge-enviroplus)** - Homebridge plugin for HomeKit integration

### Development Libraries
- **[go-enviroplus](https://github.com/rubiojr/go-enviroplus)** - Go modules to read Enviro+ sensors
- **[Enviro+ Example Projects](https://gitlab.com/dedSyn4ps3/enviroplus-community-projects)** - Includes original examples plus code to stream to Adafruit IO

**Got a project?** [Add it here →](https://github.com/walkthru-earth/enviroplus-community/issues)

---

## 🆘 Help & Support

Need help getting started or troubleshooting?

### Documentation
- **Installation Guide:** See Quick Start above
- **Hardware Setup:** Run `enviroplus-setup --help`
- **Examples:** Run `enviroplus-examples` to see all available examples
- **API Reference:** Run `enviroplus-examples --info <script>` for details
- **GPIO Pinout:** [pinout.xyz/enviro_plus](https://pinout.xyz/pinout/enviro_plus)

### Get Help
- **GitHub Issues:** [Report bugs or request features](https://github.com/walkthru-earth/enviroplus-community/issues)
- **GitHub Discussions:** [Ask questions and share ideas](https://github.com/walkthru-earth/enviroplus-community/discussions)
- **Pimoroni Forums:** [Community support](https://forums.pimoroni.com/c/support)
- **Discord:** [Join the conversation](https://discord.gg/hr93ByC)
- **Email:** yharby@walkthru.earth (for opensensor.space integration)

### Useful Links
- **Enviro+ Product:** [shop.pimoroni.com/products/enviro-plus](https://shop.pimoroni.com/products/enviro-plus)
- **Getting Started Guide:** [learn.pimoroni.com/enviro-plus](https://learn.pimoroni.com/article/getting-started-with-enviro-plus)
- **opensensor.space:** [opensensor.space](https://opensensor.space/)
- **walkthru.earth:** [walkthru.earth](https://walkthru.earth/)

---

## 🔧 Development

Want to contribute? See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed setup instructions.

```bash
# Clone repository
git clone https://github.com/walkthru-earth/enviroplus-community.git
cd enviroplus-community

# Create isolated environment
uv venv
source .venv/bin/activate

# Install for development
uv pip install -e .

# Install dev dependencies
make dev-deps

# Run tests
make pytest

# Run QA checks
make qa

# Build package
make build
```

---

## 📋 Requirements

- **Hardware:** Raspberry Pi with Enviro+ or Enviro Mini pHAT
- **OS:** Raspberry Pi OS (Debian Bookworm or later recommended)
- **Python:** 3.9 - 3.13 (fully tested across all versions)
- **System packages:** Automatically installed by `enviroplus-setup`

**Supported boards:**
- Enviro+ (all sensors)
- Enviro Mini (no gas sensor or PM sensor)

---

## 📜 License

MIT License - see [LICENSE](LICENSE)

**Original Author:** Philip Howard (Pimoroni)
**Maintained by:** Youssef Harby ([walkthru.earth](https://walkthru.earth/))

---

## 🙏 Acknowledgments

- **Pimoroni** for creating the Enviro+ hardware and original library
- **walkthru.earth** for opensensor.space integration
- **Community contributors** for examples and integrations

---

**Made with ❤️ for open environmental data**
