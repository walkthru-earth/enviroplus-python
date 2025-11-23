# Development Guide

Quick guide for contributing to `enviroplus-community`.

## 🚀 Quick Setup

```bash
# 1. Clone repository
git clone https://github.com/walkthru-earth/enviroplus-python.git
cd enviroplus-python

# 2. Create virtual environment and install package
uv venv
source .venv/bin/activate
uv pip install -e .

# 3. Install development dependencies
make dev-deps

# 4. Configure hardware (if on Raspberry Pi)
sudo enviroplus-setup --install
sudo reboot
```

## 📁 Project Structure

```
enviroplus-python/
├── enviroplus/              # Main package
│   ├── __init__.py         # Version info
│   ├── gas.py              # MICS6814 gas sensor
│   ├── noise.py            # Noise measurement
│   ├── setup_tool.py       # Hardware setup command
│   ├── examples_helper.py  # Examples management
│   └── examples/           # Example scripts + icons
├── tests/                  # Unit tests
├── .github/workflows/      # CI/CD pipelines
│   ├── test.yml           # Run tests
│   ├── build.yml          # Build packages
│   ├── qa.yml             # Quality checks
│   └── publish.yml        # Publish to PyPI
├── pyproject.toml          # Package configuration
├── Makefile                # Development tasks
└── README.md               # User documentation
```

## 🛠️ Development Workflow

### Running Tests

```bash
# Run all tests
make pytest

# Run specific test
uv run pytest tests/test_noise.py

# Run with coverage
uv run pytest --cov=enviroplus
```

### Quality Checks

```bash
# Run all QA checks (ruff + codespell)
make qa

# Individual checks
make check          # Basic integrity checks (whitespace, line endings, changelog)
make shellcheck     # Lint shell scripts
uv run ruff check . # Python linting
uv run codespell    # Spell checking
```

### Building Package

```bash
# Clean previous builds
make clean

# Build wheel and sdist
make build

# Built files will be in dist/
ls dist/
# enviroplus_community-1.0.2-py3-none-any.whl
# enviroplus_community-1.0.2.tar.gz
```

### Testing Installation

```bash
# Install from local build
uv pip install dist/enviroplus_community-1.0.2-py3-none-any.whl

# Test commands
enviroplus-setup --check
enviroplus-examples

# Uninstall
uv pip uninstall enviroplus-community
```

## 🔧 Making Changes

### 1. Code Changes

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make your changes
# edit enviroplus/...

# Test changes
make pytest
make qa

# Commit
git add .
git commit -m "feat: add my feature"
```

### 2. Adding Examples

```bash
# Add new example
# Create: enviroplus/examples/my_example.py

# Update examples_helper.py EXAMPLE_INFO dict
# Add entry with description, hardware, dependencies

# Test example
python enviroplus/examples/my_example.py

# Verify it shows in examples list
enviroplus-examples
```

### 3. Updating Dependencies

```bash
# Edit pyproject.toml
# Add to [project.dependencies] or [project.optional-dependencies]

# Reinstall package
uv pip install -e .

# Update lockfile (if using uv.lock)
uv lock
```

## 📦 Release Process

### Version Bump

```bash
# 1. Update version in enviroplus/__init__.py
#    __version__ = "1.0.3"

# 2. Update CHANGELOG.md with changes

# 3. Commit version bump
git add enviroplus/__init__.py CHANGELOG.md
git commit -m "chore: bump version to 1.0.3"
git push origin main
```

### Publishing to PyPI

Publishing is automated via GitHub Actions. See [PYPI_PUBLISHING.md](PYPI_PUBLISHING.md) for details.

```bash
# 1. Create and push tag
git tag v1.0.3
git push origin v1.0.3

# 2. GitHub Actions automatically:
#    - Builds the package
#    - Publishes to PyPI
#    - Creates GitHub Release

# 3. Verify on PyPI
# https://pypi.org/project/enviroplus-community/
```

## 🧪 Testing on Raspberry Pi

### Without Hardware

```bash
# Mock hardware for testing
export ENVIROPLUS_MOCK=1

# Run examples (will use mock data)
python enviroplus/examples/weather.py
```

### With Hardware

```bash
# Check system is configured
enviroplus-setup --check

# Run hardware-dependent tests
pytest tests/ --hardware
```

## 📝 Code Style

We use:
- **ruff** for linting, formatting, and import sorting (replaces Black, isort, flake8)
- **codespell** for spell checking

```bash
# Auto-fix issues
make format
# or manually:
ruff check --fix .
ruff format .

# Check only
make qa
# or manually:
ruff check .
ruff format --check .
codespell
```

## 🐛 Debugging

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Your code here
```

### Common Issues

**I2C/SPI not working:**
```bash
# Check interfaces are enabled
ls /dev/i2c-* /dev/spi*

# Re-run setup
sudo enviroplus-setup --install
sudo reboot
```

**Import errors:**
```bash
# Reinstall in development mode
uv pip install -e .

# Check package is installed
uv pip list | grep enviroplus
```

**Build errors:**
```bash
# Install build tools
uv tool install hatch

# Clean and rebuild
make clean
make build
```

## 📚 Useful Commands

```bash
# Show package version
hatch version

# Show package metadata
hatch project metadata

# List installed dependencies
uv pip list

# Show dependency tree
uv pip tree

# Check outdated packages
uv pip list --outdated

# Format code
ruff format .

# Type checking (if using mypy)
mypy enviroplus/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and QA checks
5. Submit a pull request

### PR Checklist

- [ ] Tests pass (`make pytest`)
- [ ] QA checks pass (`make qa`)
- [ ] Code is formatted (`ruff format .`)
- [ ] Commit messages are clear
- [ ] Documentation updated (if needed)
- [ ] CHANGELOG.md updated (for user-facing changes)

## 💬 Getting Help

- **Issues:** [GitHub Issues](https://github.com/walkthru-earth/enviroplus-python/issues)
- **Discussions:** [GitHub Discussions](https://github.com/walkthru-earth/enviroplus-python/discussions)
- **Email:** yharby@walkthru.earth

---

**Happy coding! 🎉**
