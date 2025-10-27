# tinySA-LO Power Characterization - Project Summary

## What This Does

This project automates the measurement of your ADF4351 Local Oscillator's output power across your 301-point frequency sweep (900-960 MHz, 0.2 MHz steps) using a tinySA Ultra spectrum analyzer.

## Why This Is Useful

1. **Quality Control**: Verify your LO is producing the expected power levels
2. **Calibration Data**: Characterize frequency-dependent power variations
3. **Dual Power Verification**: Compare +5 dBm and -4 dBm settings (like your filterbank setup)
4. **Automation**: No manual measurements needed - set it and walk away!

## Project Structure

```
tinysa-lo-characterization/
├── README.md                    # Full documentation
├── QUICKSTART.md               # Quick start guide
├── requirements.txt            # Python dependencies
├── config.yaml                 # Default configuration
│
├── arduino_controller.py       # Arduino/LO serial interface
├── tinysa_controller.py        # tinySA measurement interface
├── lo_power_sweep.py          # Main measurement script ⭐
├── test_system.py             # Hardware test script
├── plot_results.py            # Visualization utility
│
├── results/                    # Output directory
│   └── .gitkeep
└── .gitignore
```

## Quick Start (3 Steps!)

### 1. Install Dependencies
```bash
cd /Users/majhool/Projects/highz/tinysa-lo-characterization
pip install -r requirements.txt
```

### 2. Test Your Hardware
```bash
python test_system.py
```

This will automatically find your Arduino and tinySA, then test that both are responding correctly.

### 3. Run a Measurement
```bash
# Basic sweep (uses config.yaml)
python lo_power_sweep.py

# Or specify everything explicitly:
python lo_power_sweep.py \
    --arduino /dev/cu.usbserial-14110 \
    --tinysa auto \
    --freq-start 900 \
    --freq-stop 960 \
    --freq-step 0.2 \
    --power +5
```

## Hardware Setup

```
┌─────────────┐      USB       ┌──────────────┐
│   Arduino   │◄──────────────►│              │
│  + ADF4351  │                │   Computer   │
│     (LO)    │                │  (Python)    │
└──────┬──────┘                │              │
       │ RF Cable               │              │
       │                        │              │
       ▼                   USB  │              │
┌─────────────┐◄───────────────┤              │
│ tinySA Ultra│                 └──────────────┘
│  (Spectrum  │
│  Analyzer)  │
└─────────────┘
```

**Requirements:**
1. Arduino running `ManualControl.ino` (from your adf4351-controller repo)
2. tinySA Ultra spectrum analyzer
3. RF cable connecting LO output to tinySA input
4. Two USB connections to computer

## Key Features

### Automated Sweep
- Sends frequency command to Arduino via serial
- Waits for settling time
- Measures peak power with tinySA
- Stores result with timestamp
- Repeats for all 301 frequencies
- Takes ~2-3 minutes for full sweep

### Dual Power Mode
Perfect for calibration like your filterbank setup:
```bash
python lo_power_sweep.py --dual-power +5 -4
```
Produces two files:
- `results/lo_power_sweep_TIMESTAMP_+5dBm.csv`
- `results/lo_power_sweep_TIMESTAMP_-4dBm.csv`

### Visualization
```bash
# Plot single sweep
python plot_results.py results/sweep_+5dBm.csv

# Compare two power levels
python plot_results.py --compare \
    results/sweep_+5dBm.csv \
    results/sweep_-4dBm.csv

# Shows power difference and statistics
```

## Configuration

Edit `config.yaml` for your defaults:

```yaml
# Hardware
arduino_port: /dev/cu.usbserial-14110
tinysa_port: auto

# Sweep parameters (matches your filter band!)
freq_start: 900.0
freq_stop: 960.0
freq_step: 0.2

# LO settings
lo_power: +5

# Timing
settling_time: 0.1  # Adjust if needed

# tinySA settings
span: 1.0      # MHz around each frequency
averaging: 4   # 1, 4, or 16
```

## Output Format

CSV with columns:
```csv
timestamp,frequency_mhz,power_dbm,lo_power_setting
2025-10-26T10:30:45.123,900.0,-12.34,+5
2025-10-26T10:30:45.234,900.2,-12.28,+5
...
```

