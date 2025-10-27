# tinySA Ultra - Local Oscillator Power Characterization

Automated power measurement system for characterizing ADF4351-based Local Oscillator output power across frequency sweeps using the tinySA Ultra spectrum analyzer.

## Project Structure

```
tinysa-lo-characterization/
├── controllers/           # Hardware interface modules
│   ├── arduino_controller.py    # Arduino/ADF4351 serial interface
│   └── tinysa_controller.py     # tinySA Ultra measurement wrapper
├── scripts/              # Executable scripts
│   ├── lo_power_sweep.py        # Main automated measurement
│   ├── test_lo_sweep.py         # Visual sweep test (no measurements)
│   └── test_system.py           # Hardware connectivity test
├── utils/                # Utilities
│   └── plot_results.py          # Data visualization
├── results/              # Output data directory
├── config.yaml           # Default configuration
├── examples.py           # Usage examples
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Overview

This project automates the measurement of LO output power at 301 frequency points (900-960 MHz, 0.2 MHz steps) by coordinating:
- **Arduino/ADF4351**: Generates RF signal at commanded frequency
- **tinySA Ultra**: Measures peak power at that frequency
- **Python Controller**: Orchestrates the measurement sequence and data collection

## Hardware Setup

```
┌─────────────┐      USB       ┌──────────────┐
│   Arduino   │◄──────────────►│              │
│  + ADF4351  │                │   Computer   │
│     (LO)    │                │  (Python)    │
└──────┬──────┘                │              │
       │ RF Cable/             │              │
       │ Connector             │              │
       ▼                   USB │              │
┌─────────────┐◄───────────────┤              │
│ tinySA Ultra│                └──────────────┘
│  (Spectrum  │
│  Analyzer)  │
└─────────────┘
```

### Connections:
1. **Arduino to Computer**: USB serial connection (for frequency commands)
2. **tinySA to Computer**: USB serial connection (for power measurements)
3. **LO to tinySA**: RF cable from ADF4351 output to tinySA input

## Requirements

```bash
pip install tsapython pyserial numpy pandas
```

Optional for FITS file support:
```bash
pip install astropy
```

## Arduino Preparation

Upload the `ManualControl.ino` sketch from the `adf4351-controller` repository to your Arduino. This sketch accepts serial commands to set frequencies.

### Key Commands:
- `f <frequency>`: Set frequency in MHz (e.g., `f 900.0`)
- `p <power>`: Set output power in dBm (e.g., `p +5` or `p -4`)
- `s`: Print current status

## Usage

### Basic Power Sweep

```bash
python scripts/lo_power_sweep.py --arduino /dev/cu.usbserial-14110 --tinysa auto --output power_sweep.csv
```

### With Custom Parameters

```bash
python scripts/lo_power_sweep.py \
    --arduino /dev/cu.usbserial-14110 \
    --tinysa /dev/cu.usbserial-23456 \
    --freq-start 900.0 \
    --freq-stop 960.0 \
    --freq-step 0.2 \
    --power +5 \
    --settling-time 0.1 \
    --output results/sweep_+5dBm.csv
```

### Dual Power Measurement (for calibration)

```bash
python scripts/lo_power_sweep.py \
    --arduino /dev/cu.usbserial-14110 \
    --tinysa auto \
    --dual-power +5 -4 \
    --output-dir results/
```

## Output Format

### CSV Format
```csv
frequency_mhz,power_dbm,timestamp,lo_power_setting
900.0,-12.34,2025-10-26T10:30:45.123,+5
900.2,-12.28,2025-10-26T10:30:45.234,+5
...
```

### FITS Format (optional)
Binary table with columns:
- `FREQUENCY`: Frequency in MHz
- `POWER`: Measured power in dBm
- `TIMESTAMP`: ISO 8601 timestamp
- `LO_SETTING`: LO output power setting

## Project Structure

```
tinysa-lo-characterization/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── lo_power_sweep.py           # Main measurement script
├── arduino_controller.py       # Arduino serial interface
├── tinysa_controller.py        # tinySA measurement interface
├── config.yaml                 # Default configuration
└── results/                    # Output directory (created automatically)
```

## Configuration File

Create `config.yaml` to store default settings:

```yaml
# Serial Ports
arduino_port: /dev/cu.usbserial-14110
tinysa_port: auto  # or specific port

# Frequency Sweep
freq_start: 900.0   # MHz
freq_stop: 960.0    # MHz
freq_step: 0.2      # MHz

# LO Settings
lo_power: +5        # dBm

# Timing
settling_time: 0.1  # seconds (wait after frequency change)
measurement_time: 0.05  # seconds per tinySA measurement

# tinySA Settings
span: 1.0           # MHz (measurement span around target frequency)
rbw: auto           # Resolution bandwidth
```

## Troubleshooting

### Arduino not found
```bash
ls /dev/cu.* | grep usb
```

### tinySA not found
```bash
python -c "from tsapython import tinySA; tsa = tinySA(); tsa.autoconnect()"
```

### Frequency mismatch
Ensure your Arduino is running `ManualControl.ino` and responding to serial commands. Test with:
```bash
python -c "import serial; s = serial.Serial('/dev/cu.usbserial-14110', 115200); s.write(b's\\n'); print(s.readline())"
```

## References

- [tinySA Ultra Documentation](https://tinysa.org/wiki/)
- [tsapython GitHub](https://github.com/LC-Linkous/tinySA_python)
- [ADF4351 Controller](../adf4351-controller/)

## License

MIT License
