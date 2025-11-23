# UV Migration Guide for Enviro+ Python

This guide explains how to use the modern UV package manager with the enviroplus-python project.

## What is UV?

UV is an extremely fast Python package manager written in Rust that's **10-100x faster** than pip. It provides:

- ⚡ Lightning-fast dependency resolution and installation
- 🔒 Universal lockfiles for reproducible installs
- 🎯 Isolated virtual environments
- 🚀 Modern Python project workflow
- 📦 Built-in support for optional dependencies

## Quick Start

### Installation with UV

```bash
# Clone the repository
git clone https://github.com/pimoroni/enviroplus-python
cd enviroplus-python

# Run the UV installer (installs UV if needed, then installs enviroplus)
./install-uv.sh

# Or with optional dependencies
./install-uv.sh --with-examples    # Include example dependencies
./install-uv.sh --with-dev         # Include development tools
```

### Using the Environment

**Option 1: Activate the virtual environment**
```bash
source .venv/bin/activate
python examples/weather.py
```

**Option 2: Use UV run (no activation needed)**
```bash
uv run python examples/weather.py
uv run python examples/all-in-one.py
```

## Installation Options

The `install-uv.sh` script supports several flags:

| Flag | Description |
|------|-------------|
| `--unstable` | Install from source (development version) instead of PyPI |
| `--with-examples` | Install dependencies needed for example scripts |
| `--with-dev` | Install development tools (ruff, pdoc, etc.) |
| `--skip-hardware` | Skip hardware configuration (I2C, SPI, serial) |
| `--help` | Show help message |

### Examples

```bash
# Install stable version with example dependencies
./install-uv.sh --with-examples

# Install development version with all dependencies
./install-uv.sh --unstable --with-examples --with-dev

# Install without configuring hardware (useful for testing)
./install-uv.sh --skip-hardware
```

## Dependency Groups

The project now organizes dependencies into groups using modern PEP 735 dependency-groups:

### Core Dependencies (always installed)
```
gpiod, gpiodevice, pimoroni-bme280, pms5003, ltr559, st7735, ads1015
```

### Optional: Examples
```bash
# Install example dependencies (optional-dependencies)
uv pip install -e ".[examples]"
```

Includes: fonts, font-roboto, astral, pytz, sounddevice, paho-mqtt, pillow

### Optional: Development (PEP 735)
```bash
# Install development tools using dependency-groups
uv sync --group dev
```

Includes: check-manifest, ruff, codespell, isort, twine, hatch, tox, pdoc

### Install Multiple Groups
```bash
# Install examples and dev dependencies
uv pip install -e ".[examples]"
uv sync --group dev
```

## UV Commands Reference

### Environment Management

```bash
# Create a new virtual environment
uv venv

# Create with specific Python version
uv venv --python 3.11

# Remove and recreate
rm -rf .venv && uv venv
```

### Package Management

```bash
# Install the project in editable mode
uv pip install -e .

# Install optional dependencies (examples)
uv pip install -e ".[examples]"

# Install development dependencies (using dependency-groups)
uv sync --group dev

# Install from lockfile (exact versions)
uv pip install -r uv-requirements.lock

# List installed packages
uv pip list

# Show package information
uv pip show enviroplus

# Uninstall a package
uv pip uninstall package-name
```

### Running Code

```bash
# Run without activating environment
uv run python script.py

# Run with arguments
uv run python examples/all-in-one.py --help

# Run any command in the environment
uv run pytest
uv run ruff check
```

### Updating Dependencies

```bash
# Update a specific package
uv pip install --upgrade package-name

# Update all packages
uv pip install --upgrade -e ".[examples]"
uv sync --group dev

# Recreate lockfile
uv pip freeze > uv-requirements.lock
```

## Comparison: UV vs Traditional pip

