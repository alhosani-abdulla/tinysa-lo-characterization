# tinySA-LO Characterization

Automated power measurement system for characterizing ADF4351-based Local Oscillator output power using tinySA Ultra spectrum analyzer.

**Quick Start:** `python scripts/test_lo_sweep.py` to verify hardware, then `python scripts/lo_power_sweep.py` for measurements.

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

Automates LO power measurements at 301 frequency points (900-960 MHz, 0.2 MHz steps) by coordinating:
- **Arduino/ADF4351**: Generates RF at commanded frequency
- **tinySA Ultra**: Measures peak power
- **Python Controller**: Orchestrates measurements and saves data

## Installation

**Requirements:** Python 3.10+ (3.11 recommended)

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/tinysa-lo-characterization.git
cd tinysa-lo-characterization

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

**Arduino Setup:**
1. Upload `ManualControl.ino` from [adf4351-controller](https://github.com/alhosani-abdulla/adf4351-controller) to your Arduino
2. Verify with Serial Monitor (115200 baud) - try commands: `s`, `f 900`, `p 5`

## Hardware Setup

```
┌─────────────┐      USB       ┌──────────────┐
│   Arduino   │◄──────────────►│              │
│  + ADF4351  │                │   Computer   │
│     (LO)    │                │  (Python)    │
└──────┬──────┘                │              │
       │ RF Cable               │              │
       ▼                   USB │              │
┌─────────────┐◄───────────────┤              │
│ tinySA Ultra│                └──────────────┘
└─────────────┘
```

**Connections:**
1. Arduino to Computer: USB serial (frequency commands)
2. tinySA to Computer: USB serial (power measurements)  
3. LO to tinySA: RF cable from ADF4351 output to tinySA input

## Quick Start

### 1. Test System Connectivity
```bash
python scripts/test_system.py
```
Verifies Arduino and tinySA are connected and responding.

### 2. Visual Sweep Test (No Measurements)
```bash
python scripts/test_lo_sweep.py --dwell 1.0
```
Sweeps LO through frequencies - watch signal on spectrum analyzer to verify hardware.

### 3. Run Automated Measurement
```bash
python scripts/lo_power_sweep.py
```
Measures power at all 301 frequencies and saves to CSV.

## Usage Examples

### Basic Measurement
```bash
# Uses config.yaml defaults
python scripts/lo_power_sweep.py
```

### Custom Parameters

```bash
python scripts/lo_power_sweep.py \
    --arduino /dev/cu.usbserial-14110 \
    --tinysa /dev/cu.usbserial-23456 \
    --freq-start 900.0 \
    --freq-stop 960.0 \
    --freq-step 0.2 \
    --power +5 \
    --settling-time 0.1 \
```bash
# Specify ports and custom range
python scripts/lo_power_sweep.py \
    --arduino /dev/cu.usbserial-14110 \
    --tinysa auto \
    --freq-start 920 \
    --freq-stop 940 \
    --freq-step 0.5 \
    --power +5 \
    --output results/sweep_920-940.csv
```

### Dual Power Calibration
```bash
# Measure at two power levels
python scripts/lo_power_sweep.py --dual-power +5 -10
```
Creates two files: `results/lo_power_sweep_TIMESTAMP_+5dBm.csv` and `..._-10dBm.csv`

### Plotting Results
```bash
python utils/plot_results.py results/sweep_+5dBm.csv
```

## Configuration

Edit `config.yaml` for default settings:

```yaml
arduino_port: /dev/cu.usbserial-14110
tinysa_port: auto
freq_start: 900.0   # MHz
freq_stop: 960.0    # MHz  
freq_step: 0.2      # MHz
lo_power: +5        # dBm
settling_time: 0.1  # seconds
```

## Output Format

CSV with columns: `frequency_mhz`, `power_dbm`, `timestamp`, `lo_power_setting`

```csv
frequency_mhz,power_dbm,timestamp,lo_power_setting
900.0,-12.34,2025-10-26T10:30:45,+5
900.2,-12.28,2025-10-26T10:30:46,+5
...
```

## Troubleshooting

**Arduino not found:**
```bash
ls /dev/cu.* | grep usb
# Then specify: --arduino /dev/cu.usbserial-XXXXX
```

**tinySA not connecting:**
```bash
pip install --upgrade tsapython
python -c "from tsapython import tinySA; t=tinySA(); t.autoconnect(); print('OK')"
```

**Port busy error:**
Close Arduino IDE Serial Monitor and other programs using the port.

**Low/inconsistent readings:**
- Check RF cable connections
- Increase `--settling-time` (default 0.1s) to let LO stabilize
- Verify tinySA input attenuation settings

## Arduino Commands

The ManualControl.ino sketch accepts:
- `f <freq>` - Set frequency in MHz (e.g., `f 925.5`)
- `p <power>` - Set power in dBm (e.g., `p +5` or `p -10`)  
- `s` - Print current status

## Project Details

**Measurement specs:**
- Default range: 900-960 MHz (301 points, 0.2 MHz steps)
- Configurable frequency range, step size, and power levels
- Automatic port detection for Arduino and tinySA
- Progress tracking and error handling

**Output:**
- CSV files with timestamp
- Optional FITS format (requires astropy)
- Automatic results/ directory creation

**Use cases:**
- LO power calibration for radio astronomy receivers
- Filter bank characterization
- Component testing and validation

## References

- [tinySA Ultra](https://tinysa.org/wiki/)
- [tsapython Library](https://github.com/LC-Linkous/tinySA_python)
- [ADF4351 Controller](https://github.com/alhosani-abdulla/adf4351-controller)

## License

MIT
