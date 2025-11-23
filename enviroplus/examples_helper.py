#!/usr/bin/env python3
"""
Enviro+ Examples Helper

This tool helps you find, explore, and copy example scripts after installing enviroplus.

Usage:
    enviroplus-examples                    # List all examples
    enviroplus-examples --info weather.py  # Show info about an example
    enviroplus-examples --copy ~/my-dir/   # Copy all examples to directory
    enviroplus-examples --path             # Show examples directory path
"""

import argparse
import shutil
import sys
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output"""

    GREEN = "\033[0;32m"
    CYAN = "\033[0;36m"
    YELLOW = "\033[0;33m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def success(msg):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {msg}{Colors.RESET}")


def info(msg):
    """Print info message"""
    print(f"{Colors.CYAN}{msg}{Colors.RESET}")


def warning(msg):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.RESET}")


def get_examples_dir():
    """
    Find the examples directory in the installed package

    Returns:
        Path object or None if not found
    """
    # Try to find examples relative to this module
    module_dir = Path(__file__).parent
    examples_dir = module_dir / "examples"

    if examples_dir.exists():
        return examples_dir

    # Try alternate location (if installed differently)
    package_dir = module_dir.parent
    examples_dir = package_dir / "examples"

    if examples_dir.exists():
        return examples_dir

    return None


# Example descriptions
EXAMPLE_INFO = {
    "weather.py": {"description": "Simple temperature, pressure, and humidity readings from BME280", "hardware": ["BME280 sensor"], "dependencies": []},
    "light.py": {"description": "Light sensor readings from LTR559", "hardware": ["LTR559 light sensor"], "dependencies": []},
    "gas.py": {"description": "Gas sensor readings (oxidising, reducing, NH3) from MICS6814", "hardware": ["MICS6814 gas sensor", "ADS1015 ADC"], "dependencies": []},
    "particulates.py": {"description": "Particulate matter readings (PM1, PM2.5, PM10) from PMS5003", "hardware": ["PMS5003 particulate sensor"], "dependencies": []},
    "compensated-temperature.py": {"description": "CPU-compensated temperature reading (corrects for CPU heat)", "hardware": ["BME280 sensor"], "dependencies": []},
    "adc.py": {"description": "Raw analog-to-digital converter readings", "hardware": ["ADS1015 ADC"], "dependencies": []},
    "noise-profile.py": {"description": "Noise measurement with frequency profile (low/mid/high)", "hardware": ["ADAU7002 microphone"], "dependencies": ["sounddevice"]},
    "noise-amps-at-freqs.py": {"description": "Noise amplitude at specific frequencies", "hardware": ["ADAU7002 microphone"], "dependencies": ["sounddevice"]},
    "lcd.py": {"description": "Basic ST7735 LCD display test", "hardware": ["ST7735 LCD"], "dependencies": ["pillow", "fonts"]},
    "all-in-one.py": {
        "description": "Full-featured display with all sensors (Enviro+ with PM sensor)",
        "hardware": ["All Enviro+ sensors", "ST7735 LCD", "PMS5003"],
        "dependencies": ["pillow", "fonts", "font-roboto"],
    },
    "all-in-one-no-pm.py": {
        "description": "All sensors display except particulate matter",
        "hardware": ["All Enviro+ sensors except PMS5003", "ST7735 LCD"],
        "dependencies": ["pillow", "fonts", "font-roboto"],
    },
    "all-in-one-enviro-mini.py": {"description": "For Enviro Mini (no gas sensor or PM sensor)", "hardware": ["BME280", "LTR559", "ST7735 LCD"], "dependencies": ["pillow", "fonts", "font-roboto"]},
    "weather-and-light.py": {
        "description": "Weather display with day/night icons based on light levels",
        "hardware": ["BME280", "LTR559", "ST7735 LCD"],
        "dependencies": ["pillow", "fonts", "astral", "pytz"],
    },
    "combined.py": {"description": "Combined sensor readings with LCD display", "hardware": ["Multiple sensors", "ST7735 LCD"], "dependencies": ["pillow", "fonts"]},
    "mqtt-all.py": {"description": "Publish all sensor data to MQTT broker", "hardware": ["All Enviro+ sensors"], "dependencies": ["paho-mqtt"]},
    "sensorcommunity.py": {"description": "Upload data to Sensor.Community (Luftdaten) network", "hardware": ["BME280", "PMS5003"], "dependencies": []},
    "sensorcommunity_combined.py": {"description": "Enhanced Sensor.Community integration with additional data", "hardware": ["All Enviro+ sensors"], "dependencies": []},
}


def list_examples():
    """List all available examples with descriptions"""
    examples_dir = get_examples_dir()

    if not examples_dir:
        warning("Could not find examples directory")
        print("\nThis usually means examples were not included in your installation.")
        print("You can find examples at: https://github.com/pimoroni/enviroplus-python/tree/main/examples")
        return False

    print(f"\n{Colors.BOLD}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}  Enviro+ Example Scripts{Colors.RESET}")
    print(f"{Colors.BOLD}{'=' * 70}{Colors.RESET}\n")

    info(f"Examples location: {examples_dir}\n")

    # Get all Python files
    example_files = sorted(examples_dir.glob("*.py"))

    if not example_files:
        warning("No example files found")
        return False

    print(f"{Colors.BOLD}Basic Sensor Examples:{Colors.RESET}")
    basic_examples = ["weather.py", "light.py", "gas.py", "particulates.py", "compensated-temperature.py", "adc.py"]

    for example in basic_examples:
        example_path = examples_dir / example
        if example_path.exists():
            desc = EXAMPLE_INFO.get(example, {}).get("description", "No description")
            print(f"  {Colors.GREEN}{example:<30}{Colors.RESET} {desc}")

    print(f"\n{Colors.BOLD}Noise Measurement Examples:{Colors.RESET}")
    noise_examples = ["noise-profile.py", "noise-amps-at-freqs.py"]

    for example in noise_examples:
        example_path = examples_dir / example
        if example_path.exists():
            desc = EXAMPLE_INFO.get(example, {}).get("description", "No description")
            deps = EXAMPLE_INFO.get(example, {}).get("dependencies", [])
            deps_str = f" [requires: {', '.join(deps)}]" if deps else ""
            print(f"  {Colors.GREEN}{example:<30}{Colors.RESET} {desc}{deps_str}")

    print(f"\n{Colors.BOLD}Display Examples:{Colors.RESET}")
    display_examples = ["lcd.py", "all-in-one.py", "all-in-one-no-pm.py", "all-in-one-enviro-mini.py", "weather-and-light.py", "combined.py"]

    for example in display_examples:
        example_path = examples_dir / example
        if example_path.exists():
            desc = EXAMPLE_INFO.get(example, {}).get("description", "No description")
            deps = EXAMPLE_INFO.get(example, {}).get("dependencies", [])
            deps_str = f" [requires: {', '.join(deps)}]" if deps else ""
            print(f"  {Colors.GREEN}{example:<30}{Colors.RESET} {desc}{deps_str}")

    print(f"\n{Colors.BOLD}Integration Examples:{Colors.RESET}")
    integration_examples = ["mqtt-all.py", "sensorcommunity.py", "sensorcommunity_combined.py"]

    for example in integration_examples:
        example_path = examples_dir / example
        if example_path.exists():
            desc = EXAMPLE_INFO.get(example, {}).get("description", "No description")
            deps = EXAMPLE_INFO.get(example, {}).get("dependencies", [])
            deps_str = f" [requires: {', '.join(deps)}]" if deps else ""
            print(f"  {Colors.GREEN}{example:<30}{Colors.RESET} {desc}{deps_str}")

    # Icons directory
    icons_dir = examples_dir / "icons"
    if icons_dir.exists():
        icon_count = len(list(icons_dir.glob("*.png")))
        print(f"\n{Colors.BOLD}Icons:{Colors.RESET}")
        print(f"  {icon_count} PNG icons for display examples")

    print(f"\n{Colors.BOLD}Usage:{Colors.RESET}")
    print(f"  python {examples_dir / 'weather.py'}")
    print(f"  python {examples_dir / 'all-in-one.py'}")
    print(f"\n{Colors.BOLD}More info:{Colors.RESET}")
    print("  enviroplus-examples --info weather.py")
    print("  enviroplus-examples --copy ~/my-sensors/")

    print(f"\n{Colors.BOLD}Install example dependencies:{Colors.RESET}")
    print("  pip install enviroplus[examples]")

    print(f"\n{Colors.BOLD}{'=' * 70}{Colors.RESET}\n")

    return True


def show_example_info(example_name):
    """Show detailed information about a specific example"""
    examples_dir = get_examples_dir()

    if not examples_dir:
        warning("Could not find examples directory")
        return False

    example_path = examples_dir / example_name

    if not example_path.exists():
        warning(f"Example not found: {example_name}")
        print("\nAvailable examples:")
        for f in sorted(examples_dir.glob("*.py")):
            print(f"  - {f.name}")
        return False

    info_data = EXAMPLE_INFO.get(example_name, {})

    print(f"\n{Colors.BOLD}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}  {example_name}{Colors.RESET}")
    print(f"{Colors.BOLD}{'=' * 70}{Colors.RESET}\n")

    print(f"{Colors.BOLD}Description:{Colors.RESET}")
    print(f"  {info_data.get('description', 'No description available')}\n")

    print(f"{Colors.BOLD}Location:{Colors.RESET}")
    print(f"  {example_path}\n")

    if info_data.get("hardware"):
        print(f"{Colors.BOLD}Required Hardware:{Colors.RESET}")
        for hw in info_data["hardware"]:
            print(f"  - {hw}")
        print()

    if info_data.get("dependencies"):
        print(f"{Colors.BOLD}Python Dependencies:{Colors.RESET}")
        for dep in info_data["dependencies"]:
            print(f"  - {dep}")
        print("\nInstall with: pip install enviroplus[examples]")
        print()

    print(f"{Colors.BOLD}Run:{Colors.RESET}")
    print(f"  python {example_path}")

    # Show first few lines of the file
    try:
        with open(example_path, "r") as f:
            lines = f.readlines()[:20]

        print(f"\n{Colors.BOLD}Preview:{Colors.RESET}")
        for line in lines:
            print(f"  {line.rstrip()}")
        if len(f.readlines()) > 20:
            print("  ...")

    except Exception as e:
        warning(f"Could not read file: {e}")

    print(f"\n{Colors.BOLD}{'=' * 70}{Colors.RESET}\n")

    return True


def copy_examples(destination):
    """Copy all examples to a destination directory"""
    examples_dir = get_examples_dir()

    if not examples_dir:
        warning("Could not find examples directory")
        return False

    dest_path = Path(destination).expanduser().resolve()

    # Create destination if it doesn't exist
    if not dest_path.exists():
        info(f"Creating directory: {dest_path}")
        dest_path.mkdir(parents=True, exist_ok=True)
    elif not dest_path.is_dir():
        warning(f"Destination is not a directory: {dest_path}")
        return False

    print(f"\n{Colors.BOLD}Copying examples...{Colors.RESET}\n")
    info(f"From: {examples_dir}")
    info(f"To:   {dest_path}\n")

    copied_count = 0

    # Copy Python files
    for example_file in examples_dir.glob("*.py"):
        dest_file = dest_path / example_file.name
        shutil.copy2(example_file, dest_file)
        print(f"  {Colors.GREEN}✓{Colors.RESET} {example_file.name}")
        copied_count += 1

    # Copy icons directory
    icons_src = examples_dir / "icons"
    if icons_src.exists():
        icons_dest = dest_path / "icons"
        if icons_dest.exists():
            shutil.rmtree(icons_dest)
        shutil.copytree(icons_src, icons_dest)
        icon_count = len(list(icons_dest.glob("*.png")))
        print(f"  {Colors.GREEN}✓{Colors.RESET} icons/ ({icon_count} files)")

    print()
    success(f"Copied {copied_count} examples to {dest_path}")
    print()

    return True


def show_path():
    """Show the path to the examples directory"""
    examples_dir = get_examples_dir()

    if not examples_dir:
        warning("Could not find examples directory")
        return False

    print(examples_dir)
    return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Enviro+ Examples Helper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  enviroplus-examples                    List all examples
  enviroplus-examples --info weather.py  Show details about weather.py
  enviroplus-examples --copy ~/sensors/  Copy examples to ~/sensors/
  enviroplus-examples --path             Print examples directory path

For more information:
  https://github.com/pimoroni/enviroplus-python
        """,
    )

    parser.add_argument("--list", action="store_true", help="List all examples (default action)")

    parser.add_argument("--info", metavar="EXAMPLE", help="Show detailed information about a specific example")

    parser.add_argument("--copy", metavar="DESTINATION", help="Copy all examples to specified directory")

    parser.add_argument("--path", action="store_true", help="Show the path to the examples directory")

    args = parser.parse_args()

    # Default to list if no action specified
    if not any([args.info, args.copy, args.path]):
        args.list = True

    try:
        if args.info:
            success_result = show_example_info(args.info)
        elif args.copy:
            success_result = copy_examples(args.copy)
        elif args.path:
            success_result = show_path()
        else:
            success_result = list_examples()

        sys.exit(0 if success_result else 1)

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        warning(f"Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
