1.0.2
-----

### Community Edition Updates
* **Package renamed** to `enviroplus-community` for PyPI distribution
* **Python 3.12 and 3.13** support added and fully tested
* **Modern packaging** with UV package manager and PEP 735 dependency groups
* **New tools**: `enviroplus-setup` for hardware configuration, `enviroplus-examples` for examples management
* **CI/CD modernization**: GitHub Actions with ruff, UV, and Trusted Publishers for PyPI
* **Code quality**: Migrated to ruff for linting/formatting (replaces black, isort, flake8)
* **Documentation**: Comprehensive guides for development and PyPI publishing
* **opensensor.space integration**: Cloud-native platform for open sensor data
* README.md: Update install instructions
* Fix installer to enable serial
* Fix gas sensor heater pin

1.0.1
-----

* README.md: Fix images

1.0.0
-----

* BREAKING: Port to gpiod/gpiodevice for Pi 5/Bookworm.

0.0.6
-----

* Fix noise by specifying adau7002 device

0.0.5
-----

* Drop Python 2.x support
* Add "available()" method for gas sensor

0.0.4
-----

* Add support for ads1015 >= v0.0.7 (ADS1115 ADCs)
* Packaging tweaks

0.0.3
-----

* Fix "self.noise_floor" bug in get_noise_profile

0.0.2
-----

* Add support for extra ADC channel in Gas
* Handle breaking change in new ltr559 library
* Add Noise functionality

0.0.1
-----

* Initial Release