| Task | Traditional (pip) | Modern (UV) |
|------|------------------|-------------|
| Install package | `pip install enviroplus` | `uv pip install enviroplus` |
| Create venv | `python -m venv .venv` | `uv venv` |
| Run script | `source .venv/bin/activate && python script.py` | `uv run python script.py` |
| Speed | Standard | **10-100x faster** |
| Lockfile | Manual `pip freeze` | Built-in `uv.lock` support |
| Optional deps | Multiple requirements files | Organized in `pyproject.toml` |

## Migration from Old install.sh

If you previously used `./install.sh`:

1. **Old location**: `~/.virtualenvs/pimoroni`
2. **New location**: `.venv` in project directory

The old installation still works! You can use both:

```bash
# Traditional installation
./install.sh

# Modern UV installation
./install-uv.sh
```

To switch from old to new:

```bash
# Deactivate old environment if active
deactivate

# Remove old venv (optional - it won't interfere)
rm -rf ~/.virtualenvs/pimoroni

# Install with UV
./install-uv.sh --with-examples
```

## Reproducible Installations

UV creates `uv-requirements.lock` containing exact package versions:

```bash
# On development machine - create lockfile
uv pip freeze > uv-requirements.lock

# On production/other Pi - install exact versions
uv venv
uv pip install -r uv-requirements.lock
```

This ensures everyone has identical dependencies!

## Hardware Requirements

The installation script configures:

- **I2C**: For BME280 (temperature, pressure, humidity)
- **SPI**: For LCD display (ST7735)
- **Serial**: For PMS5003 particulate sensor

System packages installed:
- `python3-dev`: Python development headers
- `python3-cffi`: C Foreign Function Interface
- `libportaudio2`: Audio library for sound device

## Troubleshooting

### UV not found after installation

```bash
# Add UV to PATH
export PATH="$HOME/.local/bin:$PATH"

# Or restart your shell
exec bash
```

### Permission errors

Don't use `sudo` with UV commands! UV works in user space.

```bash
# Wrong
sudo uv pip install package

# Correct
uv pip install package
```

### Import errors for hardware packages

Make sure you're on a Raspberry Pi with the hardware interfaces enabled:

```bash
# Check if I2C is enabled
ls /dev/i2c-*

# Check if SPI is enabled
ls /dev/spidev*

# Re-run hardware configuration
sudo raspi-config
```

### Package compilation errors

Install required system packages:

```bash
sudo apt update
sudo apt install -y python3-dev python3-cffi libportaudio2
```

## Advanced Usage

### Using UV with GitHub Actions / CI

```yaml
- name: Install UV
  run: curl -LsSf https://astral.sh/uv/install.sh | sh

- name: Install dependencies
  run: |
    uv venv
    uv pip install -e ".[dev]"

- name: Run tests
  run: uv run pytest
```

### Custom Python Version

```bash
# Install specific Python version
uv python install 3.11

# Create venv with that version
uv venv --python 3.11
```

### Offline Installation

```bash
# On connected machine - download packages
uv pip download -r uv-requirements.lock -d packages/

# On offline machine - install from downloads
uv pip install --no-index --find-links packages/ -r uv-requirements.lock
```

## Benefits of UV for This Project

1. **Faster installations**: Critical on Raspberry Pi's slower hardware
2. **Isolated environments**: No conflicts with system Python packages
3. **Better reproducibility**: Lockfile ensures consistent installs
4. **Organized dependencies**: Clear separation of core/examples/dev
5. **Modern workflow**: `uv run` eliminates activation step
6. **Future-proof**: Built on modern Python packaging standards

## Resources

- [UV Documentation](https://docs.astral.sh/uv/)
- [UV GitHub](https://github.com/astral-sh/uv)
- [Enviro+ Repository](https://github.com/pimoroni/enviroplus-python)
- [Pimoroni Shop](https://shop.pimoroni.com/products/enviro)

## Support

- **UV Issues**: https://github.com/astral-sh/uv/issues
- **Enviro+ Issues**: https://github.com/pimoroni/enviroplus-python/issues
- **Pimoroni Forums**: https://forums.pimoroni.com/

---

**Note**: Both `install.sh` (traditional) and `install-uv.sh` (modern) are supported. Choose based on your preference!