## How It Works

### Arduino Controller (`arduino_controller.py`)
- Connects via serial (115200 baud)
- Sends commands: `f <freq>` to set frequency, `p <power>` to set power
- Parses responses to track current state
- Compatible with your existing `ManualControl.ino` sketch

### tinySA Controller (`tinysa_controller.py`)
- Uses the `tsapython` library (PyPI package!)
- Configures tinySA for spectrum analyzer mode
- Performs `hop` measurements (frequency + power)
- Finds peak power in span around target frequency
- Supports averaging for better accuracy

### Main Script (`lo_power_sweep.py`)
- Coordinates both devices
- Implements measurement sequence:
  1. Set Arduino frequency
  2. Wait for settling
  3. Measure with tinySA
  4. Store result
  5. Repeat
- Progress display with ETA
- Error handling and recovery
- CSV output with statistics

## Comparison to Your Filterbank Setup

Your `filterSweep.c` uses GPIO to control the Arduino and AD HATs to measure received power. This project is similar but for **characterizing the LO itself**:

| Feature | filterSweep.c | This Project |
|---------|---------------|--------------|
| **Purpose** | Measure filterbank response | Characterize LO output |
| **Control** | GPIO pulses | Serial commands |
| **Measurement** | AD HAT (ADC) | tinySA (Spectrum Analyzer) |
| **What's Measured** | Signal through filter | LO power directly |
| **Dual Power** | ✓ (+5, -4 dBm) | ✓ (+5, -4 dBm) |
| **Frequency Range** | 900-960 MHz | 900-960 MHz |
| **Points** | 301 | 301 |

## Use Cases

1. **Pre-Deployment Check**: Verify LO works before installing in filterbank
2. **Troubleshooting**: Is the LO producing correct power?
3. **Frequency Response**: Check for any power variation across band
4. **Power Switching**: Verify +5/-4 dBm modes work correctly
5. **Documentation**: Characterize your specific hardware unit

## Advanced Usage

### Custom Frequency List
```python
# Edit config or use --freq-start, --freq-stop, --freq-step
python lo_power_sweep.py \
    --freq-start 920 \
    --freq-stop 940 \
    --freq-step 0.1  # 201 points
```

### Different tinySA Settings
```python
python lo_power_sweep.py \
    --span 2.0 \          # Wider measurement span
    --averaging 16 \      # More averaging for low signals
    --attenuation 0 \     # Max sensitivity
    --rbw 10              # 10 kHz RBW
```

### Batch Measurements
```bash
# Create a script for multiple characterizations
for power in +5 +2 -1 -4; do
    python lo_power_sweep.py \
        --power $power \
        --output results/sweep_${power}dBm.csv
    sleep 5  # Cool down between sweeps
done
```

## Troubleshooting

### Arduino Not Found
```bash
# List ports
python lo_power_sweep.py --list-ports

# Or manually:
ls /dev/cu.* | grep usb
```

### tinySA Issues
```bash
# Test connection
python -c "from tsapython import tinySA; tsa=tinySA(); tsa.autoconnect(); print('OK')"

# Update library
pip install --upgrade tsapython
```

### Low/No Power Readings
- Check RF cable connection
- Verify LO is actually powered on
- Try lower attenuation: `--attenuation 0`
- Check tinySA input is in correct mode

### Timing Issues
- Increase settling time: `--settling-time 0.2`
- Check Arduino serial monitor for errors
- Verify Arduino isn't resetting

## Future Enhancements

Possible additions:
1. **Real-time plotting** during measurement
2. **FITS format output** (optional dependency already in requirements)
3. **Multi-band support** (Band A + Band B in one run)
4. **Phase noise measurements** (if tinySA supports)
5. **Automated report generation** with plots

## Links

- **tinySA Python Library**: https://github.com/LC-Linkous/tinySA_python
- **tinySA Wiki**: https://tinysa.org/wiki/
- **Your ADF4351 Controller**: `../adf4351-controller/`
- **Your Filterbank Code**: `../highz-filterbank/`

## License

MIT License (same as your other projects)

---

**Questions?** Run `python lo_power_sweep.py --help` or check `QUICKSTART.md` for step-by-step instructions!
